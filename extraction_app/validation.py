from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from extraction_app.schemas import ExtractedField, InvoiceCandidate, ValidationCheck


def _compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def _money(value: str | None) -> Decimal | None:
    if not value:
        return None
    cleaned = re.sub(r"[^0-9,.-]", "", value).replace(",", "")
    try:
        return Decimal(cleaned).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def normalize_field(name: str, field: ExtractedField, source_text: str) -> tuple[ExtractedField, list[str]]:
    warnings: list[str] = []
    if field.status != "found":
        if field.raw_value is not None:
            warnings.append(f"{name}: non-found status has a raw value; reviewer should inspect it.")
        return field.model_copy(update={"normalized_value": None}), warnings
    if not field.raw_value or not field.evidence:
        warnings.append(f"{name}: model marked found without both a value and evidence; downgraded to incomplete.")
        return field.model_copy(update={"status": "incomplete", "normalized_value": None}), warnings
    if _compact(field.evidence) not in _compact(source_text):
        warnings.append(f"{name}: quoted evidence was not found in extracted PDF text; downgraded to incomplete.")
        return field.model_copy(update={"status": "incomplete", "normalized_value": None}), warnings

    raw = field.raw_value.strip()
    normalized: str | None = raw
    if name == "invoice_date":
        normalized = None
        for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%b %d, %Y", "%B %d, %Y", "%d %b %Y"):
            try:
                normalized = datetime.strptime(raw, pattern).date().isoformat()
                break
            except ValueError:
                continue
        if normalized is None:
            warnings.append("invoice_date: found text could not be normalized to a recognized date.")
    elif name == "currency":
        normalized = raw.upper()
    elif name in {"subtotal", "tax", "total"}:
        amount = _money(raw)
        normalized = format(amount, ".2f") if amount is not None else None
        if normalized is None:
            warnings.append(f"{name}: found text could not be normalized as an amount.")
    return field.model_copy(update={"normalized_value": normalized}), warnings


def validate_candidate(candidate: InvoiceCandidate, source_text: str) -> tuple[InvoiceCandidate, list[ValidationCheck], list[str]]:
    warnings: list[str] = []
    normalized_fields = {}
    for name, field in candidate:
        normalized_fields[name], field_warnings = normalize_field(name, field, source_text)
        warnings.extend(field_warnings)
    validated = InvoiceCandidate(**normalized_fields)

    subtotal = _money(validated.subtotal.normalized_value)
    tax = _money(validated.tax.normalized_value)
    total = _money(validated.total.normalized_value)
    checks = []
    if subtotal is not None and tax is not None and total is not None:
        passed = subtotal + tax == total
        checks.append(ValidationCheck(name="subtotal_plus_tax_equals_total", status="passed" if passed else "failed", detail=f"Calculated {subtotal + tax:.2f}; extracted total {total:.2f}."))
        if not passed:
            warnings.append("Arithmetic check failed; the source values have not been changed.")
    else:
        checks.append(ValidationCheck(name="subtotal_plus_tax_equals_total", status="not_checkable", detail="At least one amount is missing or could not be normalized."))
    status = "complete" if all(getattr(validated, key).status == "found" for key in ("invoice_id", "invoice_date", "vendor", "currency", "subtotal", "tax", "total")) else "incomplete"
    return validated, checks, warnings
