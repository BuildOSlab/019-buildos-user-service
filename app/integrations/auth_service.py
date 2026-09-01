"""
BuildOS User Service
018 Auth Service Integration
"""

from uuid import UUID

import httpx

from app.core.config import settings
from app.core.exceptions import IntegrationError


class AuthServiceClient:
    """Client for communicating with the 018 Auth Service."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float | None = None,
    ) -> None:
        """Initialize the Auth Service client."""
        self.base_url = (
            base_url or settings.auth_service_url
        ).rstrip("/")

        self.api_key = (
            api_key
            if api_key is not None
            else settings.auth_service_api_key
        )

        self.timeout = (
            timeout
            if timeout is not None
            else settings.auth_service_timeout
        )

    def _headers(self) -> dict[str, str]:
        """Build internal service request headers."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Service-ID": settings.service_name,
        }

        if self.api_key:
            headers["X-Internal-API-Key"] = self.api_key

        return headers

    def _url(self, path: str) -> str:
        """Build an Auth Service URL."""
        return f"{self.base_url}/{path.lstrip('/')}"

    async def create_credentials(
        self,
        *,
        user_id: UUID,
        identifier: str,
        password: str,
    ) -> dict:
        """
        Request credential creation from 018.

        019 owns the canonical user.
        018 owns authentication credentials.
        """
        payload = {
            "user_id": str(user_id),
            "identifier": identifier,
            "password": password,
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
            ) as client:
                response = await client.post(
                    self._url("/api/v1/internal/auth/credentials"),
                    json=payload,
                    headers=self._headers(),
                )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            raise IntegrationError(
                "Auth Service rejected credential creation."
            ) from exc

        except httpx.RequestError as exc:
            raise IntegrationError(
                "Unable to reach the Auth Service."
            ) from exc

    async def get_user_status(
        self,
        user_id: UUID,
    ) -> dict:
        """Request authentication status information from 018."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
            ) as client:
                response = await client.get(
                    self._url(
                        f"/api/v1/internal/auth/users/{user_id}/status"
                    ),
                    headers=self._headers(),
                )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            raise IntegrationError(
                "Auth Service rejected the status request."
            ) from exc

        except httpx.RequestError as exc:
            raise IntegrationError(
                "Unable to reach the Auth Service."
            ) from exc

    async def notify_user_deleted(
        self,
        user_id: UUID,
    ) -> None:
        """Notify 018 that a user has been deleted."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
            ) as client:
                response = await client.post(
                    self._url(
                        f"/api/v1/internal/auth/users/{user_id}/deleted"
                    ),
                    headers=self._headers(),
                )

            response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            raise IntegrationError(
                "Auth Service rejected the deletion notification."
            ) from exc

        except httpx.RequestError as exc:
            raise IntegrationError(
                "Unable to reach the Auth Service."
            ) from exc
