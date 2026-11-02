import time
from typing import List, Dict, Any, Optional
from sqlalchemy import text as sql_text
from app.db.postgres import get_db


def hybrid_search(
    query_embedding: List[float],
    query_text: str,
    tenant_id: str,
    top_k: int = 5,
    alpha: float = 0.7,
) -> Dict[str, Any]:
    start_time = time.time()
    db = get_db()
    try:
        vector_results = db.execute(
            sql_text(
                "SELECT text, doc_id, chunk_id, metadata, "
                "1 - (embedding <=> :query_embedding) as vector_score "
                "FROM docs WHERE tenant_id = :tenant_id "
                "ORDER BY vector_score DESC LIMIT 20"
            ),
            {"query_embedding": query_embedding, "tenant_id": tenant_id},
        ).fetchall()
        bm25_results = db.execute(
            sql_text(
                "SELECT text, doc_id, chunk_id, metadata, "
                "ts_rank(to_tsvector(text), plainto_tsquery(:query_text)) as bm25_score "
                "FROM docs WHERE tenant_id = :tenant_id "
                "AND to_tsvector(text) @@ plainto_tsquery(:query_text) "
                "ORDER BY bm25_score DESC LIMIT 20"
            ),
            {"query_text": query_text, "tenant_id": tenant_id},
        ).fetchall()
        bm25_scores = [float(r.bm25_score) for r in bm25_results]
        if bm25_scores:
            min_score = min(bm25_scores)
            max_score = max(bm25_scores)
            normalized_bm25 = [
                (s - min_score) / (max_score - min_score + 1e-10) if max_score > min_score else 0.0
                for s in bm25_scores
            ]
        else:
            normalized_bm25 = []
        merged: Dict[str, Dict[str, Any]] = {}
        for r in vector_results:
            key = f"{r.tenant_id}_{r.doc_id}_{r.chunk_id}"
            if key not in merged:
                merged[key] = {
                    "doc_id": r.doc_id,
                    "chunk_id": r.chunk_id,
                    "text": r.text,
                    "vector_score": float(r.vector_score),
                    "bm25_score": 0.0,
                    "hybrid_score": 0.0,
                }
            merged[key]["vector_score"] = float(r.vector_score)
        for i, r in enumerate(bm25_results):
            key = f"{r.tenant_id}_{r.doc_id}_{r.chunk_id}"
            if key in merged:
                merged[key]["bm25_score"] = normalized_bm25[i] if i < len(normalized_bm25) else 0.0
                merged[key]["hybrid_score"] = (
                    alpha * merged[key]["vector_score"] 
                    + (1 - alpha) * normalized_bm25[i]
                )
            else:
                merged[key] = {
                    "doc_id": r.doc_id,
                    "chunk_id": r.chunk_id,
                    "text": r.text,
                    "vector_score": 0.0,
                    "bm25_score": normalized_bm25[i] if i < len(normalized_bm25) else 0.0,
                    "hybrid_score": (1 - alpha) * normalized_bm25[i] 
                    if normalized_bm25 and i < len(normalized_bm25)
                    else 0.0,
                }
        sorted_results = sorted(merged.values(), key=lambda x: x["hybrid_score"], reverse=True)
        final_results = sorted_results[:top_k]
        latency_ms = (time.time() - start_time) * 1000
        return {
            "results": final_results,
            "latency_ms": latency_ms,
            "vector_search_count": len(vector_results),
            "bm25_search_count": len(bm25_results),
            "alpha": alpha,
        }
    except Exception as e:
        raise Exception(f"Hybrid search error: {str(e)}")