# Candidate review checklist before submission

The timing below comes from the invitation summary in the user's supplied prompt (reply to the assessment email within 2-3 days of receipt), not from a fixed cutoff in the assessment PDF. The PDF itself describes a 2-3 day assessment duration and requests source, documentation, evaluation, architecture, tests, disclosure, and a short demonstration.

## Prepared locally

- [x] Problem 1 and Problem 5 selected; Problems 2-4 excluded.
- [x] Requirements matrix against the original assessment PDF.
- [x] Two separate Python application packages and separate decision/evaluation documents.
- [x] RAG accepts multiple TXT/PDF files, uses local embeddings + FAISS, has `/search` with citations, and includes a grounded `/ask` path.
- [x] Extraction API accepts PDF, uses a Pydantic invoice schema and field evidence/statuses, and fails clearly when the LLM is not configured.
- [x] Synthetic RAG samples, 15 labeled retrieval queries, ten varied synthetic invoice PDFs, independent ground-truth labels, and one expected schema-shaped JSON example.
- [x] Retrieval comparison against BM25 with raw per-query results.
- [x] Common GenAI reliability analysis, three Mermaid diagrams, setup documentation, decision logs, limitations, and AI disclosure.
- [x] 16 tests passed in a clean virtual environment; live localhost routes were exercised and logged.
- [x] No employer PDF copy, public repository, repository invite, email, or submission was created.

## Completed 22 Nov 2026

- [x] Real authorized LLM configured: gemini-3.5-flash-lite via a free Google AI Studio key (OpenAI-compatible endpoint, temperature 0). Only synthetic sample documents are sent to the provider; no real/employer documents. Model-backed evaluations and demos rerun.
- [x] Model answers/extractions compared against independent labels; real scores recorded in `evaluation/rag/raw_results.json`, `evaluation/rag/answer_support_review.json`, and `evaluation/extraction/raw_results.json`.
- [x] Real short demo video recorded 22 Nov 2026 (55 s, live APIs with the real model; sent with the submission email).
- [x] Final audit rechecked after model evaluation; `docs/status_and_gaps.md` updated with real results and residual misses.
- [x] Confidentiality and repository visibility reviewed: the repository is public as originally created by the candidate; the confidential employer PDF and credentials are not in the repository and are gitignored.

## Factual limits

All reported metrics come from real recorded runs on 22 Nov 2026 with gemini-3.5-flash-lite. Residual issues are recorded honestly: one abstention-flag calibration miss (R15), three per-field extraction misses, and transient provider errors cleared by bounded retries. The 503 fail-closed behavior when no model is configured remains implemented and unit-tested.
