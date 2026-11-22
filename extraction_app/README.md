# Problem 5: Structured invoice extraction

Run from the workspace root after following the root README setup:

```powershell
.\.venv\Scripts\python.exe -m uvicorn extraction_app.api:app --reload --port 8002
```

Upload a PDF to `POST /extract`. The app checks the extension, PDF signature, and 5 MiB limit; extracts text with pypdf; requests JSON extraction from the configured LLM; validates the candidate with Pydantic; checks copied evidence against source text; normalizes dates/amounts; and reports arithmetic consistency without rewriting values. Scan-only PDFs return 422 and state that OCR is required; OCR is not supported.

The field schema is an implementation choice for synthetic invoices: invoice ID, date, vendor, currency, subtotal, tax, and total. Each field keeps raw value, normalized value, status, evidence, and alternatives. No configured model means 503; malformed model output means 502. Logs record failure categories but not document content.

Run tests with `.\.venv\Scripts\python.exe -m pytest tests/test_extraction.py -q` and the model evaluation with `.\.venv\Scripts\python.exe -m evaluation.extraction.run`. OpenAPI/Swagger appears at `/docs`.
