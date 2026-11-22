# Problem 5 decisions

## 1. Synthetic invoices and a bounded schema

**Choice:** Use ten locally generated synthetic invoices with layout and completeness variations. The core schema is invoice ID, invoice date, vendor, currency, subtotal, tax, and total.

**Alternatives:** resumes, certificates, or real user documents. Synthetic invoices let us define independent labels and check arithmetic without exposing personal data. Invoice type and these field names are candidate choices, not employer-prescribed fields.

## 2. Preserve field status, raw value, normalized value, and evidence

**Choice:** Each field explicitly records `found`, `missing`, `incomplete`, or `ambiguous`; raw text, normalized value, evidence span, and alternatives are separate. A found value without an evidence substring is downgraded to incomplete.

**Alternatives:** nullable scalar fields or a model-generated completed JSON object. Null alone cannot distinguish missing from ambiguous, and silent normalization can hide unsupported repairs. Evidence checks improve traceability but may downgrade valid paraphrases; the prompt asks for verbatim spans.

## 3. PDF text extraction and explicit OCR boundary

**Choice:** Use `pypdf` for text PDFs, inspect the actual PDF signature, and return an OCR-required error when no selectable text exists. Upload size is capped at 5 MiB by default.

**Alternatives:** run OCR for every upload or silently accept empty text. OCR adds runtime/model dependencies and recognition errors; no OCR is implemented here. Image-only documents are explicitly unsupported and reported, not scored as successful extractions.

## 4. Deterministic validation after model extraction

**Choice:** Pydantic validates response shape; date and amount normalization are deterministic; subtotal plus tax is checked against total when all amounts parse. The validator reports a mismatch without rewriting source values.

**Alternatives:** ask the model to validate its own output or coerce every missing value. A model is not a trustworthy arithmetic checker and coercion can invent facts. The independent arithmetic check can flag rounding/discount/tax rules it does not understand, so it is reported as a simple check only.

## 5. LLM provider boundary

**Choice:** Use one small OpenAI-compatible HTTP client, requiring explicit endpoint and model configuration, with bounded timeout and JSON validation. Secrets are environment-only; logs omit content.

**Alternatives:** provider SDK lock-in or silent fake output. The common endpoint supports local OpenAI-compatible runners and authorized APIs. There is no configured language model at the time of implementation, so real extraction accuracy and model-backed demonstrations remain blocked.
