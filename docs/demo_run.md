# Local API demonstration record

The following is a real local API smoke demonstration executed on 2026-11-22 using the synthetic sample documents. This text log is not a video recording. This smoke run happened before a model endpoint was configured, so the generation/extraction calls below show the fail-closed 503 behavior; for the later run with the real model, see the recorded demonstration section at the end of this file.

## Start

In separate PowerShell windows from the workspace root:

```powershell
.\.verify-venv\Scripts\python.exe -m uvicorn rag_app.api:app --host 127.0.0.1 --port 8011
.\.verify-venv\Scripts\python.exe -m uvicorn extraction_app.api:app --host 127.0.0.1 --port 8012
```

Both logged `Application startup complete` and served only on `127.0.0.1`.

## Problem 1: upload and retrieve cited evidence

```powershell
curl.exe -sS -F "files=@samples/rag/park_policy.txt" -F "files=@samples/rag/emergency_procedure.pdf" http://127.0.0.1:8011/documents
```

Actual response: both synthetic files accepted, each with one chunk and no duplicates/rejections.

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8011/search?q=What%20extension%20is%20used%20for%20a%20power%20outage%3F'
```

Actual top result: `emergency_procedure.pdf`, page `1`, similarity `0.5870`, with the retrieved text stating the synthetic internal extension. The next result was the unrelated policy TXT at `0.1324`. This is evidence retrieval, not an LLM answer.

The OpenAPI document exposed `/health`, `/documents`, `/search`, and `/ask`. Health reported `status=ok`, `documents_indexed=2`, and `llm_configured=false`.

## Problem 5: explicit model/configuration and input behavior

Uploading the valid synthetic `invoice_01.pdf` to `/extract` returned HTTP 503 with `LLM is not configured. Set LLM_BASE_URL and LLM_MODEL.` The unsupported `park_policy.txt` upload returned HTTP 415 with `Only PDF input is supported.` Health reported `ocr_supported=false`; the OpenAPI document exposed `/health` and `/extract`.

The RAG `/ask` call for the supported synthetic outage question also returned HTTP 503 because no LLM is configured. This is a correctly surfaced block, not a successful answer.

## Remaining video task

A real video is not included. Installing Playwright to record the browser demonstration stalled while downloading its 42 MB wheel; the attempt was stopped. The assessment permits a live demonstration, which was exercised above. If an email explicitly requires a video file, record it later from the two live Swagger pages after a local or authorized LLM endpoint is available.


## 22 Nov 2026 recorded demonstration (real model)

A 55-second screen recording was captured on 22 Nov 2026 with the configured model `gemini-3.5-flash-lite` (free Google AI Studio key, OpenAI-compatible endpoint). The video file accompanies the submission email. It shows, against synthetic samples only:

1. RAG `/ask` "When is the front desk open?" returning a grounded answer ("staffed Monday through Friday 8:00 a.m. to 6:00 p.m., closed weekends and public holidays") with citation `facility_hours.txt`, `abstained: false`.
2. RAG `/ask` "What is the visitor permit fee?" returning "The provided evidence does not mention the visitor permit fee." with `abstained: true`.
3. Extraction `/extract` on synthetic `invoice_01.pdf` returning invoice_id NS-1042, vendor Northstar Labs, total 259.20, date 2026-01-14.
4. Extraction `/extract` on a `.txt` file returning HTTP 415 "Only PDF input is supported."

The recording is a single take of the real running applications on localhost; transient provider errors were retried by the demo script and are documented in `status_and_gaps.md`.
