from __future__ import annotations

import json
import os
import threading
from pathlib import Path

import faiss
import numpy as np

from rag_app.chunking import Chunk
from rag_app.embeddings import embed_texts


class LocalVectorIndex:
    """Small persistent FAISS inner-product index; embeddings are L2-normalized."""

    def __init__(self, directory: str | Path, dimension: int = 384) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.index_path = self.directory / "chunks.faiss"
        self.metadata_path = self.directory / "chunks.json"
        self.dimension = dimension
        self.lock = threading.RLock()
        self.index = faiss.read_index(str(self.index_path)) if self.index_path.exists() else faiss.IndexFlatIP(dimension)
        self.chunks: list[dict] = json.loads(self.metadata_path.read_text("utf-8")) if self.metadata_path.exists() else []
        if self.index.ntotal != len(self.chunks):
            raise RuntimeError("Persisted vector index and metadata counts do not match.")

    def add_documents(self, chunks: list[Chunk]) -> tuple[int, list[str]]:
        known_documents = {item["document_id"] for item in self.chunks}
        new_chunks = []
        duplicates = set()
        for chunk in chunks:
            if chunk.document_id in known_documents:
                duplicates.add(chunk.document_id)
            else:
                new_chunks.append(chunk)
                known_documents.add(chunk.document_id)
        if not new_chunks:
            return 0, duplicates
        vectors = embed_texts([chunk.text for chunk in new_chunks])
        with self.lock:
            self.index.add(vectors)
            self.chunks.extend(chunk.as_dict() for chunk in new_chunks)
            faiss.write_index(self.index, str(self.index_path))
            temp = self.metadata_path.with_suffix(".json.tmp")
            temp.write_text(json.dumps(self.chunks, ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(temp, self.metadata_path)
        return len(new_chunks), sorted(duplicates)

    def search(self, query: str, top_k: int = 5) -> list[tuple[dict, float]]:
        if not self.chunks:
            return []
        vector = embed_texts([query])
        with self.lock:
            scores, indices = self.index.search(vector, min(top_k, len(self.chunks)))
        output = []
        for score, position in zip(scores[0], indices[0]):
            if position >= 0:
                output.append((self.chunks[int(position)], float(score)))
        return output


def bm25_search(query: str, chunks: list[dict], top_k: int = 5) -> list[tuple[dict, float]]:
    """Tiny transparent BM25 baseline used for an apples-to-apples evaluation."""
    import math
    import re
    from collections import Counter

    tokens = lambda text: re.findall(r"[a-z0-9]+", text.casefold())
    query_terms = tokens(query)
    documents = [tokens(chunk["text"]) for chunk in chunks]
    if not query_terms or not documents:
        return []
    doc_freq = Counter(term for term in set(query_terms) for doc in documents if term in doc)
    lengths = [len(doc) for doc in documents]
    avg_len = sum(lengths) / max(len(lengths), 1)
    scored = []
    for item, terms, length in zip(chunks, documents, lengths):
        counts = Counter(terms)
        score = 0.0
        for term in query_terms:
            if not counts[term]:
                continue
            idf = math.log(1 + (len(documents) - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
            denom = counts[term] + 1.2 * (1 - 0.75 + 0.75 * length / max(avg_len, 1))
            score += idf * counts[term] * 2.2 / denom
        scored.append((item, score))
    return sorted(scored, key=lambda pair: pair[1], reverse=True)[:top_k]
