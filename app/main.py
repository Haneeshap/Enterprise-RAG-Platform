from fastapi import FastAPI, Request, middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.routes.ingest import router as ingest_router
from app.routes.query import router as query_router
from app.routes.health import router as health_router
from app.routes.metrics import router as metrics_router
from app.routes.auth import router as auth_router
from app.routes.debug import router as debug_router
from app.routes.analytics import router as analytics_router
from app.middleware.tenant import tenant_middleware
from app.middleware.tracing import tracing_middleware

import os

app = FastAPI(
    title="Enterprise RAG Platform",
    version="1.0.0",
    description="FastAPI backend with JWT auth, tenant isolation, OTEL tracing, and Prometheus metrics",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "*").split(","),
)

# Prometheus middleware (adds http_request_duration_seconds and http_requests_total)


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    from prometheus_client import Histogram, Counter

    http_requests_total.labels(
        method=request.method, route=request.url.path, status="200"
    ).inc()

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    http_request_duration_seconds.labels(
        method=request.method, route=request.url.path, status=str(response.status_code)
    ).observe(duration)

    return response

# Include routers
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(metrics_router)
app.include_router(debug_router)
app.include_router(analytics_router)

# Tenant middleware (must be after router inclusion)


@app.middleware("http")
async def tenant_middleware_func(request: Request, call_next):
    from app.middleware.tenant import tenant_middleware as tm

    return await tm(request, call_next)

# Health check endpoint


@app.get("/health", include_in_schema=False)
async def health(request: Request):
    from sqlalchemy import text
    from app.db.postgres import get_db
    import redis as redis_lib
    import time

    start_time = time.time()

    # Check Postgres
    db_status = "down"
    try:
        db = get_db()
        db.execute(text("SELECT 1"))
        db_status = "up"
        db.close()
    except Exception:
        db_status = "down"

    # Check Redis
    redis_status = "down"
    try:
        r = redis_lib.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        redis_status = "up"
    except Exception:
        redis_status = "down"

    latency_ms = (time.time() - start_time) * 1000

    return {
        "status": "ok",
        "db": db_status,
        "redis": redis_status,
        "latency_ms": latency_ms,
        "version": "1.0.0",
    }


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Enterprise RAG Platform API", "version": "1.0.0"}