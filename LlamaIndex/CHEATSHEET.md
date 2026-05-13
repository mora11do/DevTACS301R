# LlamaIndex Cheat Sheet

Use these from the repo root with the course `.venv` selected in PyCharm or the terminal.

## `llamaindexTesting.py`
- Older LlamaIndex PDF test script.
- Uses PDFs from `LlamaIndex/documents`.
- This was the earlier experiment before the cleaner comparison files.
- Useful tags:
- `--docs-dir`
- `--storage-dir`
- `--question`
- `--top-k`
- `--chunk-size`
- `--chunk-overlap`
- `--llm-model`
- `--embedding-model`
- `--rebuild`

## `llamaindex_bm25.py`
- Baseline LlamaIndex PDF test using BM25.
- Reads PDFs from `LlamaIndex/documents`.
- Builds fresh each run.
- Useful tags:
- `--docs-dir`
- `--question`
- `--top-k`
- `--chunk-size`
- `--chunk-overlap`
- `--llm-model`


## THIS NEVER FINISHED RUNNING
## `llamaindex_embeddings.py`
- Baseline LlamaIndex PDF test using embeddings.
- Reads PDFs from `LlamaIndex/documents`.
- Builds fresh each run.
- Useful tags:
- `--docs-dir`
- `--question`
- `--top-k`
- `--chunk-size`
- `--chunk-overlap`
- `--llm-model`
- `--embedding-model`

## BECAUSE THE LAST ONE NEVER FINISHED, THIS ONE IS UNTESTED
## `llamaindex_embeddings_persisted.py`
- LlamaIndex embedding test that saves the built index to disk and reuses it later.
- This is the file to use if you want to test LlamaIndex's built-in persistence idea.
- Saves to `LlamaIndex/persisted_embedding_storage` by default.
- Useful tags:
- `--docs-dir`
- `--storage-dir`
- `--question`
- `--top-k`
- `--chunk-size`
- `--chunk-overlap`
- `--llm-model`
- `--embedding-model`
- `--rebuild`

## `llamaindex_utils.py`
- Helper file used by the other LlamaIndex scripts.
- Not meant to be run directly.

## Quick order to test
- `llamaindex_bm25.py`
- `llamaindex_embeddings.py`
- `llamaindex_embeddings_persisted.py`

## Common requirements
- `OPENAI_API_KEY` must be set.
- BM25 may require the extra `llama-index-retrievers-bm25` package.
