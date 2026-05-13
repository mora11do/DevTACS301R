# Haystack Cheat Sheet

Use these from the repo root with the course `.venv` selected in PyCharm or the terminal.

## `haystackTesting.py`
- Older PDF test script.
- Uses PDFs from `Haystack/documents`.
- Good if you want to look at the earlier experiment before the cleaner comparison files.
- No special tags built in.

## `haystack_bm25.py`
- Baseline Haystack PDF test using BM25.
- Reads PDFs from `Haystack/documents`.
- Good for quick keyword-style retrieval testing.
- Useful tags:
- `--docs-dir`
- `--question`
- `--top-k`
- `--split-length`
- `--split-overlap`
- `--llm-model`

## `haystack_embeddings.py`
- Baseline Haystack PDF test using embeddings.
- Reads PDFs from `Haystack/documents`.
- Good for semantic retrieval testing.
- Useful tags:
- `--docs-dir`
- `--question`
- `--top-k`
- `--split-length`
- `--split-overlap`
- `--llm-model`
- `--embedding-model`

## `haystack_url_bm25.py`
- Haystack URL test.
- Fetches content from a single link using Haystack components, converts the HTML into documents, splits it, then does BM25 retrieval.
- Good for testing whether Haystack can work directly from a webpage instead of a PDF.
- Useful tags:
- `--url`
- `--question`
- `--top-k`
- `--split-length`
- `--split-overlap`
- `--llm-model`

## `haystack_utils.py`
- Helper file used by the other Haystack scripts.
- Not meant to be run directly.

## Quick order to test
- `haystack_bm25.py`
- `haystack_embeddings.py`
- `haystack_url_bm25.py`

## Common requirements
- `OPENAI_API_KEY` must be set.
- URL mode may also need `trafilatura` installed.
