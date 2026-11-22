# Evidence and completion status

| Requirement/deliverable | Status | Evidence or gap |
|---|---|---|
| Requirements mapped from original assessment | PASS | `outputs/requirements_matrix.md`; full 13-page PDF read locally |
| Problem 1 separate runnable Python API | PASS | `rag_app/`; FastAPI routes and local FAISS retrieval |
| Multiple PDF/TXT ingestion, preprocessing, chunks, embeddings, vector database | PASS | `rag_app/loaders.py`, `chunking.py`, `embeddings.py`, `index.py`; local embedding smoke check succeeded |
| Problem 1 LLM grounded generation | BLOCKED | API integration exists; no authorized local/remote LLM endpoint configured |
| Citations, follow-up state, abstention | BLOCKED | response contract, citation allowlist, session logic exist; model-backed behavior not run |
| Problem 1 10+ retrieval queries and alternative comparison | PASS | 15 queries; MiniLM/FAISS versus BM25; `evaluation/rag/raw_results.json` |
| Problem 1 answer support/unavailable-answer quality | BLOCKED | no LLM output to review; retrieval-only results are not answer-quality evidence |
| Problem 1 failure/edge tests | PASS | tests for bad uploads, scans/empty text, duplicates, citations; see test output below |
| Problem 5 FastAPI PDF upload, extraction, Pydantic schema | PASS | `extraction_app/`; real endpoint and PDF text parser implemented |
| Problem 5 real LLM extraction | BLOCKED | no authorized model endpoint configured |
| Problem 5 10 representative documents, labels, layouts | PASS | 10 synthetic PDFs plus `samples/extraction/ground_truth.json` |
| Problem 5 model accuracy and sample outputs | BLOCKED | real extraction outputs unavailable; no scores fabricated |
| OCR boundary | PASS | OCR is not implemented; scan-only PDFs return an OCR-required error as documented |
| Common reasoning document and architecture diagrams | PASS | `docs/common_reasoning.md`, `docs/diagrams.md` |
| At least 3 design decisions per selected problem | PASS | separate decision logs |
| README/setup/OpenAPI documentation | PASS | root `README.md`; Swagger generated at each app `/docs` |
| AI tool disclosure | PASS | `docs/ai_disclosure.md` |
| Meaningful tests | PASS | actual command/result recorded below |
| Live demo | PASS | both APIs started over localhost; upload, citation retrieval, HTTP errors, health and OpenAPI routes exercised; see `docs/demo_run.md` |
| Short demo video | NOT RUN | Screen-capture package download stalled; no video is claimed |
| Final complete setup tested from clean environment | PASS | separate `.verify-venv` created from `requirements.lock.txt`; `pip check` and all tests passed |
| Submission/public sharing | NOT RUN | not performed; the user asked to keep the material private |

## Actual checks run

`.\.verify-venv\Scripts\python.exe -m pytest -q` returned **16 passed, 1 warning**. Warning: Starlette's TestClient reports an httpx compatibility deprecation; tests still passed. Retrieval metrics are recorded in the raw results. Extraction evaluation returned `BLOCKED` (no endpoint), not passed.

## Immediate gaps

1. Configure an authorized local or remote OpenAI-compatible LLM endpoint and record its model/version and data handling; rerun both model-backed evaluations.
2. Inspect retrieval limits, add held-out labeled queries and gold chunk spans, and review generated answer support.
3. Record a real short walkthrough video using only synthetic samples if the email specifically requests a video file.
