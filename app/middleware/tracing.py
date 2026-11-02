import time
import uuid
from fastapi import Request, Response
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import Attributes


# Initialize Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

trace_provider = TracerProvider(resource=Resource.create({"service.name": "enterprise-rag"}))
trace.set_tracer_provider(trace_provider)

tracer = trace.get_tracer(__name__)

# Add Jaeger span processor
span_processor = BatchSpanProcessor(jaeger_exporter)
trace_provider.add_span_processor(span_processor)


def get_trace_id() -> str:
    """Get or generate a trace ID."""
    return str(uuid.uuid4())


@staticmethod
def add_span_attributes(span, tenant_id: str = None, user_id: str = None, route: str = None):
    """Add custom attributes to the current span."""
    if tenant_id:
        span.set_attribute("tenant_id", tenant_id)
    if user_id:
        span.set_attribute("user_id", user_id)
    if route:
        span.set_attribute("route", route)


@staticmethod
def get_user_from_request(request: Request) -> str | None:
    """Extract user_id from JWT token in request."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        from app.auth.jwt import get_token_from_request
        token = get_token_from_request(request)
        if token:
            try:
                from jose import JWTError, jwt
                secret = os.getenv("JWT_SECRET", "default-secret")
                payload = jwt.decode(token, secret, algorithms=["HS256"])
                return payload.get("user_id")
            except Exception:
                return None
    return None


async def tracing_middleware(request: Request, call_next):
    # Generate trace_id
    trace_id = get_trace_id()
    request.state.trace_id = trace_id
    
    # Set X-Trace-ID header for response
    request.headers.__dict__["_list"].append(("x-trace-id", trace_id))  # simplified
    
    # Start span
    with tracer.start_as_current_span(
        "http_request",
        attributes={
            "http.method": request.method,
            "http.route": request.url.path,
            "tenant_id": request.state.tenant_id,
            "user_id": get_user_from_request(request),
        },
    ) as span:
        response = await call_next(request)
        
        # Add trace ID to response header
        response.headers["X-Trace-ID"] = trace_id
        
        # Add span attributes
        add_span_attributes(
            span,
            tenant_id=request.state.tenant_id,
            user_id=get_user_from_request(request),
            route=request.url.path,
        )
    
    return response