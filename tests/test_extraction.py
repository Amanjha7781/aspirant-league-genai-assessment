from __future__ import annotations

from decimal import Decimal

from reportlab.pdfgen import canvas
from fastapi.testclient import TestClient

from extraction_app.pdf import PDFInputError, extract_pdf_text
from extraction_app.schemas import ExtractedField, InvoiceCandidate, InvoiceExtractionResponse
from extraction_app.validation import validate_candidate
from shared.llm import LLMClient, ModelOutputInvalid


def make_text_pdf(text: str) -> bytes:
    from io import BytesIO
    output = BytesIO()
    pdf = canvas.Canvas(output)
    y = 760
    for line in text.splitlines():
        pdf.drawString(50, y, line)
        y -= 20
    pdf.save()
    return output.getvalue()


def test_pdf_text_extraction_and_invalid_input():
    text, pages = extract_pdf_text(make_text_pdf("SYNTHETIC INVOICE\nTotal: 12.00"))
    assert pages == 1 and "Total: 12.00" in text
    try:
        extract_pdf_text(b"not a pdf")
        assert False, "Expected PDFInputError"
    except PDFInputError as exc:
        assert exc.status_code == 415
    try:
        extract_pdf_text(b"%PDF-broken")
        assert False, "Expected malformed PDF error"
    except PDFInputError as exc:
        assert exc.status_code == 422


def test_scan_only_pdf_is_reported_as_ocr_required():
    from io import BytesIO
    from pypdf import PdfWriter
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.write(output)
    try:
        extract_pdf_text(output.getvalue())
        assert False, "Expected scan/OCR boundary error"
    except PDFInputError as exc:
        assert "OCR is required" in str(exc)


def test_missing_and_invented_value_handling_and_arithmetic():
    source = "Invoice INV-1\nDate: 2026-01-02\nVendor: Cedar\nCurrency USD\nSubtotal 10.00\nTax 1.00\nTotal 11.00"
    found = lambda raw, evidence: ExtractedField(status="found", raw_value=raw, evidence=evidence)
    missing = lambda: ExtractedField(status="missing")
    candidate = InvoiceCandidate(
        invoice_id=found("INV-1", "Invoice INV-1"), invoice_date=found("2026-01-02", "Date: 2026-01-02"),
        vendor=found("Cedar", "Vendor: Cedar"), currency=found("USD", "Currency USD"),
        subtotal=found("10.00", "Subtotal 10.00"), tax=found("1.00", "Tax 1.00"), total=found("12.00", "Total 11.00"),
    )
    validated, checks, warnings = validate_candidate(candidate, source)
    assert validated.total.normalized_value == "12.00"  # preserves the candidate value, validator does not repair it
    assert checks[0].status == "failed" and warnings
    fabricated = candidate.model_copy(update={"vendor": found("Invented Corp", "Vendor: Invented Corp")})
    validated, _, warnings = validate_candidate(fabricated, source)
    assert validated.vendor.status == "incomplete"
    assert any("not found" in warning for warning in warnings)


def test_ambiguous_and_missing_values_remain_explicit():
    field = ExtractedField(status="ambiguous", alternatives=["03/04/2026", "04/03/2026"])
    normalized, warnings = __import__("extraction_app.validation", fromlist=["normalize_field"]).normalize_field("invoice_date", field, "Date: 03/04/2026; Printed: 04/03/2026")
    assert normalized.status == "ambiguous" and normalized.normalized_value is None
    assert not warnings


def test_example_structured_output_matches_response_schema():
    import json
    from pathlib import Path
    sample = Path("samples/extraction/example_invoice_01_output.json")
    result = InvoiceExtractionResponse.model_validate_json(sample.read_text("utf-8"))
    assert result.status == "complete"
    assert result.fields.invoice_id.normalized_value == "NS-1042"


def test_unexpected_model_output_is_classified_as_invalid():
    import asyncio
    from extraction_app.extractor import extract_invoice

    class InvalidOutput:
        async def json_chat(self, *, system: str, user: str):
            return {"invoice_id": "invented", "extra": "unexpected"}

    try:
        asyncio.run(extract_invoice(InvalidOutput(), "invoice text"))
        assert False, "Expected schema validation error"
    except ModelOutputInvalid as exc:
        assert "schema validation" in str(exc)


def test_extract_api_openapi_and_missing_model_behavior(monkeypatch):
    from extraction_app import api
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.setattr(api, "llm", LLMClient())
    client = TestClient(api.app)
    assert "/extract" in client.get("/openapi.json").json()["paths"]
    unsupported = client.post("/extract", files={"file": ("file.txt", b"text", "text/plain")})
    assert unsupported.status_code == 415
    unavailable = client.post("/extract", files={"file": ("invoice.pdf", make_text_pdf("Total: 3.00"), "application/pdf")})
    assert unavailable.status_code == 503
    monkeypatch.setattr(api, "MAX_UPLOAD_BYTES", 10)
    oversized = client.post("/extract", files={"file": ("invoice.pdf", b"%PDF-" + b"x" * 30, "application/pdf")})
    assert oversized.status_code == 413
    monkeypatch.setattr(api, "MAX_UPLOAD_BYTES", 5 * 1024 * 1024)
    async def invalid_output(*args, **kwargs):
        raise ModelOutputInvalid("unexpected JSON shape")
    monkeypatch.setattr(api, "extract_invoice", invalid_output)
    from pathlib import Path
    sample_pdf = Path("samples/extraction/invoice_01.pdf").read_bytes()
    invalid_model = client.post("/extract", files={"file": ("invoice.pdf", sample_pdf, "application/pdf")})
    assert invalid_model.status_code == 502
