"""LlamaIndex embedding comparison script.

Install first:
    pip install llama-index llama-index-llms-openai llama-index-embeddings-openai

Run:
    python LlamaIndex/llamaindex_embeddings.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from llama_index.core import VectorStoreIndex

from llamaindex_utils import (
    DEFAULT_DOCS_DIR,
    DEFAULT_QUESTION,
    configure_embeddings,
    load_documents,
    print_sources,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LlamaIndex embedding test over local documents.")
    parser.add_argument("--docs-dir", default=str(DEFAULT_DOCS_DIR))
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--chunk-size", type=int, default=400)
    parser.add_argument("--chunk-overlap", type=int, default=60)
    parser.add_argument("--llm-model", default="gpt-4o-mini")
    parser.add_argument("--embedding-model", default="text-embedding-3-small")
    return parser.parse_args()


def build_index(docs_dir: Path):
    documents = load_documents(docs_dir)
    print(f"Documents loaded: {len(documents)}")
    print("Building embedding index...")
    return VectorStoreIndex.from_documents(documents, show_progress=True)


def main() -> None:
    args = parse_args()
    docs_dir = Path(args.docs_dir).expanduser().resolve()

    configure_embeddings(
        llm_model=args.llm_model,
        embedding_model=args.embedding_model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    print(f"Documents: {docs_dir}")
    print(f"Question:  {args.question}")
    print("Mode: fresh embedding build")

    index = build_index(docs_dir=docs_dir)

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
