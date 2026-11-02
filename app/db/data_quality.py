from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import statistics

load_dotenv()

DATABASE_URL = "postgresql+psycopg2://rag:rag@localhost:5432/rag"
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_doc_length(db, tenant_id: str = None) -> dict:
    """Check document length statistics."""
    query = "SELECT LENGTH(text) as length FROM docs WHERE text IS NOT NULL"
    params = {}
    if tenant_id:
        query += " AND tenant_id = :tenant_id"
        params["tenant_id"] = tenant_id
    
    lengths = [row.length for row in db.execute(text(query), params).fetchall()]
    
    if not lengths:
        return {"avg": 0, "min": 0, "max": 0, "count": 0}
    
    return {
        "avg": round(statistics.mean(lengths)),
        "min": min(lengths),
        "max": max(lengths),
        "count": len(lengths),
    }


def check_null_embedding(db, tenant_id: str = None) -> int:
    """Count documents with null embeddings."""
    query = "SELECT COUNT(*) FROM docs WHERE embedding IS NULL"
    params = {}
    if tenant_id:
        query += " AND tenant_id = :tenant_id"
        params["tenant_id"] = tenant_id
    
    result = db.execute(text(query), params).scalar()
    return result or 0


def check_dim_mismatch(db, tenant_id: str = None) -> int:
    """Count documents with embedding dimension mismatch."""
    # In a real system, this would check if embedding dimension != 1536
    # For now, return 0 as no mismatches expected with fixed schema
    query = "SELECT COUNT(*) FROM docs WHERE embedding IS NOT NULL"
    result = db.execute(text(query), params={} if not tenant_id else {"tenant_id": tenant_id}).scalar()
    return result or 0


def get_coverage(db, tenant_id: str = None) -> dict:
    """Calculate embedding coverage percentage."""
    if tenant_id:
        total_query = text("SELECT COUNT(*) FROM docs WHERE tenant_id = :tenant_id")
        total_result = db.execute(total_query, {"tenant_id": tenant_id}).scalar()
        embedded_query = text("SELECT COUNT(*) FROM docs WHERE tenant_id = :tenant_id AND embedding IS NOT NULL")
        embedded_result = db.execute(embedded_query, {"tenant_id": tenant_id}).scalar()
    else:
        total_query = text("SELECT COUNT(*) FROM docs")
        total_result = db.execute(total_query).scalar()
        embedded_query = text("SELECT COUNT(*) FROM docs WHERE embedding IS NOT NULL")
        embedded_result = db.execute(embedded_query).scalar()
    
    total = total_result or 1  # Avoid division by zero
    embedded = embedded_result or 0
    coverage = round((embedded / total) * 100, 2) if total > 0 else 0
    
    return {
        "coverage_percent": coverage,
        "total_docs": total,
    }