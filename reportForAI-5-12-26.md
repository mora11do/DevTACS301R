# reportForAI-5-12-26

## Session Summary
- Set up a Haystack-based RAG prototype and focused on learning how Haystack works.
- Created a folder structure:
  - `Haystack\` (project folder)
  - `Haystack\documents\` (drop PDFs here for retrieval)
- Moved script to `Haystack\haystackTesting.py`.

## Current Script Behavior
- Converts PDFs in `Haystack\documents\` to text.
- Splits documents into chunks (`split_by="word"`, `split_length=200`, `split_overlap=40`).
- Uses **BM25 keyword retrieval** (not embeddings).
- Sends retrieved chunks to OpenAI Chat Generator for answers.
- Question is currently hard-coded in the script.
- Added a local cache file `Haystack\index_cache.json` so PDF conversion + chunking only happens for new/changed PDFs.

## Key Concepts Discussed
- **BM25** is keyword-based retrieval (word overlap scoring), not embeddings.
- **Embeddings** are semantic vectors; better for meaning-based matches but less interpretable.
- BM25 can still work well if query terms appear in the text.
- Chunk size is controlled by `DocumentSplitter`, not by BM25.

## Persistence / Storage Notes
- Current setup uses **in-memory** document store, rebuilt each run from cached chunks.
- Discussed switching to **semantic embeddings** with a persistent vector store later.
- Chroma and Qdrant are both vector DBs (Document Stores in Haystack). Chroma is familiar from a prior class.

## LlamaIndex vs Haystack (persistence angle)
- Haystack: persistence depends on chosen Document Store (system-oriented, explicit backend choice).
- LlamaIndex: built-in `persist()` for disk save/load without extra DB (quick prototypes).

## User Preferences
- Wants clear explanations with simple vocab and definitions.
- Not ready to switch to embeddings yet but interested.
- Future interest: add webpage ingestion.

## Files Created/Updated
- `Haystack\haystackTesting.py` (PDF pipeline + cache + BM25)
- `Haystack\documents\` (PDF drop folder)
- `Haystack\index_cache.json` (auto-generated cache)
- `report-5-12-26.md` (brief comparison Haystack vs LlamaIndex for persistence)
- `AGENTS.md` (TA research context)

## Next Possible Steps
- Make the question interactive (CLI input) instead of hard-coded.
- Switch to semantic embeddings (Chroma or Qdrant) with persistence.
- Add webpage downloader → HTML → documents.