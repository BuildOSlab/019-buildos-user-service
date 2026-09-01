"""
BuildOS User Service
Application Configuration
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the User Service."""

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    service_name: str = "buildos-user-service"
    environment: str = "development"
    debug: bool = False

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_url: str = (
        "postgresql+psycopg2://gerald@localhost:5432/buildos_user"
    )

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    internal_api_key: str = "change-me-in-production"

    # ------------------------------------------------------------------
    # JWT
    # ------------------------------------------------------------------

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"

    jwt_issuer: str = "buildos-user-service"
    auth_jwt_issuer: str = "buildos-auth-service"
    
    jwt_audience: str = "buildos-api"

    # ------------------------------------------------------------------
    # User IDs
    # ------------------------------------------------------------------

    public_id_prefix: str = "usr"

    # ------------------------------------------------------------------
    # 018 Auth Service Integration
    # ------------------------------------------------------------------

    auth_service_url: str = "http://localhost:8018"
    auth_service_api_key: str | None = None
    auth_service_timeout: float = 5.0

    # ------------------------------------------------------------------
    # Event Broker
    # ------------------------------------------------------------------

    event_broker_url: str | None = None
    event_broker_enabled: bool = False

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


settings = get_settings()
