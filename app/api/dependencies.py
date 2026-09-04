### `app/api/dependencies.py`

"""
BuildOS User Service
API dependencies and authentication.
"""

from uuid import UUID

import jwt
from fastapi import Header, HTTPException, Security, status
from fastapi.security import (
    APIKeyHeader,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.core.config import settings

api_key_header = APIKeyHeader(
    name="Authorization",
    auto_error=False,
)

bearer_scheme = HTTPBearer(
    auto_error=False,
)

internal_api_key_dependency = Security(api_key_header)
service_id_dependency = Header(
    default=None,
    alias="X-Service-ID",
)
current_user_credentials_dependency = Security(bearer_scheme)


async def verify_internal_service(
    api_key: str | None = internal_api_key_dependency,
    service_id: str | None = service_id_dependency,
) -> bool:
    """Verify service-to-service authentication and service identity."""

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    if not service_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing service identity",
        )

    if api_key.startswith("Bearer "):
        api_key = api_key.removeprefix("Bearer ").strip()

    if api_key != settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if service_id not in settings.allowed_service_ids:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Service identity not allowed",
        )

    return True


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = (
        current_user_credentials_dependency
    ),
) -> UUID:
    """
    Validate an access token issued by the BuildOS Auth Service.

    The User Service does not issue tokens. It only validates the
    Auth Service token and extracts the canonical user UUID from `sub`.
    """

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.auth_jwt_issuer,
            audience=settings.jwt_audience,
            options={
                "require": [
                    "sub",
                    "iss",
                    "aud",
                    "iat",
                    "exp",
                    "jti",
                ],
            },
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return UUID(str(payload["sub"]))
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
