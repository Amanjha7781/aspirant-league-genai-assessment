from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from extraction_app.extractor import extract_invoice
from extraction_app.pdf import PDFInputError, extract_pdf_text
from extraction_app.schemas import InvoiceExtractionResponse
from extraction_app.validation import validate_candidate
from shared.llm import LLMClient, ModelOutputInvalid, ModelUnavailable


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("invoice_api")
MAX_UPLOAD_BYTES = int(os.getenv("EXTRACTION_MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))
llm = LLMClient()
app = FastAPI(title="Problem 5 - Invoice Extraction", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {"status": "ok", "llm_configured": llm.configured, "ocr_supported": False}


@app.post("/extract", response_model=InvoiceExtractionResponse)
async def extract(file: UploadFile = File(...)) -> InvoiceExtractionResponse:
    filename = Path(file.filename or "unnamed").name
    if not filename.lower().endswith(".pdf"):
        logger.info("rejected_upload reason=unsupported_extension")
        raise HTTPException(status_code=415, detail="Only PDF input is supported.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        logger.info("rejected_upload reason=oversized")
        raise HTTPException(status_code=413, detail=f"PDF exceeds the {MAX_UPLOAD_BYTES}-byte limit.")
    try:
        document_text, _page_count = extract_pdf_text(content)
    except PDFInputError as exc:
        logger.info("rejected_upload reason=pdf_processing status=%s", exc.status_code)
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from None
    try:
        candidate = await extract_invoice(llm, document_text)
    except ModelUnavailable as exc:
        logger.warning("extraction_failed reason=model_unavailable")
        raise HTTPException(status_code=503, detail=str(exc)) from None
    except ModelOutputInvalid as exc:
        logger.warning("extraction_failed reason=invalid_model_output")
        raise HTTPException(status_code=502, detail=str(exc)) from None
    fields, checks, warnings = validate_candidate(candidate, document_text)
    status = "complete" if all(getattr(fields, key).status == "found" for key in fields.__class__.model_fields) else "incomplete"
    logger.info("extraction_finished status=%s warning_count=%d", status, len(warnings))
    return InvoiceExtractionResponse(status=status, fields=fields, validation_checks=checks, warnings=warnings, source_filename=filename)
