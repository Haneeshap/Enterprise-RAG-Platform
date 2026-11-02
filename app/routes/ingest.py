from fastapi import APIRouter, Request
from pydantic import BaseModel
import tiktoken
import time
import uuid
from sqlalchemy import text
from app.db.postgres import get_db

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestRequest(BaseModel):
    doc_id: str
    text: str
    metadata: dict
    tenant_id: str


class IngestResponse(BaseModel):
    doc_id: str
    chunks: int
    trace_id: str


@router.post("/", response_model=IngestResponse)
async def ingest(request: Request, payload: IngestRequest):
    tenant_id = request.state.tenant_id
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(payload.text)
    chunk_size = 500
    overlap = 50
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    embedding = [0.1] * 1536
    num_chunks = len(chunks)
    trace_id = getattr(request.state, "trace_id", "unknown")
    db = get_db()
    try:
        for i, chunk_text in enumerate(chunks):
            chunk_id = hash(chunk_text) % 10000
            db.execute(
                text(
                    "INSERT INTO docs (id, tenant_id, doc_id, chunk_id, text, embedding, metadata, created_at) "
                    "VALUES (:id, :tenant_id, :doc_id, :chunk_id, :text, :embedding, :metadata, :created_at)"
                ),
                {
                    "id": str(uuid4()),
                    "tenant_id": tenant_id,
                    "doc_id": payload.doc_id,
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "embedding": embedding,
                    "metadata": payload.metadata,
                    "created_at": time.time(),
                },
            )
    finally:
        db.close()
    return IngestResponse(doc_id=payload.doc_id, chunks=num_chunks, trace_id=trace_id)