from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from rag_app.chunking import chunk_document
from rag_app.generation import grounded_answer
from rag_app.index import LocalVectorIndex
from rag_app.loaders import DocumentInputError, parse_document
from rag_app.retrieval import retrieve
from rag_app.schemas import AskRequest, AskResponse, RetrievedEvidence, SourceCitation, UploadSummary
from shared.llm import LLMClient, ModelOutputInvalid, ModelUnavailable


MAX_FILE_BYTES = 10 * 1024 * 1024
DATA_DIR = Path(os.getenv("RAG_DATA_DIR", "rag_app/data"))
index = LocalVectorIndex(DATA_DIR)
llm = LLMClient()
sessions: dict[str, list[dict[str, str]]] = {}
app = FastAPI(title="Problem 1 - Document RAG", version="0.1.0")


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "llm_configured": llm.configured, "documents_indexed": len({c['document_id'] for c in index.chunks})}


@app.post("/documents", response_model=UploadSummary)
async def upload_documents(files: list[UploadFile] = File(...)) -> UploadSummary:
    if len(files) > 20:
        raise HTTPException(status_code=413, detail="Upload at most 20 files at a time.")
    accepted, duplicates, rejected = [], [], []
    new_chunks = []
    filenames_by_id: dict[str, str] = {}
    seen_documents = {chunk["document_id"] for chunk in index.chunks}
    for upload in files:
        content = await upload.read(MAX_FILE_BYTES + 1)
        filename = Path(upload.filename or "unnamed").name
        if len(content) > MAX_FILE_BYTES:
            rejected.append({"filename": filename, "reason": "File exceeds 10 MiB."})
            continue
        try:
            document = parse_document(filename, content)
            if document.document_id in seen_documents:
                duplicates.append(filename)
                continue
            seen_documents.add(document.document_id)
            document_chunks = chunk_document(document)
            new_chunks.extend(document_chunks)
            filenames_by_id[document.document_id] = filename
            accepted.append({"document_id": document.document_id, "filename": filename, "chunks": len(document_chunks)})
        except DocumentInputError as exc:
            rejected.append({"filename": filename, "reason": str(exc)})
    _added, duplicate_ids = index.add_documents(new_chunks)
    if duplicate_ids:
        duplicate_set = set(duplicate_ids)
        duplicates.extend(filenames_by_id.get(doc_id, doc_id) for doc_id in duplicate_ids)
        accepted = [item for item in accepted if item["document_id"] not in duplicate_set]
    return UploadSummary(accepted=accepted, duplicates=duplicates, rejected=rejected)


@app.get("/search")
def search_documents(q: str, top_k: int = 5) -> list[RetrievedEvidence]:
    if not q.strip():
        raise HTTPException(status_code=422, detail="Query cannot be blank.")
    if not index.chunks:
        raise HTTPException(status_code=409, detail="Upload at least one document first.")
    top_k = min(max(top_k, 1), 10)
    found = retrieve(index, q, top_k)
    return [RetrievedEvidence(citation=SourceCitation(document_id=x['document_id'], filename=x['filename'], chunk_id=x['chunk_id'], page=x['page']), text=x['text'], similarity=x['similarity']) for x in found]


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    if not index.chunks:
        raise HTTPException(status_code=409, detail="Upload at least one document first.")
    session_id = request.session_id or str(uuid.uuid4())
    history = sessions.setdefault(session_id, [])
    # Prior user questions help resolve follow-ups; prior answers are not treated as evidence.
    retrieval_query = " ".join([turn["question"] for turn in history[-3:]] + [request.question])
    found = retrieve(index, retrieval_query, top_k=5)
    relevant = [x for x in found if x["relevant"]]
    if not relevant:
        answer = "I could not find supporting evidence in the uploaded documents."
        history.extend([{"question": request.question, "answer": answer}])
        return AskResponse(session_id=session_id, answer=answer, abstained=True, citations=[], retrieved=[], reason="No retrieved chunk reached the provisional relevance threshold.")
    try:
        answer, abstained, citation_ids = await grounded_answer(llm, request.question, history, relevant)
    except ModelUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None
    except ModelOutputInvalid as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from None
    citations = [SourceCitation(document_id=x["document_id"], filename=x["filename"], chunk_id=x["chunk_id"], page=x["page"]) for x in relevant if x["chunk_id"] in citation_ids]
    history.append({"question": request.question, "answer": answer})
    del history[:-12]
    return AskResponse(session_id=session_id, answer=answer, abstained=abstained, citations=citations, retrieved=[RetrievedEvidence(citation=SourceCitation(document_id=x['document_id'], filename=x['filename'], chunk_id=x['chunk_id'], page=x['page']), text=x['text'], similarity=x['similarity']) for x in found], reason="Model abstained based on the supplied evidence." if abstained else None)
