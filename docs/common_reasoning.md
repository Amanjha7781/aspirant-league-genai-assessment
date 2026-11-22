# Think Like a GenAI Engineer

This is an analysis document, not a third prototype. Current observations are separated from proposals. Update 22 Nov 2026: a real model (gemini-3.5-flash-lite, free Google AI Studio key) was configured and both model-backed evaluations were run, so the observations below now include real model behavior recorded in `evaluation/rag/raw_results.json`, `evaluation/rag/answer_support_review.json`, and `evaluation/extraction/raw_results.json`.

## 1. Confidently incorrect answers

**Plausible causes:** weak or incomplete retrieved evidence, chunk boundaries separating conditions, model prior knowledge overriding the source, contradictory documents, or a cited passage that does not support the answer.

**Investigate:** preserve the question, retrieved chunk IDs/text, similarity scores, prompt version, model/provider/version, output, and human support label. Re-run the same case and check whether the source was absent, retrieval was wrong, or generation overstated it. Logs should avoid storing document text by default; evaluation artifacts use synthetic data.

**Fixes:** retrieval coverage and reranking (retrieval work); concise evidence-only prompt and explicit abstention contract (prompt work); citation allowlist and output schema (application logic); stronger or better-calibrated model (model selection); conflict detection and human review for consequential results (other). The RAG app already enforces that returned chunk IDs came from retrieval, but that does not prove the answer is supported by those chunks.

**Validate and fail safely:** independently review answer-to-source support on held-out questions; count unsupported answers separately from retrieval hits. If evidence is missing or conflicting, return a clear abstention or conflict statement with no invented resolution.

## 2. Irrelevant retrieval

**Plausible causes:** ambiguous wording, short chunks without context, domain mismatch in the embedding model, duplicate content, or a similarity threshold chosen without labeled data.

**Investigate:** inspect query, top-k IDs, scores, expected source labels, and compare the same query using BM25. Current local evaluation uses 15 synthetic building-policy queries. MiniLM/FAISS and BM25 each achieved source-hit rate@5 0.8000 overall, 1.0000 for the 12 answerable questions, expected-source coverage@5 0.8000, and chunk precision@5 0.2267 under the report's denominator; no advantage is demonstrated. Query R11 (visitor permit fee, expected abstention) still retrieved policy chunks with MiniLM top similarity 0.412, showing that topical similarity is not factual answerability.

**Fixes:** improve extraction/chunk context and labels, tune the relevance threshold on training/development queries only, add a reranker or hybrid retrieval, deduplicate by content, and separately require answer-level evidence. A threshold filters candidates but does not establish truth.

**Validate and fail safely:** report source hit, source coverage, precision@k, and abstention false-positive rate, with explicit denominators. Keep a held-out set. If a candidate is only topically similar but does not contain the requested fact, the model should abstain.

## 3. Unexpected model-output format

**Plausible causes:** provider ignores JSON mode, truncation, extra prose, incompatible endpoint behavior, or the prompt/schema changes.

**Investigate:** inspect HTTP status, provider/model version, response content type, and parse/schema error categories. Do not log raw document contents or API keys. The current unit suite tests schema/citation contracts with labeled fake clients; this is not evidence of model quality.

**Fixes:** request JSON output (prompt/provider feature); validate every response with Pydantic or explicit type checks (application logic); allow at most one bounded repair attempt only if it can preserve evidence, otherwise return an explicit 502. Never accept partial JSON as a successful extraction.

**Validate and fail safely:** test malformed JSON, missing keys, wrong types, extra keys, and fabricated citations. The current apps reject wrong response shapes or citations that were not retrieved. Extraction fields marked found without quoted evidence are downgraded to incomplete.

## 4. Failed or slow external APIs

**Plausible causes:** network outage, rate limits, bad credentials, overloaded provider, or request/payload size.

**Investigate:** record request duration, status class, timeout/error category, provider/model name, and a correlation ID. Never log headers containing secrets or document text. Current code uses a 1-60 second bounded timeout, returns 503 when no model is configured or the request fails, and does not retry indefinitely. Update 22 Nov 2026: live transient provider errors were observed during the real evaluation runs (5 retried calls across the extraction run); bounded retries with backoff (3 attempts, 45 s) cleared them and no call was silently dropped. Formal latency percentiles were not measured.

**Fixes:** bounded retries with backoff for transient failures, concurrency limits, circuit breaker, smaller contexts, local fallback, or asynchronous jobs (application/system work). Do not retry invalid requests or schema errors endlessly.

**Validate and fail safely:** inject timeout/429/5xx cases in unit/integration tests and measure p50/p95 latency when a real endpoint is authorized. Return an explicit service error; never return a cached or fabricated success without telling the user.

## 5. Different outputs for the same query

**Plausible causes:** sampling, model/provider updates, mutable source data, tied retrieval scores, changing conversation history, or nondeterministic infrastructure.

**Investigate:** hold constant the query, source/index version, session history, provider/model ID, prompt, and settings; compare retrieval rankings separately from generated text. Store a synthetic regression set and prompt version in evaluation output.

**Fixes:** use stable index versions, pin model versions where available, temperature 0 where supported, structured outputs, and regression tests. Temperature 0 does not guarantee identical output across all providers or versions.

**Validate and fail safely:** compare semantic correctness, citation support, and schema validity across repeated runs, not exact string equality alone. On material uncertainty, expose it or abstain rather than hide variability.

## Technique ownership and trade-offs

| Issue | Prompt engineering | Application logic | Retrieval | Model/other |
|---|---|---|---|---|
| Unsupported answer | evidence-only instructions | citation allowlist, abstention contract | relevance and coverage | model quality, human review |
| Irrelevant chunks | ask model to judge evidence carefully | thresholds and observability | chunking, hybrid search, rerank | domain embeddings |
| Wrong format | request JSON | schema validation, bounded retry/error | n/a | provider structured-output support |
| API failure/latency | n/a | timeout, retry policy, circuit breaker | reduce prompt context | local fallback, provider capacity |
| Output variance | constrain response form | versions, repeat checks, state isolation | stable index | pinned model; temperature is not a guarantee |

Higher-quality embeddings/rerankers and larger models may improve quality but add download/storage, compute, cost, and latency. Strict thresholds and abstention reduce unsupported responses but can increase unanswered questions. The current architecture is intentionally small and transparent; production deployment would need authentication, tenant isolation, durable session storage, rate limiting, retention controls, and monitored model/version pinning.
