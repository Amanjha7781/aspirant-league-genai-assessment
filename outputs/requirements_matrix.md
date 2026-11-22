# Assessment requirements and implementation map

This map is based on the full 13-page assessment PDF. The PDF defines the required capabilities and deliverables; names, sample domains, exact model settings, metrics and directory layout below are implementation choices unless marked **PDF requirement**.

## Problem 1: Intelligent Document Retrieval and Question Answering

| Assessment requirement | Planned code/evidence | Planned verification/deliverable | Source |
|---|---|---|---|
| Upload multiple PDF and TXT files | `rag_app/api.py`, ingestion pipeline | API upload walkthrough; upload tests | PDF requirement, p.2 |
| Extract/preprocess; semantic chunking | `rag_app/loaders.py`, `rag_app/chunking.py` | parser/chunker tests; decision log | PDF requirement, p.2 |
| Embeddings and vector database | `rag_app/embeddings.py`, `rag_app/index.py` | index/retrieval tests; setup docs | PDF requirement, p.2 |
| Retrieve relevant chunks and generate grounded answers | `rag_app/retrieval.py`, `rag_app/generation.py` | 10+ query evaluation; support review | PDF requirement, pp.2-3 |
| Citations, follow-up context, abstention | `rag_app/schemas.py`, `rag_app/service.py` | citation provenance, follow-up and unavailable cases | PDF requirement, p.2 |
| Modular Python app, structured responses, exceptions, API/UI | `rag_app/` | runnable app and README | PDF requirement, p.2 |
| Explain chunking/model/relevance/errors/hallucination/alternatives/conflicts | `docs/problem_1_decisions.md`, `docs/problem_1_evaluation.md` | review against checklist | PDF requirement, pp.2-3 |
| 10+ representative queries, answer support, abstention, 3+ edge cases | `evaluation/rag/` | reproducible evaluation and raw results | PDF requirement, p.3 |
| Improve retrieval; architecture diagram; sample docs/queries; decision log (3+) | `docs/`, `samples/rag/` | deliverable audit | PDF requirement, p.3 |

## Problem 5: Intelligent Document Understanding and Structured Data Extraction

| Assessment requirement | Planned code/evidence | Planned verification/deliverable | Source |
|---|---|---|---|
| Python + FastAPI upload API; PDF primary input | `extraction_app/api.py` | OpenAPI/Swagger and API walkthrough | PDF requirement, p.10 |
| PDF text extraction and LLM/document-understanding extraction | `extraction_app/pdf.py`, `extraction_app/extractor.py` | extraction tests and provider status | PDF requirement, p.10 |
| Predefined JSON schema validated with Pydantic | `extraction_app/schemas.py` | schema tests and example outputs | PDF requirement, p.10 |
| Identify missing/incomplete/ambiguous and distinguish not-found | `extraction_app/validation.py`, response schema | fixtures and field-level evaluation | PDF requirement, p.10 |
| Invalid/unsupported/oversized handling; status codes; failure logging | `extraction_app/api.py`, `extraction_app/logging_config.py` | negative API tests | PDF requirement, pp.10-11 |
| Separate extraction, validation and response generation | `extraction_app/` modules | architecture diagram | PDF requirement, p.10 |
| Explain document type/schema, ambiguity, invention prevention, layouts, OCR, accuracy, future types | `docs/problem_5_decisions.md` | review against checklist | PDF requirement, pp.10-11 |
| At least 10 samples; correct/missing/incorrect/layout and scanned if supported | `samples/extraction/`, `evaluation/extraction/` | independent ground truth and report | PDF requirement, p.11 |
| Accuracy report, API docs, diagrams, decision log (3+) | `docs/`, `evaluation/` | deliverable audit | PDF requirement, p.11 |

## Mandatory common reasoning challenge

| Assessment requirement | Planned evidence | Verification | Source |
|---|---|---|---|
| Analyze five observed failure modes and causes | `docs/common_reasoning.md` | checklist review | PDF requirement, p.12 |
| Investigation, fixes, validation and safe failure | `docs/common_reasoning.md` | checklist review | PDF requirement, p.12 |
| Proposed architecture/workflow diagram and trade-offs | `docs/common_reasoning.md`, `docs/diagrams/` | diagram renders/readability | PDF requirement, p.12 |
| Distinguish prompt, application logic, retrieval, model and other fixes | `docs/common_reasoning.md` | checklist review | PDF requirement, p.12 |

## Common submission requirements

| Requirement | Planned evidence | Source |
|---|---|---|
| Executable source, README, architecture diagram, short video or live demo per selected project | app code, `README.md`, diagrams, recorded demo if feasible | PDF requirement, pp.12-13 |
| Meaningful tests including failures/edges | `tests/` | PDF requirement, p.13 |
| At least 3 decisions per selected project | `docs/problem_1_decisions.md`, `docs/problem_5_decisions.md` | PDF requirement, p.13 |
| Evaluation reports, limitations and AI-tool disclosure | `evaluation/`, `docs/ai_disclosure.md` | PDF requirement, p.13 |

## Explicit implementation choices, not PDF mandates

- Implement only Problems 1 and 5 plus the common reasoning challenge, as selected in the pasted request.
- Use synthetic invoices for Problem 5; the PDF permits the candidate to select a document type.
- Proposed folder/file names, a FastAPI surface for Problem 1, selected metrics, exact chunk sizes, model provider, and any demo recording format are implementation choices.
- No FireAI-only requirements, employer PDF uploads, public repository, remote sharing, or submission are in scope.

## Initial environment and plan

- Workspace inspection found only empty `work/` and `outputs/` folders; no existing project files to preserve.
- Python 3.14.6 and Git 2.55.0 are available. FastAPI, Pydantic, Uvicorn, NumPy, FAISS, ChromaDB, sentence-transformers, and OpenAI SDK were not installed at inspection time. `pypdf` 7.1.1 was installed for reading the assessment PDF.
- No `ollama`, `docker`, or `uv` command was found. Model/API access is therefore **not yet confirmed**. The apps will use an explicit configurable model adapter; any real model evaluation stays blocked until an authorized local model or API is available.
- Stages: (1) requirements/environment and architecture; (2) local PDF/TXT ingestion + retrieval vertical slice and synthetic invoice extraction vertical slice; (3) API/model integrations and error behavior; (4) tests and separate evaluations; (5) documentation, diagrams, demonstrations, and final requirement audit.
