from rag_app.index import LocalVectorIndex


MIN_SIMILARITY = 0.30  # provisional; evaluation must calibrate before claiming quality


def retrieve(index: LocalVectorIndex, query: str, top_k: int = 5) -> list[dict]:
    results = []
    for chunk, score in index.search(query, top_k=top_k):
        result = dict(chunk)
        result["similarity"] = score
        result["relevant"] = score >= MIN_SIMILARITY
        results.append(result)
    return results
