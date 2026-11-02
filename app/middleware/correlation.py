import time
import uuid
import json
import logging
from fastapi import Request, Response

logger = logging.getLogger("rag-platform")


def get_correlation_id(request: Request) -> str:
    """Get or generate correlation ID."""
    correlation_id = request.headers.get("X-Correlation-ID", "")
    if not correlation_id:
        correlation_id = uuid.uuid4().hex
    return correlation_id


async def correlation_middleware(request: Request, call_next):
    """Middleware to add correlation IDs and structured logging."""
    correlation_id = get_correlation_id(request)
    trace_id = getattr(request.state, "trace_id", "")
    
    request.state.correlation_id = correlation_id
    
    response = await call_next(request)
    
    # Set correlation ID response header
    response.headers["X-Correlation-ID"] = correlation_id
    
    # Log the request
    log_data = {
        "timestamp": time.time(),
        "level": "INFO",
        "service": "rag-platform",
        "tenant_id": getattr(request.state, "tenant_id", ""),
        "trace_id": trace_id,
        "correlation_id": correlation_id,
        "message": f"{request.method} {request.url.path}",
        "latency_ms": response.headers.get("X-Process-Time", 0),
        "route": request.url.path,
    }
    
    logger.info("Request processed", extra=log_data)
    
    return response