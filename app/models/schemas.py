from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid


# Ingest models
class IngestRequest(BaseModel):
    doc_id: str = Field(..., description="Unique document identifier")
    text: str = Field(..., description="Document text content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    tenant_id: str = Field(..., description="Tenant identifier")


class IngestResponse(BaseModel):
    doc_id: str
    chunks: int
    trace_id: str


# Query models
class QueryRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    top_k: int = Field(
        default=5, description="Number of top results to return"
    )
    tenant_id: str = Field(..., description="Tenant identifier")


class QueryResponse(BaseModel):
    answer: str
    citations: list
    trace_id: str
    latency_ms: float


# Auth models
class LoginRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    tenant_id: str = Field(..., description="Tenant identifier")


class LoginResponse(BaseModel):
    user_id: str
    tenant_id: str
    exp: int


# Health models
class HealthCheck(BaseModel):
    status: str
    db: str
    redis: str
    latency_ms: float
    version: str = "1.0.0"


# Audit models
class AuditLog(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    action: str
    doc_id: Optional[str] = None
    query: Optional[str] = None
    timestamp: float
    trace_id: str


# Response model for audit list
class AuditLogEntry(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    action: str
    doc_id: Optional[str] = None
    query: Optional[str] = None
    timestamp: float
    trace_id: str