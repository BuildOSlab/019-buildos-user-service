"""
BuildOS User Service
User status and lifecycle schemas.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StatusTransitionRequest(BaseModel):
    """Request to transition a user's account status."""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(min_length=1, max_length=20)
    reason: str | None = Field(default=None, max_length=1000)


class StatusHistoryResponse(BaseModel):
    """Historical user status transition."""

    model_config = ConfigDict(from_attributes=True)

    from_status: str
    to_status: str
    reason: str | None
    actor_id: str | None
    created_at: datetime


class StatusResponse(BaseModel):
    """Current user account status."""

    model_config = ConfigDict(extra="forbid")

    user_id: str
    status: str
    is_active: bool
    status_changed_at: datetime | None = None
    verification: dict[str, str]


class StatusLifecycleResponse(BaseModel):
    """User status together with lifecycle history."""

    model_config = ConfigDict(extra="forbid")

    user_id: str
    status: str
    is_active: bool
    status_changed_at: datetime | None = None
    history: list[StatusHistoryResponse]
