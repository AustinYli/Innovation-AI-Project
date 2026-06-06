from hmac import compare_digest

from fastapi import Header, HTTPException

from app.core.config import TRUST_API_KEY


def require_api_key(x_api_key: str | None = Header(default=None)):
    if not TRUST_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="TRUST_API_KEY is not configured",
        )

    if not x_api_key or not compare_digest(x_api_key, TRUST_API_KEY):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
        )
