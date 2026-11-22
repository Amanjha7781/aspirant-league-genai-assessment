from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    document_id: str
    filename: str
    chunk_id: str
    page: int | None = None


class RetrievedEvidence(BaseModel):
    citation: SourceCitation
    text: str
    similarity: float


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None


class AskResponse(BaseModel):
    session_id: str
    answer: str
    abstained: bool
    citations: list[SourceCitation]
    retrieved: list[RetrievedEvidence]
    reason: str | None = None


class UploadSummary(BaseModel):
    accepted: list[dict[str, str | int]]
    duplicates: list[str]
    rejected: list[dict[str, str]]
