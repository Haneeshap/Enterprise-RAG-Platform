import json
import aiohttp
from fastapi import Request
from app.middleware.correlation import get_correlation_id


async def send_to_loki(log_entry: dict, loki_url: str = "http://loki:3100/loki/api/v1/push"):
    """Send a log entry to Loki."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(loki_url, json=[log_entry]) as resp:
                return resp.status
    except Exception:
        return 0


def build_log_entry(request: Request, level: str, message: str) -> dict:
    """Build a structured log entry."""
    correlation_id = getattr(request.state, "correlation_id", "")
    tenant_id = getattr(request.state, "tenant_id", "")
    trace_id = getattr(request.state, "trace_id", "")
    
    return {
        "streams": [
            {
                "stream": {
                    "service": "rag-platform",
                    "tenant_id": tenant_id,
                    "trace_id": trace_id,
                    "correlation_id": correlation_id,
                    "level": level,
                },
                "values": [
                    [
                        str(int(time.time() * 1e9)),
                        json.dumps(log_entry),
                    ]
                ],
            }
        ]
    }