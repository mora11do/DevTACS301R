import json
from pathlib import Path

from haystack import Pipeline, Document
from haystack.utils import Secret
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentSplitter

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "documents"
CACHE_PATH = BASE_DIR / "index_cache.json"

if not DOCS_DIR.exists():
    raise FileNotFoundError(f"Documents folder not found: {DOCS_DIR}")

pdf_paths = sorted(DOCS_DIR.glob("*.pdf"))
if not pdf_paths:
    raise FileNotFoundError(f"No PDF files found in: {DOCS_DIR}")

# Load or initialize cache
if CACHE_PATH.exists():
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {"files": {}}

pdf_converter = PyPDFToDocument()
splitter = DocumentSplitter(split_by="word", split_length=200, split_overlap=40)

def file_signature(path: Path) -> dict:
    stat = path.stat()
    return {"size": stat.st_size, "mtime": stat.st_mtime}

all_chunks = []
updated_cache = False
current_keys = {str(p.resolve()) for p in pdf_paths}

# Remove cache entries for PDFs no longer present
for cached_key in list(cache["files"].keys()):
    if cached_key not in current_keys:
        del cache["files"][cached_key]
        updated_cache = True

for pdf_path in pdf_paths:
    key = str(pdf_path.resolve())
    sig = file_signature(pdf_path)
    cached = cache["files"].get(key)

    if cached and cached.get("size") == sig["size"] and cached.get("mtime") == sig["mtime"]:
        chunks = cached["chunks"]
    else:
        # Convert and split this PDF
        converted = pdf_converter.run(sources=[str(pdf_path)])
        split_docs = splitter.run(documents=converted["documents"])
        chunks = [
            {"content": doc.content, "meta": doc.meta or {}}
            for doc in split_docs["documents"]
        ]
        cache["files"][key] = {**sig, "chunks": chunks}
        updated_cache = True

    all_chunks.extend(chunks)

if updated_cache:
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=True, indent=2)

# Write documents to an in-memory store (fast to load from cache)
document_store = InMemoryDocumentStore()
document_store.write_documents([
    Document(content=chunk["content"], meta=chunk.get("meta") or {})
    for chunk in all_chunks
])

# Build a RAG pipeline
prompt_template = [
    ChatMessage.from_system("You are a helpful assistant."),
    ChatMessage.from_user(
        "Given these documents, answer the question.\n"
        "Documents:\n{% for doc in documents %}{{ doc.content }}{% endfor %}\n"
        "Question: {{question}}\n"
        "Answer:"
    ),
]

# Define required variables explicitly
prompt_builder = ChatPromptBuilder(
    template=prompt_template,
    required_variables={"question", "documents"},
)

retriever = InMemoryBM25Retriever(document_store=document_store)
llm = OpenAIChatGenerator(api_key=Secret.from_env_var("OPENAI_API_KEY"))

rag_pipeline = Pipeline()
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", llm)
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm.messages")

# Ask a question
question = "Was the main character allowed to go on the pilgrimage, as shown by the coca leaves?."
results = rag_pipeline.run(
    {
        "retriever": {"query": question},
        "prompt_builder": {"question": question},
    }
)

print(results["llm"]["replies"])
