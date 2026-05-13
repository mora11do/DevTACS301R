"""LlamaIndex BM25 comparison script.

Install first:
    pip install llama-index llama-index-llms-openai llama-index-retrievers-bm25

Run:
    python LlamaIndex/llamaindex_bm25.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.retrievers.bm25 import BM25Retriever

from llamaindex_utils import (
    DEFAULT_DOCS_DIR,
    DEFAULT_QUESTION,
    build_splitter,
    configure_llm,
    load_documents,
    print_sources,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LlamaIndex BM25 test over local documents.")
    parser.add_argument("--docs-dir", default=str(DEFAULT_DOCS_DIR))
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--chunk-size", type=int, default=400)
    parser.add_argument("--chunk-overlap", type=int, default=60)
    parser.add_argument("--llm-model", default="gpt-4o-mini")
    return parser.parse_args()


def build_retriever(
    docs_dir: Path,
    top_k: int,
    chunk_size: int,
    chunk_overlap: int,
):
    documents = load_documents(docs_dir)
    print(f"Documents loaded: {len(documents)}")
    splitter = build_splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"Nodes built: {len(nodes)}")
    print("Building BM25 index...")
    return BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=top_k)


def main() -> None:
    args = parse_args()
    docs_dir = Path(args.docs_dir).expanduser().resolve()

    configure_llm(args.llm_model)

    print(f"Documents: {docs_dir}")
    print(f"Question:  {args.question}")
    print("Mode: fresh BM25 build")

    retriever = build_retriever(
        docs_dir=docs_dir,
        top_k=args.top_k,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    query_engine = RetrieverQueryEngine.from_args(retriever=retriever)
    response = query_engine.query(args.question)

    print("\nAnswer:")
    print(response)
    print_sources(response, args.top_k)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from exc
