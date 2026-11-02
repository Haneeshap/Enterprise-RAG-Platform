import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def log_slow_query(
    tenant_id: str,
    query: str,
    execution_time_ms: float,
    planning_time_ms: Optional[float] = None,
    trace_id: Optional[str] = None,
    index_used: bool = False,
):
    """Log a slow query (>100ms) to stdout JSON and/or Loki."""
    log_entry = {
        "tenant_id": tenant_id,
        "query": query,
        "execution_time_ms": execution_time_ms,
        "planning_time_ms": planning_time_ms,
        "trace_id": trace_id,
        "index_used": index_used,
    }
    
    # Log to stdout as JSON
    print(json.dumps(log_entry))
    
    # Loki label format (would be sent to Loki in production)
    # labels: {slow_query="true", tenant_id, trace_id}
    # line: json parser {execution_time_ms, query, ...}
    
    logger.info("Slow query logged", extra={"slow_query_data": log_entry})