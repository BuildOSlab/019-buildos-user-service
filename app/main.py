"""
BuildOS User Service
Application Entry Point
"""

from fastapi import FastAPI

from app.api.internal.router import router as internal_router
from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.logging import configure_logging


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging()

    application = FastAPI(
        title="BuildOS User Service",
        description="Canonical user identity, profile, and account lifecycle management.",
        version="0.1.0",
        debug=settings.debug,
    )

    # Public and v1 APIs
    application.include_router(api_v1_router, prefix="/api/v1")

    # Internal service-to-service APIs
    application.include_router(internal_router, prefix="/internal/v1")

    @application.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        """Basic service health check."""
        return {"status": "ok", "service": settings.service_name}

    return application


app = create_application()
