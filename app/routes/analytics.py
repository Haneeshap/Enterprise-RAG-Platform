from fastapi import APIRouter, Request
from prometheus_client import Histogram
import time

from app.db.postgres import get_db
from app.logging.slow_query import log_slow_query

router = APIRouter(prefix="/analytics", tags=["analytics"])

latency_histogram = Histogram("analytics_latency_ms", "Analytics query latency in ms")


@router.get("/window")
async def window_query(request: Request):
    """Run window analytics queries on audit logs."""
    from fastapi import Request
    from sqlalchemy import text as sql_text
    from app.db.postgres import get_db
    
    tenant_id = request.query_params.get("tenant_id", "")
    query_type = request.query_params.get("type", "last_7_days_top_docs")
    
    db = get_db()
    try:
        start_time = time.time()
        
        if query_type == "last_7_days_top_docs":
            result = db.execute(
                sql_text(
                    "SELECT doc_id, COUNT(*) as query_count "
                    "FROM audit_logs WHERE action='query' "
                    "AND tenant_id = :tenant_id "
                    "AND timestamp > NOW() - INTERVAL '7 days' "
                    "GROUP BY doc_id ORDER BY COUNT DESC LIMIT 10"
                ),
                {"tenant_id": tenant_id if tenant_id else ""}
            ).fetchall()
            results = [{"doc_id": row.doc_id, "queries": row.query_count} for row in result]
        
        elif query_type == "top_queries":
            result = db.execute(
                sql_text(
                    "SELECT query, COUNT(*) as query_count "
                    "FROM audit_logs WHERE action='query' "
                    f"{'AND tenant_id = :tenant_id ' if tenant_id else ''}"
                    "GROUP BY query ORDER BY COUNT DESC LIMIT 10"
                ),
                {"tenant_id": tenant_id if tenant_id else ""}
            ).fetchall()
            results = [{"query": row.query, "queries": row.query_count} for row in result]
        
        elif query_type == "latency_p95":
            result = db.execute(
                sql_text(
                    "SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_ms) "
                    "FROM audit_logs WHERE action='query' "
                    f"{'AND tenant_id = :tenant_id ' if tenant_id else ''}"
                ),
                {"tenant_id": tenant_id if tenant_id else ""}
            ).scalar()
            results = {"p95_latency_ms": float(result) if result else 0}
        
        elif query_type == "error_rate":
            result = db.execute(
                sql_text(
                    "SELECT (COUNT(*) FILTER WHERE status='error')::float / NULLIF(COUNT(), 0) "
                    "FROM audit_logs "
                    f"{'AND tenant_id = :tenant_id ' if tenant_id else ''}"
                ),
                {"tenant_id": tenant_id if tenant_id else ""}
            ).scalar()
            results = {"error_rate": float(result) if result else 0.0}
        
        elif query_type == "tenant_usage":
            result = db.execute(
                sql_text(
                    "SELECT tenant_id, COUNT(*) as queries, COUNT(DISTINCT doc_id) as docs "
                    "FROM audit_logs WHERE action='query' "
                    f"GROUP BY tenant_id "
                )
            ).fetchall()
            results = [
                {"tenant_id": row.tenant_id, "queries": row.queries, "docs": row.docs}
                for row in result
            ]
        
        else:
            results = {"error": f"Unknown query type: {query_type}"}
        
        latency_ms = (time.time() - start_time) * 1000
        latency_histogram.observe(latency_ms)
        
        return {
            "query_type": query_type,
            "results": results,
            "latency_ms": round(latency_ms, 2),
            "trace_id": request.headers.get("X-Trace-ID", "unknown"),
        }
    
    except Exception as e:
        return {
            "query_type": query_type,
            "results": {"error": str(e)},
            "latency_ms": 0,
            "trace_id": request.headers.get("X-Trace-ID", "unknown"),
        }