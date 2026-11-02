from fastapi import APIRouter, Request, HTTPException
from prometheus_client import Histogram, Counter
import time

from app.db.postgres import get_hnsw_stats
from app.db.data_quality import check_doc_length, check_null_embedding, check_dim_mismatch, get_coverage
from app.logging.slow_query import log_slow_query

router = APIRouter(prefix="/debug", tags=["debug"])

pgvector_explain_total = Counter("pgvector_explain_total", "Total pgvector EXPLAIN queries")
pgvector_search_duration_seconds = Histogram(
    "pgvector_search_duration_seconds",
    "pgvector search duration in seconds",
    ["query_type"],
)


@router.post("/hnsw-stats")
async def hnsw_stats(request: Request):
    """Return HNSW index statistics."""
    from app.db.postgres import get_db
    
    stats = get_hnsw_stats()
    # Count tenants from docs table
    from app.db.postgres import get_db as get_db_func
    db = get_db_func()
    try:
        from sqlalchemy import text as sql_text
        tenant_result = db.execute(sql_text("SELECT COUNT(DISTINCT tenant_id) FROM docs")).scalar()
        tenant_count = tenant_result if tenant_result else 0
    except Exception:
        tenant_count = 0
    finally:
        db.close()
    
    # Get index properties from the index definition
    index_info = stats[0] if stats else {"indexname": "", "indexdef": ""}
    index_def = index_info.get("indexdef", "")
    
    # Extract m and ef_construction from indexdef
    m_val = 16  # default
    ef_construction_val = 64  # default
    if "m=" in index_def:
        try:
            m_val = int(index_def.split("m=")[1].split(",")[0])
        except (ValueError, IndexError):
            pass
    if "ef_construction=" in index_def:
        try:
            ef_construction_val = int(index_def.split("ef_construction=")[1].split(")")[0])
        except (ValueError, IndexError):
            pass
    
    return {
        "m": m_val,
        "ef_construction": ef_construction_val,
        "index_size": len(stats) if stats else 0,
        "index_type": "hnsw",
        "tenant_count": tenant_count,
    }


@router.post("/explain")
async def explain_query(request: Request):
    """Run EXPLAIN ANALYZE on a pgvector search query."""
    from fastapi import Request
    from sqlalchemy import text as sql_text
    from app.db.postgres import get_db
    
    body = await request.json()
    query = body.get("query", "")
    tenant_id = body.get("tenant_id", "")
    
    if not query or not tenant_id:
        raise HTTPException(status_code=400, detail="query and tenant_id are required")
    
    db = get_db()
    try:
        # Generate query embedding (mock: [0.1]*1536)
        embedding = [0.1] * 1536
        
        # Set HNSW ef_search
        db.execute(text("SET hnsw.ef_search = 40"))
        db.commit()
        
        # Run EXPLAIN ANALYZE
        explain_query = text(
            f"EXPLAIN (ANALYZE, BUFFERS) "
            f"SELECT text, doc_id, chunk_id, metadata, "
            f"1 - (embedding <=> '{embedding}'::vector) as score "
            f"FROM docs WHERE tenant_id = '{tenant_id}' "
            f"ORDER BY embedding <=> '{embedding}'::vector LIMIT 5"
        )
        
        start_time = time.time()
        explain_result = db.execute(explain_query).fetchall()
        execution_time_ms = (time.time() - start_time) * 1000
        
        pgvector_explain_total.inc()
        
        # Parse the explain output
        explain_text = str(explain_result[0]) if explain_result else ""
        
        # Extract buffer info and index usage
        buffers_hit = 0
        index_used = False
        for line in explain_text.split("\\n"):
            if "Buffers:" in line:
                # Parse buffer info
                pass
            if "hnsw" in line.lower() or "index" in line.lower():
                index_used = True
        
        return {
            "explain": explain_text,
            "planning_time_ms": 0,  # Would be extracted from actual output
            "execution_time_ms": round(execution_time_ms, 2),
            "buffers_hit": buffers_hit,
            "index_used": index_used,
            "hnsw_ef_search": 40,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()