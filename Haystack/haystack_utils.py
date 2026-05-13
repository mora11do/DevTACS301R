from __future__ import annotations

import os
from pathlib import Path

from haystack import Document
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentSplitter

BASE_DIR = Path(__file__).parent.resolve()
DEFAULT_DOCS_DIR = BASE_DIR / "documents"
DEFAULT_QUESTION = (
    "Was the main character allowed to go on the pilgrimage, as shown by the coca leaves?"
)


def ensure_openai_key() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY is not set.")


def load_chunk_documents(
    docs_dir: Path,
    split_length: int,
    split_overlap: int,
) -> list[Document]:
    if not docs_dir.exists():
        raise FileNotFoundError(f"Documents folder not found: {docs_dir}")

    pdf_paths = sorted(docs_dir.glob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found in: {docs_dir}")

    pdf_converter = PyPDFToDocument()
    splitter = DocumentSplitter(
        split_by="word",
        split_length=split_length,
        split_overlap=split_overlap,
    )

    source_documents = []
    for pdf_path in pdf_paths:
        converted = pdf_converter.run(sources=[str(pdf_path)])
        source_documents.extend(converted["documents"])

    split_docs = splitter.run(documents=source_documents)["documents"]
    return [
        Document(content=document.content, meta=document.meta or {})
        for document in split_docs
    ]


def print_sources(documents: list[Document], top_k: int) -> None:
    if not documents:
        return

    print("\nTop sources:")
    for index, document in enumerate(documents[:top_k], start=1):
        meta = document.meta or {}
        file_path = meta.get("file_path") or meta.get("source_id") or "unknown"
        page_number = meta.get("page_number")
        score = meta.get("score")

        page_text = f", page={page_number}" if page_number is not None else ""
        score_text = f", score={score:.3f}" if isinstance(score, (int, float)) else ""
        print(f"{index}. {file_path}{page_text}{score_text}")
