import json
import time
import uuid
from fastapi import APIRequest, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from app.db.postgres import get_db
from app.cost.tracking import calculate_cost

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def stream_chat(request: Request):
    """SSE streaming chat endpoint."""
    body = await request.json()
    query = body.get("query", "")
    tenant_id = body.get("tenant_id", "tenant1")
    trace_id = body.get("trace_id", str(uuid.uuid4()))

    db = get_db()
    try:
        # Set HNSW ef_search for better search quality
        db.execute(text("SET hnsw.ef_search = 40"))
        db.commit()

        # Calculate embedding cost (mock: $0.00002 per 1k tokens for 1536d)
        embedding_tokens = 100  # mock embedding token count
        embedding_cost = (embedding_tokens / 1000) * 0.00002

        # Mock LLM streaming - simulate token generation
        # In production, this would call an LLM API like OpenAI
        llm_tokens = 150  # mock generated tokens
        llm_cost = (llm_tokens / 1000) * 0.01

        total_cost = embedding_cost + llm_cost

        # Mock chunk text for citations
        mock_chunks = [
            {"doc_id": "doc1", "chunk": 0, "text": "Machine learning is a subset of AI.", "score": 0.95},
            {"doc_id": "doc2", "chunk": 1, "text": "Neural networks process data through layers.", "score": 0.87},
        ]

        async def event_stream():
            # Send trace_id immediately
            yield f"data: {json.dumps({'type': 'trace_id', 'trace_id': trace_id})}\n\n"

            # Simulate streaming tokens
            mock_answer = "Answer based on the context provided. The document discusses machine learning concepts including neural networks and deep learning architectures."
            words = mock_answer.split()

            for i, word in enumerate(words):
                # Calculate cumulative cost as we stream
                current_cost = embedding_cost + (llm_cost * (i / len(words)))
                yield f"data: {json.dumps({'type': 'token', 'token': word})}\n\n"
                await asyncio.sleep(0.02)  # Simulate streaming delay

                # Yield citation every ~3 tokens
                if i % 3 === 0 and i > 0:
                    citation = mock_chunks[i % len(mock_chunks)]
                    yield f"data: {json.dumps({'type': 'citation', 'doc_id': citation['doc_id'], 'chunk': citation['chunk'], 'text': citation['text'], 'score': citation['score']})}\n\n"

            # Send done event with final metadata
            yield f"data: {json.dumps({'type': 'done', 'trace_id': trace_id, 'cost': round(total_cost, 6), 'latency': 150, 'cache_hit': False})}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))