"""
BuildOS User Service
Security Utilities
"""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(
    name="Authorization",
    auto_error=False,
)


async def verify_internal_api_key(
    api_key: str | None = Security(api_key_header),
) -> bool:
    """Verify that the request contains a valid internal API key."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    if api_key.startswith("Bearer "):
        api_key = api_key.removeprefix("Bearer ").strip()

    if api_key != settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return True
