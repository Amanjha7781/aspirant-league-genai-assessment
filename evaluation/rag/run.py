from __future__ import annotations

import json
from pathlib import Path

from rag_app.chunking import chunk_document
from rag_app.index import LocalVectorIndex, bm25_search
from rag_app.loaders import parse_document
from shared.llm import LLMClient


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = ROOT / "samples" / "rag"
OUT_DIR = ROOT / "evaluation" / "rag"


def score_retriever(queries: list[dict], ranked: list[list[dict]], k: int) -> dict[str, float]:
    hit = coverage = precision = 0.0
    answerable = answerable_hit = 0
    for query, results in zip(queries, ranked):
        expected = set(query["expected_sources"])
        actual = [item["filename"] for item in results[:k]]
        if expected and expected.intersection(actual):
            hit += 1
        if expected:
            coverage += len(expected.intersection(actual)) / len(expected)
            answerable += 1
            answerable_hit += int(bool(expected.intersection(actual)))
        precision += sum(filename in expected for filename in actual) / k
    n = max(len(queries), 1)
    return {"source_hit_rate_at_5": round(hit / n, 4), "answerable_query_source_hit_rate_at_5": round(answerable_hit / max(answerable, 1), 4), "expected_source_coverage_at_5": round(coverage / n, 4), "chunk_precision_at_5": round(precision / n, 4)}


def main() -> None:
    index = LocalVectorIndex(OUT_DIR / ".local_index")
    for path in sorted(SAMPLE_DIR.glob("*")):
        if path.suffix.lower() not in {".txt", ".pdf"}:
            continue
        parsed = parse_document(path.name, path.read_bytes())
        index.add_documents(chunk_document(parsed))
    queries = json.loads((SAMPLE_DIR / "evaluation_queries.json").read_text("utf-8"))
    semantic_rows, lexical_rows, records = [], [], []
    for query in queries:
        semantic = [{**chunk, "score": score} for chunk, score in index.search(query["query"], top_k=5)]
        lexical = [{**chunk, "score": score} for chunk, score in bm25_search(query["query"], index.chunks, top_k=5)]
        semantic_rows.append(semantic)
        lexical_rows.append(lexical)
        records.append({"id": query["id"], "query": query["query"], "expected_sources": query["expected_sources"], "expected_abstention": query["expected_abstention"], "expected_conflict": query.get("expected_conflict", False), "semantic_top5": semantic, "bm25_top5": lexical})
    llm = LLMClient()
    result = {
        "dataset": "hand-labeled synthetic building-policy examples",
        "queries": len(queries),
        "k": 5,
        "denominators": {"source_hit_rate_at_5": f"all {len(queries)} queries; abstention queries count as no source hit", "answerable_query_source_hit_rate_at_5": f"{sum(bool(query['expected_sources']) for query in queries)} queries with expected supporting sources", "expected_source_coverage_at_5": "macro average over expected source names per query; zero when none expected", "chunk_precision_at_5": f"all {len(queries)} queries times 5 slots, including missing slots as incorrect"},
        "semantic": score_retriever(queries, semantic_rows, 5),
        "bm25": score_retriever(queries, lexical_rows, 5),
        "similarity_gate_rate_on_expected_abstentions": round(sum(bool(row) and row[0]["score"] >= 0.30 for query, row in zip(queries, semantic_rows) if query["expected_abstention"]) / max(sum(query["expected_abstention"] for query in queries), 1), 4),
        "answer_support_review": "BLOCKED - no LLM endpoint configured; this script measured retrieval only",
        "unavailable_answer_behavior": "NOT RUN - requires a real configured LLM; retrieval results for abstention-labeled queries are preserved below",
        "llm_configured": llm.configured,
        "results": records,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"queries": len(queries), "semantic": result["semantic"], "bm25": result["bm25"], "answer_support_review": result["answer_support_review"], "output": "evaluation/rag/raw_results.json"}, indent=2))


if __name__ == "__main__":
    main()
