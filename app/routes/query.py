from fastapi import APIRouter, Request
from pydantic import BaseModel
import tiktoken
import time
import uuid
from sqlalchemy import text
from app.db.postgres import get_db

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    tenant_id: str


class QueryResponse(BaseModel):
    answer: str
    citations: list
    trace_id: str
    latency_ms: float


@router.post("/", response_model=QueryResponse)
async def query(
    request: Request,
    payload: QueryRequest,
):
    start_time = time.time()
    tenant_id = request.state.tenant_id

    # Generate query embedding
    encoding = tiktoken.get_encoding("cl100k_base")
    query_tokens = encoding.encode(payload.query)
    # mock embedding
    embedding = [0.1] * 1536

    # Search pgvector cosine similarity
    db = get_db()
    try:
        result = db.execute(
            text(
                "SELECT text, doc_id, chunk_id, metadata, "
                "1 - (embedding <=> :query_embedding) as score "
                "FROM docs WHERE tenant_id = :tenant_id "
                "ORDER BY score DESC LIMIT :top_k"
            ),
            {"query_embedding": embedding, "tenant_id": tenant_id, "top_k": payload.top_k},
        ).fetchall()
    finally:
        db.close()

    latency_ms = (time.time() - start_time) * 1000

    # Build citations
    citations = []
    for row in result:
        citations.append({
            "doc_id": row.doc_id,
            "chunk_id": row.chunk_id,
            "text": row.text,
            "score": float(row.score),
        })

    # Mock answer based on top 3 chunks
    top_citations = citations[:3]
    citation_texts = [c["text"][:50] + "..." for c in top_citations]
    answer = f"Answer based on {len(top_citations)} chunks: {' '.join(citation_texts)}"

    trace_id = getattr(request.state, "trace_id", "unknown")

    return QueryResponse(
        answer=answer,
        citations=citations,
        trace_id=trace_id,
        latency_ms=latency_ms,
    )