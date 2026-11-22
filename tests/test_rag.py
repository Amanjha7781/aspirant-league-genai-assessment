from __future__ import annotations

import asyncio
import json
from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from rag_app.chunking import chunk_document
from rag_app.generation import grounded_answer
from rag_app.index import LocalVectorIndex, bm25_search
from rag_app.loaders import DocumentInputError, parse_document
from shared.llm import LLMClient, ModelOutputInvalid, ModelUnavailable


def test_txt_upload_parse_and_stable_chunk_ids():
    data = b"A heading\n\nFirst paragraph.\n\nSecond paragraph."
    doc1 = parse_document("guide.txt", data)
    doc2 = parse_document("guide.txt", data)
    chunks = chunk_document(doc1)
    assert doc1.document_id == doc2.document_id
    assert chunks and chunks[0].page is None
    assert [x.chunk_id for x in chunks] == [x.chunk_id for x in chunk_document(doc2)]


def test_rejects_unsupported_bad_empty_and_scan_inputs():
    with pytest.raises(DocumentInputError, match="Only PDF and TXT"):
        parse_document("image.png", b"data")
    with pytest.raises(DocumentInputError, match="UTF-8"):
        parse_document("bad.txt", b"\xff")
    with pytest.raises(DocumentInputError, match="signature"):
        parse_document("fake.pdf", b"not a pdf")
    blank = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.write(blank)
    with pytest.raises(DocumentInputError, match="[Nn]o extractable text"):
        parse_document("blank.pdf", blank.getvalue())


def test_chunker_rejects_bad_limits():
    doc = parse_document("one.txt", b"A short example.")
    with pytest.raises(ValueError):
        chunk_document(doc, max_chars=50, overlap=4)


def test_faiss_search_duplicate_and_bm25(tmp_path: Path):
    index = LocalVectorIndex(tmp_path)
    first = chunk_document(parse_document("parking.txt", b"Visitors need a dashboard permit for visitor parking."))
    added, duplicates = index.add_documents(first)
    assert added == 1 and not duplicates
    added_again, duplicates_again = index.add_documents(first)
    assert added_again == 0 and duplicates_again
    vector_result = index.search("permit for visitors", top_k=1)
    lexical_result = bm25_search("permit visitors", index.chunks, top_k=1)
    assert vector_result[0][0]["filename"] == "parking.txt"
    assert lexical_result[0][0]["filename"] == "parking.txt"
    loaded = LocalVectorIndex(tmp_path)
    assert len(loaded.chunks) == 1


class FakeLLM:
    async def json_chat(self, *, system: str, user: str):
        return {"answer": "Visitors need a permit.", "abstained": False, "citation_chunk_ids": ["chunk-1"]}


class BadCitationLLM:
    async def json_chat(self, *, system: str, user: str):
        return {"answer": "A fabricated answer.", "abstained": False, "citation_chunk_ids": ["not-retrieved"]}


def test_grounded_answer_only_allows_retrieved_citations():
    evidence = [{"chunk_id": "chunk-1", "filename": "parking.txt", "page": None, "text": "Permit required."}]
    answer, abstained, citations = asyncio.run(grounded_answer(FakeLLM(), "Permit?", [], evidence))
    assert answer == "Visitors need a permit." and not abstained and citations == ["chunk-1"]
    with pytest.raises(ModelOutputInvalid, match="not retrieved"):
        asyncio.run(grounded_answer(BadCitationLLM(), "Permit?", [], evidence))


def test_rag_api_upload_and_search(tmp_path: Path, monkeypatch):
    from rag_app import api

    monkeypatch.setattr(api, "index", LocalVectorIndex(tmp_path))
    client = TestClient(api.app)
    payload = b"Front desk hours are Monday to Friday, 8 a.m. to 6 p.m."
    pdf_path = Path("samples/rag/emergency_procedure.pdf")
    response = client.post("/documents", files=[("files", ("hours.txt", payload, "text/plain")), ("files", (pdf_path.name, pdf_path.read_bytes(), "application/pdf"))])
    assert response.status_code == 200, response.text
    assert len(response.json()["accepted"]) == 2
    result = client.get("/search", params={"q": "When is the front desk staffed?"})
    assert result.status_code == 200
    assert result.json()[0]["citation"]["filename"] == "hours.txt"
    duplicate = client.post("/documents", files=[("files", ("hours.txt", payload, "text/plain"))])
    assert duplicate.status_code == 200 and duplicate.json()["duplicates"]
    pdf_search = client.get("/search", params={"q": "What extension is used for a power outage?"})
    assert pdf_search.status_code == 200 and pdf_search.json()[0]["citation"]["page"] == 1
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.setattr(api, "llm", LLMClient())
    unavailable = client.post("/ask", json={"question": "What extension is used for a power outage?"})
    assert unavailable.status_code == 503


def test_duplicate_files_in_same_request_report_one_acceptance(tmp_path: Path, monkeypatch):
    from rag_app import api
    monkeypatch.setattr(api, "index", LocalVectorIndex(tmp_path))
    client = TestClient(api.app)
    payload = b"Synthetic duplicated document content."
    response = client.post("/documents", files=[("files", ("one.txt", payload, "text/plain")), ("files", ("copy.txt", payload, "text/plain"))])
    assert response.status_code == 200
    assert len(response.json()["accepted"]) == 1
    assert response.json()["duplicates"] == ["copy.txt"]


def test_followup_context_stays_in_its_session(tmp_path: Path, monkeypatch):
    from rag_app import api

    monkeypatch.setattr(api, "index", LocalVectorIndex(tmp_path))
    api.sessions.clear()
    captured = []

    class RecordingLLM:
        async def json_chat(self, *, system: str, user: str):
            payload = json.loads(user)
            captured.append(payload)
            return {"answer": "See retrieved evidence.", "abstained": False, "citation_chunk_ids": [payload["evidence"][0]["chunk_id"]]}

    monkeypatch.setattr(api, "llm", RecordingLLM())
    client = TestClient(api.app)
    text = b"Front desk hours are Monday through Friday from 8 a.m. to 6 p.m. The desk is closed weekends."
    assert client.post("/documents", files=[("files", ("hours.txt", text, "text/plain"))]).status_code == 200
    first = client.post("/ask", json={"question": "When is the front desk staffed?", "session_id": "session-a"})
    followup = client.post("/ask", json={"question": "What about weekends?", "session_id": "session-a"})
    other = client.post("/ask", json={"question": "What about weekends?", "session_id": "session-b"})
    assert first.status_code == followup.status_code == other.status_code == 200
    assert captured[0]["recent_conversation"] == []
    assert len(captured[1]["recent_conversation"]) == 1
    assert captured[2]["recent_conversation"] == []


def test_conflicting_files_retrieve_as_separate_sources():
    from rag_app.retrieval import retrieve

    documents = [
        parse_document("posted.txt", b"Visitors may park in marked spaces until 6 p.m."),
        parse_document("draft.txt", b"An internal draft says visitors may use marked spaces until 7 p.m.; it does not state whether it replaces the posted policy."),
    ]
    chunks = [chunk for document in documents for chunk in chunk_document(document)]
    # Use a temporary disk index because FAISS is part of this genuine retrieval check.
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        index = LocalVectorIndex(directory)
        index.add_documents(chunks)
        found = retrieve(index, "What time may visitors park until?", top_k=2)
    assert {item["filename"] for item in found} == {"posted.txt", "draft.txt"}
