from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from jose import JWTError, jwt
import time

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    user_id: str
    tenant_id: str

class LoginResponse(BaseModel):
    user_id: str
    tenant_id: str
    exp: int

@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    # Create JWT token
    import os
    secret = os.getenv("JWT_SECRET", "default-secret-change-in-production")
    
    exp = int(time.time()) + 3600  # 1 hour
    token = jwt.encode(
        {"user_id": payload.user_id, "tenant_id": payload.tenant_id, "exp": exp},
        secret,
        algorithm="HS256",
    )
    
    auth_success_total.labels(tenant_id=payload.tenant_id).inc()
    
    return LoginResponse(user_id=payload.user_id, tenant_id=payload.tenant_id, exp=exp)