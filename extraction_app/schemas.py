from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


FieldStatus = Literal["found", "missing", "incomplete", "ambiguous"]


class ExtractedField(BaseModel):
    model_config = {"extra": "forbid"}
    status: FieldStatus
    raw_value: str | None = None
    normalized_value: str | None = None
    evidence: str | None = None
    alternatives: list[str] = Field(default_factory=list)


class InvoiceCandidate(BaseModel):
    model_config = {"extra": "forbid"}
    invoice_id: ExtractedField
    invoice_date: ExtractedField
    vendor: ExtractedField
    currency: ExtractedField
    subtotal: ExtractedField
    tax: ExtractedField
    total: ExtractedField


class ValidationCheck(BaseModel):
    name: str
    status: Literal["passed", "failed", "not_checkable"]
    detail: str


class InvoiceExtractionResponse(BaseModel):
    status: Literal["complete", "incomplete"]
    fields: InvoiceCandidate
    validation_checks: list[ValidationCheck]
    warnings: list[str]
    source_filename: str

