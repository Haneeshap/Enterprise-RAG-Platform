from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import time
import uuid

router = APIRouter(prefix="/health", tags=["health"])

class HealthResponse(BaseModel):
    status: str
    db: str
    redis: str
    latency_ms: float
    version: str = "1.0.0"

@router.get("/", response_model=HealthResponse)
async def health(request: Request):
    start_time = time.time()
    
    # Check Postgres
    from sqlalchemy import text
    from app.db.postgres import get_db
    db_status = "down"
    try:
        db = get_db()
        db.execute(text("SELECT 1"))
        db_status = "up"
        db.close()
    except Exception:
        db_status = "down"
    
    # Check Redis
    import redis as redis_lib
    redis_status = "down"
    try:
        r = redis_lib.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        redis_status = "up"
    except Exception:
        redis_status = "down"
    
    latency_ms = (time.time() - start_time) * 1000
    
    return HealthResponse(
        status="ok",
        db=db_status,
        redis=redis_status,
        latency_ms=latency_ms,
    )