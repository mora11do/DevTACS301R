"""Simple LlamaIndex RAG demo for quick classroom comparison.

Run:
    python LlamaIndex/llamaindexTesting.py --rebuild

Use --rebuild any time you change the source documents.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

BASE_DIR = Path(__file__).parent.resolve()
DEFAULT_DOCS_DIR = BASE_DIR / "documents"
FALLBACK_DOCS_DIR = BASE_DIR.parent / "Haystack" / "documents"
DEFAULT_STORAGE_DIR = BASE_DIR / "storage"
SUPPORTED_EXTENSIONS = [".pdf", ".md", ".txt"]
DEFAULT_QUESTION = (
    "Was the main character allowed to go on the pilgrimage, as shown by the coca leaves?"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Minimal LlamaIndex RAG demo for class comparison. "
            "It reads local documents, builds or reloads a persisted index, and answers one question."
        )
    )
    parser.add_argument(
        "--docs-dir",
        default=None,
        help=(
            "Directory containing documents. "
            "Defaults to LlamaIndex/documents, or falls back to Haystack/documents if present."
        ),
    )
    parser.add_argument(
        "--storage-dir",
        default=str(DEFAULT_STORAGE_DIR),
        help="Directory used to persist the LlamaIndex storage on disk.",
    )
    parser.add_argument(
        "--question",
        default=DEFAULT_QUESTION,
        help="Question to ask after loading the index.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="How many chunks to retrieve for the final answer.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=400,
        help="Chunk size used when splitting documents during indexing.",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=60,
        help="Chunk overlap used when splitting documents during indexing.",
    )
    parser.add_argument(
        "--llm-model",
        default="gpt-4o-mini",
        help="OpenAI chat model used to synthesize the final answer.",
    )
    parser.add_argument(
        "--embedding-model",
        default="text-embedding-3-small",
        help="OpenAI embedding model used for retrieval.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Ignore any stored index and rebuild it from the source documents.",
    )
    return parser.parse_args()


def resolve_docs_dir(docs_dir_arg: str | None) -> Path:
    if docs_dir_arg:
        return Path(docs_dir_arg).expanduser().resolve()
    if DEFAULT_DOCS_DIR.exists():
        return DEFAULT_DOCS_DIR
    if FALLBACK_DOCS_DIR.exists():
        return FALLBACK_DOCS_DIR
    return DEFAULT_DOCS_DIR


def configure_settings(
    llm_model: str,
    embedding_model: str,
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY is not set.")

    Settings.llm = OpenAI(model=llm_model, temperature=0)
    Settings.embed_model = OpenAIEmbedding(model=embedding_model)
    Settings.text_splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


def load_documents(docs_dir: Path):
    if not docs_dir.exists():
        raise FileNotFoundError(f"Documents folder not found: {docs_dir}")

    documents = SimpleDirectoryReader(
        input_dir=str(docs_dir),
        recursive=True,
        required_exts=SUPPORTED_EXTENSIONS,
    ).load_data()

    if not documents:
        extensions = ", ".join(SUPPORTED_EXTENSIONS)
        raise ValueError(f"No supported documents found in {docs_dir}. Expected: {extensions}")

    return documents


def load_or_build_index(
    docs_dir: Path,
    storage_dir: Path,
    rebuild: bool,
) -> tuple[VectorStoreIndex, str]:
    if storage_dir.exists() and any(storage_dir.iterdir()) and not rebuild:
        storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
        return load_index_from_storage(storage_context), "loaded existing index"

    documents = load_documents(docs_dir)
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    storage_dir.mkdir(parents=True, exist_ok=True)
    index.storage_context.persist(persist_dir=str(storage_dir))
    return index, "built new index"


def print_sources(response, top_k: int) -> None:
    source_nodes = getattr(response, "source_nodes", None) or []
    if not source_nodes:
        return

    print("\nTop sources:")
    for index, source in enumerate(source_nodes[:top_k], start=1):
        metadata = getattr(source.node, "metadata", {}) or {}
        file_path = metadata.get("file_path") or metadata.get("filename") or "unknown"
        page_label = metadata.get("page_label")
        score = getattr(source, "score", None)

        page_text = f", page={page_label}" if page_label else ""
        score_text = f", score={score:.3f}" if isinstance(score, (int, float)) else ""
        print(f"{index}. {file_path}{page_text}{score_text}")


def main() -> None:
    args = parse_args()
    docs_dir = resolve_docs_dir(args.docs_dir)
    storage_dir = Path(args.storage_dir).expanduser().resolve()

    configure_settings(
        llm_model=args.llm_model,
        embedding_model=args.embedding_model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    print(f"Documents: {docs_dir}")
    print(f"Storage:   {storage_dir}")
    print(f"Question:  {args.question}")

    index, status = load_or_build_index(
        docs_dir=docs_dir,
        storage_dir=storage_dir,
        rebuild=args.rebuild,
    )
    print(f"Index:     {status}")

    query_engine = index.as_query_engine(similarity_top_k=args.top_k)
    response = query_engine.query(args.question)

    print("\nAnswer:")
    print(response)
    print_sources(response, args.top_k)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from exc
