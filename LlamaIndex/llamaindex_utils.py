from __future__ import annotations

import os
from pathlib import Path

from llama_index.core import Settings, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

BASE_DIR = Path(__file__).parent.resolve()
DEFAULT_DOCS_DIR = BASE_DIR / "documents"
DEFAULT_QUESTION = (
    "Was the main character allowed to go on the pilgrimage, as shown by the coca leaves?"
)
SUPPORTED_EXTENSIONS = [".pdf", ".md", ".txt"]


def ensure_openai_key() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY is not set.")


def configure_llm(llm_model: str) -> None:
    ensure_openai_key()
    Settings.llm = OpenAI(model=llm_model, temperature=0)


def configure_embeddings(
    llm_model: str,
    embedding_model: str,
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    ensure_openai_key()
    Settings.llm = OpenAI(model=llm_model, temperature=0)
    Settings.embed_model = OpenAIEmbedding(model=embedding_model)
    Settings.text_splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


def build_splitter(chunk_size: int, chunk_overlap: int) -> SentenceSplitter:
    return SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def load_documents(docs_dir: Path):
    if not docs_dir.exists():
        raise FileNotFoundError(f"Documents folder not found: {docs_dir}")

    documents = SimpleDirectoryReader(
        input_dir=str(docs_dir),
        recursive=True,
        required_exts=SUPPORTED_EXTENSIONS,
    ).load_data()
    if not documents:
        raise ValueError(f"No supported documents found in {docs_dir}")
    return documents


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
