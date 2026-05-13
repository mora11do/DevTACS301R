"""LlamaIndex embedding script with built-in persisted storage.

Install first:
    pip install llama-index llama-index-llms-openai llama-index-embeddings-openai

Run first build:
    python LlamaIndex/llamaindex_embeddings_persisted.py

Run again to reuse the saved index:
    python LlamaIndex/llamaindex_embeddings_persisted.py

Force a rebuild:
    python LlamaIndex/llamaindex_embeddings_persisted.py --rebuild
"""

from __future__ import annotations

import argparse
from pathlib import Path

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage

from llamaindex_utils import (
    BASE_DIR,
    DEFAULT_DOCS_DIR,
    DEFAULT_QUESTION,
    configure_embeddings,
    load_documents,
    print_sources,
)

DEFAULT_STORAGE_DIR = BASE_DIR / "persisted_embedding_storage"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LlamaIndex embedding test with built-in persisted local storage."
    )
    parser.add_argument("--docs-dir", default=str(DEFAULT_DOCS_DIR))
    parser.add_argument("--storage-dir", default=str(DEFAULT_STORAGE_DIR))
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--chunk-size", type=int, default=400)
    parser.add_argument("--chunk-overlap", type=int, default=60)
    parser.add_argument("--llm-model", default="gpt-4o-mini")
    parser.add_argument("--embedding-model", default="text-embedding-3-small")
    parser.add_argument("--rebuild", action="store_true")
    return parser.parse_args()


def load_or_build_index(docs_dir: Path, storage_dir: Path, rebuild: bool):
    if storage_dir.exists() and any(storage_dir.iterdir()) and not rebuild:
        print("Mode: loading persisted embedding index")
        storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
        return load_index_from_storage(storage_context), "loaded existing storage"

    print("Mode: building embedding index and persisting to disk")
    documents = load_documents(docs_dir)
    print(f"Documents loaded: {len(documents)}")
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    storage_dir.mkdir(parents=True, exist_ok=True)
    index.storage_context.persist(persist_dir=str(storage_dir))
    return index, "built and persisted new storage"


def main() -> None:
    args = parse_args()
    docs_dir = Path(args.docs_dir).expanduser().resolve()
    storage_dir = Path(args.storage_dir).expanduser().resolve()

    configure_embeddings(
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
    print(f"Storage status: {status}")

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
