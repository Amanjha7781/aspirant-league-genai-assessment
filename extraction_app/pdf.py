from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader


class PDFInputError(ValueError):
    def __init__(self, message: str, status_code: int = 422):
        super().__init__(message)
        self.status_code = status_code


def extract_pdf_text(content: bytes) -> tuple[str, int]:
    if not content.startswith(b"%PDF-"):
        raise PDFInputError("File content is not a PDF.", 415)
    try:
        reader = PdfReader(BytesIO(content), strict=True)
        if reader.is_encrypted:
            raise PDFInputError("Encrypted PDFs are not supported.")
        if not reader.pages:
            raise PDFInputError("PDF contains no pages.")
        page_texts = [page.extract_text() or "" for page in reader.pages]
    except PDFInputError:
        raise
    except Exception as exc:
        raise PDFInputError(f"PDF could not be read ({type(exc).__name__}).") from None
    text = "\n\n".join(page_texts).strip()
    if not text:
        raise PDFInputError("No selectable text found; OCR is required for this scan.")
    return text, len(reader.pages)
