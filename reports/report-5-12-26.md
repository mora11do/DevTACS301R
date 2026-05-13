# RAG Persistence Notes (2026-05-12)

**Haystack (systems‑oriented, long‑term)**
- Persistence depends on the Document Store you choose (e.g., Chroma/Qdrant/etc.), so you explicitly pick the storage and deployment model.
- This forces students to think about real system components: storage backend, retriever compatibility, scaling, and deployment constraints.
- Better fit when teaching “systems thinking” and long‑term architecture decisions.

**LlamaIndex (fast path, quick example)**
- Built‑in persistence lets you save/load indexes to disk without an external vector database.
- This makes it easier to get a working demo quickly, with less setup.
- Better fit for quick prototypes or an introductory exercise where you want minimal friction.