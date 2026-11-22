# Problem 1 evaluation report

## Dataset and method

The evaluation uses 15 hand-labeled questions against four unique synthetic documents (three TXT and one PDF). `facility_hours_copy.txt` is byte-identical to `facility_hours.txt`; ingestion deduplicates it by SHA-256. A separate revision document deliberately conflicts with posted visitor hours. Queries include multi-document retrieval, conflicts, irrelevant questions, and expected abstentions.

The script runs MiniLM/FAISS and BM25 on the same queries and same chunks. The labels identify expected source names, not all individual chunk spans. All query labels are design annotations, not independent external user research. The evaluation corpus and labels were iterated during implementation and are not held out from development; the metrics are exploratory, not a blind benchmark.

## Metrics and denominators

- Source hit rate@5: queries with at least one expected source in the top five / all 15 queries. Abstention questions count as misses.
- Answerable-query source hit rate@5: answerable queries with at least one expected source / 12 answerable queries.
- Expected-source coverage@5: macro average of expected source names present in top five / expected source names per query, with zero for queries with none expected.
- Chunk precision@5: top-five chunks from expected source files / 75 total slots (15 queries × 5); missing slots count incorrect. This small corpus has only four unique chunks, so this measure is conservative and low-resolution.
- Similarity-gate rate on expected-abstention queries: queries labeled as unavailable whose MiniLM top score is at least 0.30 / 3 such queries. This measures only the candidate gate; it does not establish that an answer is available or unavailable.

## Actual retrieval result

`python -m evaluation.rag.run` writes complete per-query semantic and BM25 rankings and scores to `evaluation/rag/raw_results.json`. On the current run, MiniLM/FAISS and BM25 produce the same source-level metrics: source hit rate@5 0.8000 over all queries, answerable-query hit rate@5 1.0000 over 12 answerable queries, expected-source coverage@5 0.8000, and chunk precision@5 0.2267 under the stated denominator. The similarity gate triggers on 2/3 expected-abstention queries (0.6667); this is not an answerability classifier. Neither retriever demonstrates a source-level advantage. See raw results for query-specific ranks and scores.

**Answer generation, citation support and abstention were measured on 22 Nov 2026** with gemini-3.5-flash-lite (free Google AI Studio key, temperature 0): all 15 labeled queries were answered by the real model; 12/12 answerable queries returned answers whose citations all came from the retrieved allowlist; 2/3 expected-abstention queries abstained correctly; one calibration miss (R15: the answer text reported the information absent but the abstain flag was not set) is recorded per query in `evaluation/rag/answer_support_review.json`. Unit tests use fake clients only to verify citation allowlisting and response contracts; they are not model-quality evidence. The 0.30 relevance threshold is provisional; the permit-fee query is a known difficult negative because it is topically close to policy excerpts. This confirms why retrieval score alone cannot certify factual support.

## Failure cases exercised

1. Unsupported file type, invalid UTF-8 text, malformed PDF signature, blank/scan-style PDF without extractable text.
2. Exact duplicate document upload and persistent index reload.
3. Fabricated citation ID rejected by the answer contract.
4. Unanswerable policy questions and a conflicting revision are included in the labeled query set; in the 22 Nov 2026 run the conflicting-revision query (R13) surfaced the conflicting documents, and two of three expected-abstention queries abstained (the third miss is recorded in `answer_support_review.json`).

## Improvements

Create a larger held-out set with gold chunk spans; compare hybrid BM25+dense retrieval and a reranker; tune chunk boundaries and threshold only on a development set; measure source precision/recall and abstention false positives separately; then run a real model and have a reviewer label every answer's support and citations.
