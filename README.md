# Aspirant League assessment projects

Two separate applications are being built for the selected assessment problems: document question answering (Problem 1) and structured invoice extraction (Problem 5). The common reasoning challenge is documented separately. The assessment PDF is confidential and is not copied into this project.

## Status

The local embedding model and FAISS index are available for Problem 1. A language model is not currently configured. The apps fail closed for answer generation/extraction when the configured LLM is missing or unavailable; no mocked output is presented as a real model result. See `docs/status_and_gaps.md` for the evidence audit.

## Setup (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
Copy-Item .env.example .env
```

`requirements.txt` lists pinned direct dependencies; `requirements.lock.txt` records all resolved package versions for this Windows/Python 3.14 environment.

Set `LLM_BASE_URL`, `LLM_MODEL`, and `LLM_API_KEY` in the local `.env` only when an authorized OpenAI-compatible chat-completions endpoint is available. Ollama can be used with its local OpenAI-compatible endpoint. Do not put secrets in source, reports, or chat. The first embedding call downloads the Apache-2.0 `all-MiniLM-L6-v2` ONNX model from Hugging Face; after that it runs locally. Model endpoint calls send only the synthetic sample/document text and question; never upload employer or personal documents.

## Run the applications

```powershell
.\.venv\Scripts\python.exe -m uvicorn rag_app.api:app --reload --port 8001
.\.venv\Scripts\python.exe -m uvicorn extraction_app.api:app --reload --port 8002
```

Open `http://127.0.0.1:8001/docs` or `http://127.0.0.1:8002/docs` for the interactive API documentation. Each app has its own persistence and request path.

## Run checks and evaluations

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m evaluation.rag.run
.\.venv\Scripts\python.exe -m evaluation.extraction.run
```

Model-backed evaluations require the configured LLM endpoint and are reported as blocked when it is absent. Synthetic evaluation inputs and independent expected labels are under `samples/` and `evaluation/`.

## API quick path

Start Problem 1, upload the synthetic policy TXT and emergency procedure PDF through `/documents`, then inspect `/search?q=When%20is%20the%20front%20desk%20open%3F`. `/ask` returns an evidence-based abstention for weak retrieval; with relevant chunks it requires a configured LLM and returns 503 when none is configured.

Start Problem 5 and upload `samples/extraction/invoice_01.pdf` to `/extract`. It returns 503 until a real LLM endpoint is configured. Invalid format, malformed PDF, oversized PDF, and scan-only PDF paths return explicit error responses. Both OpenAPI docs pages describe request and response schemas.

`.\.venv\Scripts\python.exe samples/extraction/generate_samples.py` regenerates the ten synthetic invoice PDFs. `.\.venv\Scripts\python.exe samples/rag/generate_pdf_sample.py` regenerates the RAG PDF sample. `samples/extraction/ground_truth.json` contains independently written field labels and normalization rules. The PDF generators need ReportLab; the generated sample PDFs are included. `samples/extraction/example_invoice_01_output.json` illustrates the response schema and is an expected synthetic example, not a model output.

## Project map

- `rag_app/`: Problem 1 upload, parsing, paragraph-aware chunking, local embeddings, FAISS, retrieval and grounded answer generation.
- `extraction_app/`: Problem 5 PDF upload, text extraction, model extraction, Pydantic validation and field status reporting.
- `samples/`: synthetic text/PDF fixtures and expected labels only.
- `evaluation/`: separate reproducible evaluation scripts and raw artifacts.
- `docs/`: requirements map, design decisions, diagrams, evaluation, AI disclosure and common reasoning challenge.

## Privacy and limitations

All source data stays local unless a user configures an external LLM endpoint. The local embedding model is used only for Problem 1 and receives document/query text on the local machine. Scan-only PDFs are detected but OCR is not implemented. RAG persistence is local. API keys are read from environment variables and never logged. These are learning projects, not production services.

