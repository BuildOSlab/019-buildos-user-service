"""
BuildOS User Service
Application Configuration
"""

from functools import lru_cache

from pydantic import model_validator
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

    allowed_service_ids: list[str] = [
        "buildos-auth-service",
        "buildos-018-auth-service",
    ]

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

    auth_service_internal_url: str = "http://localhost:8018"
    auth_service_internal_api_key: str = "change-me-in-production"

    # ------------------------------------------------------------------
    # Event Broker
    # ------------------------------------------------------------------

    event_broker_url: str | None = None
    event_broker_enabled: bool = False

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Reject insecure configuration in production."""

        if self.environment.lower() != "production":
            return self

        placeholder = "change-me-in-production"

        sensitive_settings = {
            "internal_api_key": self.internal_api_key,
            "jwt_secret_key": self.jwt_secret_key,
            "auth_service_internal_api_key": (
                self.auth_service_internal_api_key
            ),
        }

        for name, value in sensitive_settings.items():
            if value == placeholder:
                raise ValueError(
                    f"Default {name} used in production!"
                )

        service_urls = {
            "auth_service_url": self.auth_service_url,
            "auth_service_internal_url": self.auth_service_internal_url,
        }

        for name, url in service_urls.items():
            if not url.lower().startswith("https://"):
                raise ValueError(
                    f"{name} must use HTTPS in production"
                )

        return self

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
