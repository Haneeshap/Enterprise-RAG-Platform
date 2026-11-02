from fastapi import APIRequest, HTTPException, Request
from prometheus_client import Histogram, Counter
from app.cost.tracking import calculate_cost, cost_tracker, get_cost_summary, get_cost_breakdown_summary


router = APIRouter(prefix="/cost", tags=["cost"])

cost_per_1k_queries_gauge = Gauge(
    "cost_per_1k_queries",
    "Cost per 1,000 queries in USD",
    ["tenant_id"],
)

cost_per_query_histogram = Histogram(
    "cost_per_query_histogram",
    "Cost per individual query in USD",
    ["tenant_id"],
)

cost_breakdown_gauge = Gauge(
    "cost_breakdown",
    "Cost breakdown by type",
    ["tenant_id", "type"],
)

cache_hit_rate_gauge = Gauge(
    "cache_hit_rate",
    "Cache hit rate percentage",
    ["tenant_id"],
)

cost_saved_total = Counter(
    "cost_saved_total",
    "Total cost saved via cache hits",
    ["tenant_id"],
)


@router.get("/")
async def cost_root():
    """Cost root endpoint."""
    return {"message": "Cost tracking API endpoint"}


@router.get("/")