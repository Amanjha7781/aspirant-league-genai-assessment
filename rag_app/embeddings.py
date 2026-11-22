from __future__ import annotations

import os
from functools import lru_cache

import numpy as np
from fastembed import TextEmbedding


@lru_cache(maxsize=1)
def _model() -> TextEmbedding:
    return TextEmbedding(model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))


def embed_texts(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.empty((0, 384), dtype="float32")
    vectors = np.asarray(list(_model().embed(texts)), dtype="float32")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.maximum(norms, 1e-12)
