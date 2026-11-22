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

## Required review and remaining gaps

- [ ] Configure and identify a real authorized local/remote LLM, confirm its data handling, then rerun generation/extraction demos and model-backed evaluations. Do not share real/employer documents.
- [ ] Review model answers/extractions and compare against independent labels; current model-quality scores are blocked, not zero or passed.
- [ ] Record a real short demo video if the invitation email requires a file. The assessment PDF accepts a short video or live demonstration; a live localhost run is documented, but no video is included.
- [ ] Recheck the final audit after model evaluation and decide what materials to include in the email/repository.
- [ ] Review confidentiality and repository visibility/audience before any remote sharing. No submission has been sent.

## Factual limits

The project currently has no real LLM-backed answer or invoice-extraction result. The local embedding/retrieval pipeline did run. The live extraction demonstration shows a 503 for missing model configuration and a 415 for unsupported TXT input. The RAG answer path also returns 503 until a model is configured. Do not describe these as successful model demonstrations.
