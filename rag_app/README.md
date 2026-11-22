# Problem 1: Document RAG

Run from the workspace root after following the root README setup:

```powershell
.\.venv\Scripts\python.exe -m uvicorn rag_app.api:app --reload --port 8001
```

Use `POST /documents` with one or more PDF/TXT files, `GET /search?q=...` to inspect retrieval and citations, and `POST /ask` with `{ "question": "...", "session_id": "optional-session" }` for a grounded answer. The app stores its FAISS index and chunk metadata under `rag_app/data/` and indexes locally. It returns 503 when an answer needs a model but no LLM endpoint is configured; it never invents a fallback answer.

The app uses paragraph-aware page-bounded chunks (900 character maximum, 120 character overlap), FastEmbed MiniLM vectors, FAISS exact inner-product ranking, and a provisional 0.30 similarity gate. Chunk IDs, document hashes, filename, page, and evidence text pass through to the citation response. Retrieval and BM25 comparison are separate from model answer-quality evaluation.

Run tests with `.\.venv\Scripts\python.exe -m pytest tests/test_rag.py -q` and retrieval evaluation with `.\.venv\Scripts\python.exe -m evaluation.rag.run`. The API docs are at `/docs`.
