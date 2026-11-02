import os
from fastapi import Request, HTTPException
from sqlalchemy import text
from app.db.postgres import get_db


async def tenant_middleware(request: Request, call_next):
    # Read X-Tenant-ID header
    tenant_id = request.headers.get("X-Tenant-ID", "")
    
    # Set tenant_id in request state
    request.state.tenant_id = tenant_id
    
    # Set Postgres config for tenant isolation
    db = get_db()
    try:
        db.execute(text(f"SET app.tenant_id = '{tenant_id}'"))
        db.commit()
    except Exception:
        pass
    finally:
        db.close()
    
    # Verify tenant_id in JWT matches X-Tenant-ID
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        from app.auth.jwt import verify_jwt
        try:
            payload = verify_jwt(token)
            jwt_tenant_id = payload.get("tenant_id", "")
            if jwt_tenant_id != tenant_id and tenant_id:
                raise HTTPException(status_code=403, detail="JWT tenant_id mismatch with X-Tenant-ID")
        except HTTPException:
            raise
        except Exception:
            pass
    
    response = await call_next(request)
    
    # Clear tenant_id from Postgres
    try:
        db = get_db()
        db.execute(text("RESET app.tenant_id"))
        db.commit()
        db.close()
    except Exception:
        pass
    
    return response