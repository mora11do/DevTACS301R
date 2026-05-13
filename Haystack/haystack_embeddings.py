"""Haystack embeddings comparison script.

Install add-ons first if needed:
    pip install haystack-ai openai

Run:
    python Haystack/haystack_embeddings.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from haystack import Pipeline
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils import Secret

from haystack_utils import (
    DEFAULT_DOCS_DIR,
    DEFAULT_QUESTION,
    ensure_openai_key,
    load_chunk_documents,
    print_sources,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Haystack embedding test over local PDFs.")
    parser.add_argument("--docs-dir", default=str(DEFAULT_DOCS_DIR))
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--split-length", type=int, default=200)
    parser.add_argument("--split-overlap", type=int, default=40)
    parser.add_argument("--llm-model", default="gpt-4o-mini")
    parser.add_argument("--embedding-model", default="text-embedding-3-small")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    docs_dir = Path(args.docs_dir).expanduser().resolve()

    ensure_openai_key()
    print(f"Documents: {docs_dir}")
    print(f"Question: {args.question}")
    print("Mode: fresh embedding build")

    documents = load_chunk_documents(
        docs_dir=docs_dir,
        split_length=args.split_length,
        split_overlap=args.split_overlap,
    )
    print(f"Chunks: {len(documents)}")
    print("Embedding chunks with OpenAI...")

    embedder = OpenAIDocumentEmbedder(
        api_key=Secret.from_env_var("OPENAI_API_KEY"),
        model=args.embedding_model,
    )
    embedded_documents = embedder.run(documents=documents)["documents"]

    document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")
    document_store.write_documents(embedded_documents)

    prompt_template = [
        ChatMessage.from_system("You are a helpful assistant."),
        ChatMessage.from_user(
            "Given these documents, answer the question.\n"
            "Documents:\n{% for doc in documents %}{{ doc.content }}\n{% endfor %}\n"
            "Question: {{question}}\n"
            "Answer:"
        ),
    ]

    prompt_builder = ChatPromptBuilder(
        template=prompt_template,
        required_variables={"question", "documents"},
    )
    query_embedder = OpenAITextEmbedder(
        api_key=Secret.from_env_var("OPENAI_API_KEY"),
        model=args.embedding_model,
    )
    retriever = InMemoryEmbeddingRetriever(document_store=document_store)
    llm = OpenAIChatGenerator(model=args.llm_model, api_key=Secret.from_env_var("OPENAI_API_KEY"))

    rag_pipeline = Pipeline()
    rag_pipeline.add_component("query_embedder", query_embedder)
    rag_pipeline.add_component("retriever", retriever)
    rag_pipeline.add_component("prompt_builder", prompt_builder)
    rag_pipeline.add_component("llm", llm)
    rag_pipeline.connect("query_embedder.embedding", "retriever.query_embedding")
    rag_pipeline.connect("retriever", "prompt_builder.documents")
    rag_pipeline.connect("prompt_builder", "llm.messages")

    results = rag_pipeline.run(
        {
            "query_embedder": {"text": args.question},
            "retriever": {"top_k": args.top_k},
            "prompt_builder": {"question": args.question},
        },
        include_outputs_from={"retriever"},
    )

    replies = results["llm"]["replies"]
    retrieved_documents = results["retriever"]["documents"]

    print("\nAnswer:")
    for reply in replies:
        print(reply.text)
    print_sources(retrieved_documents, args.top_k)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from exc
