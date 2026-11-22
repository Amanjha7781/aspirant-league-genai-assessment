from __future__ import annotations

import hashlib
from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader


@dataclass
class PageText:
    page: int | None
    text: str


@dataclass
class ParsedDocument:
    document_id: str
    filename: str
    pages: list[PageText]


class DocumentInputError(ValueError):
    pass


def parse_document(filename: str, content: bytes) -> ParsedDocument:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix not in {"pdf", "txt"}:
        raise DocumentInputError("Only PDF and TXT files are supported.")
    if not content:
        raise DocumentInputError("The file is empty.")

    pages: list[PageText] = []
    if suffix == "txt":
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise DocumentInputError("TXT files must be UTF-8 encoded.") from None
        pages.append(PageText(page=None, text=text))
    else:
        if not content.startswith(b"%PDF-"):
            raise DocumentInputError("File extension is PDF but PDF signature is missing.")
        try:
            reader = PdfReader(BytesIO(content), strict=True)
            if reader.is_encrypted:
                raise DocumentInputError("Encrypted PDFs are not supported.")
            pages = [PageText(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
        except DocumentInputError:
            raise
        except Exception as exc:
            raise DocumentInputError(f"PDF could not be read ({type(exc).__name__}).") from None
        if not pages:
            raise DocumentInputError("PDF contains no pages.")
        if not any(page.text.strip() for page in pages):
            raise DocumentInputError("No extractable text found; this may be a scan and needs OCR.")

    if not any(p.text.strip() for p in pages):
        raise DocumentInputError("Document contains no extractable text.")
    document_id = hashlib.sha256(content).hexdigest()[:20]
    return ParsedDocument(document_id=document_id, filename=filename, pages=pages)
