# Evidence and completion status

| Requirement/deliverable | Status | Evidence or gap |
|---|---|---|
| Requirements mapped from original assessment | PASS | `outputs/requirements_matrix.md`; full 13-page PDF read locally |
| Problem 1 separate runnable Python API | PASS | `rag_app/`; FastAPI routes and local FAISS retrieval |
| Multiple PDF/TXT ingestion, preprocessing, chunks, embeddings, vector database | PASS | `rag_app/loaders.py`, `chunking.py`, `embeddings.py`, `index.py`; local embedding smoke check succeeded |
| Problem 1 LLM grounded generation | PASS | gemini-3.5-flash-lite via OpenAI-compatible endpoint, 22 Nov 2026: all 15 labeled queries answered by the real model; `evaluation/rag/raw_results.json` answer_stage |
| Citations, follow-up state, abstention | PASS with one recorded miss | 12/12 answerable queries answered with allowlist citations; 2/3 expected-abstention queries abstained; R15 answered 'not provided' in text but did not set the abstain flag (recorded calibration miss, `evaluation/rag/answer_support_review.json`) |
| Problem 1 10+ retrieval queries and alternative comparison | PASS | 15 queries; MiniLM/FAISS versus BM25; `evaluation/rag/raw_results.json` |
| Problem 1 answer support/unavailable-answer quality | PASS | per-query support review of real model answers: 12 supported, 2 correct abstentions, 1 contract miss; `evaluation/rag/answer_support_review.json` |
| Problem 1 failure/edge tests | PASS | tests for bad uploads, scans/empty text, duplicates, citations; see test output below |
| Problem 5 FastAPI PDF upload, extraction, Pydantic schema | PASS | `extraction_app/`; real endpoint and PDF text parser implemented |
| Problem 5 real LLM extraction | PASS | gemini-3.5-flash-lite, 22 Nov 2026: all 10 synthetic invoices processed; `evaluation/extraction/raw_results.json` |
| Problem 5 10 representative documents, labels, layouts | PASS | 10 synthetic PDFs plus `samples/extraction/ground_truth.json` |
| Problem 5 model accuracy and sample outputs | PASS | schema validity 1.0, field exact-match 0.9571 (67/70), present-value accuracy 0.9848 (65/66); 3 residual per-field misses recorded in raw results |
| OCR boundary | PASS | OCR is not implemented; scan-only PDFs return an OCR-required error as documented |
| Common reasoning document and architecture diagrams | PASS | `docs/common_reasoning.md`, `docs/diagrams.md` |
| At least 3 design decisions per selected problem | PASS | separate decision logs |
| README/setup/OpenAPI documentation | PASS | root `README.md`; Swagger generated at each app `/docs` |
| AI tool disclosure | PASS | `docs/ai_disclosure.md` |
| Meaningful tests | PASS | actual command/result recorded below |
| Live demo | PASS | 22 Nov 2026 recorded demo with the real model: grounded answer with citation, correct abstention, real invoice extraction, explicit 415; see `docs/demo_run.md` |
| Short demo video | PASS | 55-second screen recording of the live APIs with the real model, 22 Nov 2026 (sent with the submission email) |
| Final complete setup tested from clean environment | PASS | separate `.verify-venv` created from `requirements.lock.txt`; `pip check` and all tests passed |
| Submission | PENDING | repository is public as originally created by the candidate; the submission email (repo link + recorded demo video) is prepared but not yet sent at the time of this update |

## Actual checks run

`.\.verify-venv\Scripts\python.exe -m pytest -q` returned **16 passed, 1 warning**. Warning: Starlette's TestClient reports an httpx compatibility deprecation; tests still passed. Retrieval metrics are recorded in the raw results.

22 Nov 2026 model-backed runs (model `gemini-3.5-flash-lite`, free Google AI Studio key, OpenAI-compatible endpoint, temperature 0, Linux Python 3.10):
- `python -m evaluation.extraction.run`: **COMPLETE**, schema validity 1.0, field exact-match 0.9571, expected present-value accuracy 0.9848. Transient provider errors occurred; bounded retries with backoff (counted per document, 5 total) cleared them. Residual misses: invoice_02 id prefix normalization, invoice_04 tax flagged incomplete instead of missing, invoice_05 ambiguous date resolved as found.
- `python -m evaluation.rag.run`: retrieval metrics unchanged (semantic hit@5 0.80, answerable 1.00); answer stage answered all 15 queries, 12/12 answerable with valid citations, 2/3 expected abstentions; one contract miss (R15) recorded in `answer_support_review.json`.
- `python -m pytest -q` re-run after evaluation-script changes: 16 passed.

## Immediate gaps

1. R15 abstention-flag calibration: the answer text correctly reports missing information but the model did not set `abstained`; tighten the abstention contract (prompt or output checking) before production use.
2. Inspect retrieval limits, add held-out labeled queries and gold chunk spans, and keep tuning the provisional 0.30 similarity threshold on labeled data only.
3. Known residual extraction misses (prefix normalization, incomplete-vs-missing boundary, ambiguous-date flagging) are recorded per field in `evaluation/extraction/raw_results.json`.
