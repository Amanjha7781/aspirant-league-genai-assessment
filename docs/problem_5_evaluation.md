# Problem 5 evaluation report

## Dataset

Ten synthetic invoice PDFs are generated locally with ten layout variations, including compact statements, table-like rows, missing fields, a deliberately ambiguous date, a missing vendor, and multiple date/currency styles. The independent labels in `samples/extraction/ground_truth.json` specify field status and normalized value before any model result is scored. Dates normalize to ISO `YYYY-MM-DD`; monetary values normalize to decimal strings with two places and grouping/currency symbols removed.

## Metrics and denominators

- Schema-validity rate: schema-valid extraction documents / 10 documents.
- Field exact-match accuracy: matching status and normalized value / 70 annotated fields. Missing and ambiguous labels are included; failed model documents count incorrect.
- Expected-present value accuracy: correct normalized found values / every field labeled found in ground truth. Missing outputs and failed documents count incorrect.

These extraction metrics are distinct from schema validity. A well-formed value without matching source evidence is downgraded to incomplete and does not score as correct.

## Actual results and limitations

`python -m evaluation.extraction.run` writes `evaluation/extraction/raw_results.json`. Status on 22 Nov 2026: **COMPLETE** with gemini-3.5-flash-lite (free Google AI Studio key, temperature 0) over all 10 synthetic invoices - schema validity 1.0, field exact-match accuracy 0.9571 (67/70), expected present-value accuracy 0.9848 (65/66). Three residual per-field misses and 5 bounded retries of transient provider errors are recorded per document in the raw results. No mocked extraction or hand-written answer is presented as model performance.

Unit tests cover valid text PDFs, unsupported content, malformed PDFs, scan/OCR-required detection, missing/ambiguous status preservation, evidence mismatch, arithmetic mismatch, OpenAPI schema availability, size enforcement, and fail-closed model access. OCR is not implemented. Invoice arithmetic assumes subtotal + tax = total; discounts, freight, withholding, tax-inclusive amounts, multiple rates, and currency-specific rounding need explicit future rules.
