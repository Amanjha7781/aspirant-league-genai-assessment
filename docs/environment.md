# Environment and model record

## Evaluated environment

- OS: Windows PowerShell environment.
- Python: 3.14.6 (`C:\Python314\python.exe`).
- API/framework: FastAPI 0.165.0, Pydantic 2.14.4, Uvicorn 0.54.0.
- PDF parsing: pypdf 7.1.1.
- Vector retrieval: FAISS CPU 1.16.0.
- Embedding runtime: FastEmbed 0.9.1 and ONNX Runtime 1.32.0.
- HTTP client: HTTPX 0.28.1.
- Synthetic PDFs: ReportLab 4.4.9.
- Test runner: pytest 8.4.2.

`requirements.txt` pins direct dependencies. `requirements.lock.txt` records the complete environment resolved during this build.

## Problem 1 embedding model

- Name: `sentence-transformers/all-MiniLM-L6-v2` as selected by FastEmbed, using the ONNX artifact repository `Qdrant/all-MiniLM-L6-v2-onnx`.
- Observed repository revision at download: `d13954661f83248295ba75c1ed411eef3b7b936e`.
- Output: 384-dimensional normalized float32 vectors; CPU; no query/document prefix; default tokenizer truncates at 256 input tokens.
- Reported download size: approximately 0.09 GB; Apache-2.0 model card.
- Data handling: embeddings are generated locally after the first model download. No user document text is sent to the model-hosting site by this app.

FastEmbed currently resolves the supported model by name and the project does not vendor/pin the checkpoint artifact. A future clean setup may fetch an updated checkpoint; record the actual revision/cache when reproducing results. Pinning the model artifact or packaging an approved local model copy is an improvement.

## Problem 1 and Problem 5 language model

No LLM provider or local runner is configured in the observed environment. Therefore model-backed generation/extraction, latency, and quality are **BLOCKED**. The API accepts an OpenAI-compatible chat-completions base URL and model through `LLM_BASE_URL`, `LLM_MODEL`, optional `LLM_API_KEY`, and `LLM_TIMEOUT_SECONDS`. Current settings request JSON mode and temperature 0 with a timeout clamped to 1-60 seconds. Temperature 0 is not a guarantee of identical results.

An Ollama Windows installation was attempted from the official package through WinGet, but the GitHub installer remained at zero bytes; a direct HTTPS check failed Windows certificate revocation validation (`CRYPT_E_REVOCATION_OFFLINE`). The installation was stopped without bypassing that check. No Ollama binary or language model was installed. If a local runner is installed later, set `LLM_BASE_URL=http://localhost:11434/v1`, `LLM_MODEL` to an installed local model name, and `LLM_API_KEY=ollama` (Ollama ignores the local placeholder key). Ollama documents the OpenAI-compatible local endpoint at [its API compatibility guide](https://docs.ollama.com/api/openai-compatibility).

If a remote endpoint is selected, the full retrieved excerpts/question (Problem 1) or extracted PDF text (Problem 5) are sent to that endpoint. Use synthetic files for this assessment and check the provider's data handling. A local endpoint keeps those text calls on the machine. Secrets are read from environment variables and never logged.
