import os
import time
from jose import JWTError, jwt
from fastapi import Request, Response

JWT_SECRET = os.getenv("JWT_SECRET", "default-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_SECONDS = 3600  # 1 hour


def create_jwt(user_id: str, tenant_id: str) -> str:
    """Create a JWT HS256 token."""
    exp = int(time.time()) + JWT_EXPIRY_SECONDS
    to_encode = {"user_id": user_id, "tenant_id": tenant_id, "exp": exp}
    encoded = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded


def verify_jwt(token: str) -> dict:
    """Verify a JWT token and return the payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid JWT: {str(e)}")


def decode(token: str) -> dict:
    """Decode a JWT token without verification (for internal use)."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return {}


def get_token_from_request(request: Request) -> str | None:
    """Extract Bearer token from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None