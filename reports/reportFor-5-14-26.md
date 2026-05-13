# Haystack vs Llamaindex

## Haystack
Codex was able to pretty quickly write some code to utilize BM25 stuff to look through a pdf.
30 seconds or so to do it (there was no database to draw from) when looking at one long pdf.
Same time for using embeddings.
Has a function to put in a link and it will use that link as data (convenient).
NO BUILT-IN persistent storage (would still need Chroma).

## Llamaindex
Couldn't really get it to work well.
BM25 "worked" but the answer was wrong.
Embeddings never finished loading ever.
Supposedly has built-in basic persistent storage, but never actually got it working.

# HAYSTACK WINS