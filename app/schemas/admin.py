"""
BuildOS User Service
Administrative API schemas.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminUserUpdateRequest(BaseModel):
    """Explicitly allowed administrative user updates."""

    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, max_length=100)


class AdminStatusUpdateRequest(BaseModel):
    """Administrative request to change account status."""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(min_length=1, max_length=20)
    reason: str | None = Field(default=None, max_length=1000)


class AdminUserResponse(BaseModel):
    """Administrative user representation."""

    model_config = ConfigDict(from_attributes=True)

    public_id: str
    status: str
    display_name: str | None
    last_active_at: datetime | None
    deactivated_at: datetime | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime
