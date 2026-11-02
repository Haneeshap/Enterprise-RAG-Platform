from fastapi import APIRouter, Request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

router = APIRouter(prefix="/metrics", tags=["metrics"])

# Prometheus metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "route", "status"],
)

auth_success_total = Counter("auth_success_total", "Total authentication successes", ["tenant_id"])
auth_failure_total = Counter("auth_failure_total", "Total authentication failures", ["tenant_id"])

ingest_total = Counter("ingest_total", "Total ingest operations", ["tenant_id"])
query_total = Counter("query_total", "Total query operations", ["tenant_id"])


@router.get("/", include_in_schema=False)
async def metrics(request: Request):
    # Record metrics before generating response
    # In a real app, we'd use middleware; here we just expose the metrics
    output = generate_latest()
    return Response(
        content=output,
        media_type=CONTENT_TYPE_LATEST,
    )