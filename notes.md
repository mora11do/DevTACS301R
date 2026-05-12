It seems like Llamaindex might be easier because you don't have to install other things, like Chroma,
supposedly, for it to work. The students would be able to get a nice working example faster.

I have only actually messed with Haystack so far though. I was able to get it to a point where
I can add a pdf into a folder and when I run the python code, it accurately told me about
the coca leaf sign about Kolata joining the pilgrimage. So I can just add a pdf to the folder
and the code will search through the pdf. Very useful. However, it has to re chunk and make
everything from scratch every time (because I'm not using Chroma or anything rn). Also, supposedly,
it's not even using embeddings in this example. It's using 

ALSO I learned about BM25 vs embeddings, so apparently, when using BM25, it doesn't store
the MEANINGS of words necessarily, just looks at the words themselves (similar to Google docs
ctrl+f, sort of). And it is still using RAG through that.
But you can also using embeddings to instead store the actual MEANING of a word, not the word itself.
So BM25 is good at retrieval when exact words are used and embeddings are nice when the meanings line up,
but not necessarily the exact wording.

TO DO:
- Maybe mess around a little more with Haystack, try out embeddings, try getting data from a website
instead of just pdf.
- PLAY WITH LLAMAINDEX. Especially, get the "on disk" storage working, or whatever it's called,
just get the Chroma functionality without actually using Chroma.