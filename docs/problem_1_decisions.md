# Problem 1 decisions

## 1. Paragraph-aware bounded chunks

**Choice:** Split on paragraph boundaries, combine adjacent paragraphs up to 900 characters, and use a 120-character overlap when a paragraph or boundary is too large. The app keeps each PDF page separate so citations retain page provenance.

**Alternatives:** fixed token windows or whole pages. Token windows need tokenizer coupling; whole pages can be too large and mix topics. The selected character limits are an explainable starting point, not an optimum. Evaluation will report retrieval failures and support later tuning.

## 2. Local MiniLM embeddings with FAISS

**Choice:** FastEmbed's `sentence-transformers/all-MiniLM-L6-v2` ONNX model produces normalized 384-dimensional local vectors; FAISS `IndexFlatIP` ranks them by cosine similarity. The first use downloads about 0.09 GB, then inference is local.

**Alternatives:** hosted embeddings (document text leaves the machine) or lexical-only search (misses some paraphrases). Local inference protects document text from an embedding service and avoids an API requirement. FAISS exact search is simple for this small assessment dataset; a larger corpus may need an approximate index.

## 3. Retrieval threshold plus lexical baseline

**Choice:** Return the best five vector matches and mark scores below 0.30 as not relevant. This threshold is provisional and cannot prove factual support. A transparent BM25 function is included for the comparison on the same queries.

**Alternatives:** always send top-k regardless of score or add a learned reranker. Top-k alone can force unrelated evidence into the prompt; a reranker adds data and complexity. The evaluation must calibrate the threshold on labeled queries and separately review answer support.

## 4. Citations and conversation state

**Choice:** Stable SHA-256-derived document and chunk IDs, source filename, page, and exact retrieved text travel through the pipeline. The app rejects model citations outside the retrieved chunk set. Session history is in-memory and scoped by session ID; prior user questions may clarify follow-ups, while prior assistant answers are not treated as evidence.

**Alternatives:** global history (cross-session leakage) or persistent accounts (more privacy/security work). In-memory sessions are suitable for a local demonstration but reset on restart and are not multi-user production storage.

## 5. Duplicate and conflicting documents

Exact duplicate PDF/TXT byte streams share a content hash and are skipped. Distinct files with contradictory statements remain separate retrieved evidence; the generation instructions require the model to identify unresolved conflict and cite both. Conflicts are not merged into a single asserted fact. This policy needs tests with explicit conflicting fixture documents.
