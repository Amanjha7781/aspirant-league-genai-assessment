from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass

from rag_app.loaders import ParsedDocument


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    filename: str
    page: int | None
    text: str

    def as_dict(self) -> dict:
        return asdict(self)


def _split_long_paragraph(text: str, max_chars: int, overlap: int) -> list[str]:
    output: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start + max_chars // 2, end)
            if boundary > start:
                end = boundary
        output.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [value for value in output if value]


def chunk_document(document: ParsedDocument, max_chars: int = 900, overlap: int = 120) -> list[Chunk]:
    if max_chars < 200 or overlap < 0 or overlap >= max_chars:
        raise ValueError("Require max_chars >= 200 and 0 <= overlap < max_chars.")
    chunks: list[Chunk] = []
    for page in document.pages:
        paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", page.text)]
        paragraphs = [p for p in paragraphs if p]
        groups: list[str] = []
        current = ""
        for paragraph in paragraphs:
            pieces = _split_long_paragraph(paragraph, max_chars, overlap) if len(paragraph) > max_chars else [paragraph]
            for piece in pieces:
                combined = f"{current}\n{piece}" if current else piece
                if current and len(combined) > max_chars:
                    groups.append(current)
                    current = current[-overlap:] + "\n" + piece if overlap else piece
                else:
                    current = combined
        if current:
            groups.append(current)
        for position, text in enumerate(groups):
            stable = f"{document.document_id}:{page.page}:{position}:{text}"
            chunk_id = hashlib.sha256(stable.encode("utf-8")).hexdigest()[:20]
            chunks.append(Chunk(chunk_id, document.document_id, document.filename, page.page, text))
    return chunks
