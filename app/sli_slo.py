"""Service Level Indicators and Objectives for Enterprise RAG Platform."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SLI:
    """Service Level Indicator metrics."""
    name: str
    description: str
    metric_name: str
    target: float  # e.g., 0.5 for 500ms, 0.999 for 99.9%
    window: str = "5m"


@dataclass
class SLO:
    """Service Level Objective derived from SLIs."""
    name: str
    sli: SLI
    error_budget: float  # e.g., 0.001 for 0.1%
    availability_target: float  # e.g., 99.9


# Define SLIs for the RAG platform
LATENCY_P95_SLI = SLI(
    name="latency_p95",
    description="95th percentile request latency",
    metric_name="request_latency_seconds_p95",
    target=0.5,  # 500ms
)

AVAILABILITY_SLI = SLI(
    name="availability",
    description="Request success rate",
    metric_name="request_success_rate",
    target=0.999,  # 99.9%
)

THROUGHPUT_SLI = SLI(
    name="throughput",
    description="Requests per second",
    metric_name="requests_per_second",
    target=None,
)

# Define SLOs
RAG_SLO = SLO(
    name="rag_platform_slo",
    sli=LATENCY_P95_SLI,
    error_budget=0.001,  # 0.1%
    availability_target=0.999,  # 99.9%
)