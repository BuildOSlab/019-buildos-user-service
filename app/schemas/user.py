"""
BuildOS User Service
User API schemas.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserCreateRequest(BaseModel):
    """Internal request to create a canonical user."""

    model_config = ConfigDict(extra="forbid")

    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    username: str | None = Field(default=None, max_length=50)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    display_name: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, min_length=2, max_length=2)
    timezone: str = Field(default="Africa/Lagos", max_length=100)
    language: str = Field(default="en", max_length=20)


class UserCreateResponse(BaseModel):
    """Internal user creation response."""

    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    public_id: str
    status: str
    created_at: datetime


class UserStatusResponse(BaseModel):
    """Internal user status response."""

    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    status: str
    is_active: bool
    status_changed_at: datetime | None = None
    verification: dict[str, str]


class UserResolveRequest(BaseModel):
    """Internal identity resolution request."""

    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=20)


class ResolvedIdentity(BaseModel):
    """Minimal identity information returned during resolution."""

    model_config = ConfigDict(extra="forbid")

    type: str
    value: str
    is_verified: bool


class UserResolveResponse(BaseModel):
    """Internal identity resolution response."""

    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    status: str
    identities: list[ResolvedIdentity]


class UserResponse(BaseModel):
    """Standard user response."""

    model_config = ConfigDict(from_attributes=True)

    public_id: str
    status: str
    display_name: str | None
    last_active_at: datetime | None
    deactivated_at: datetime | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserDetailResponse(UserResponse):
    """Detailed user response including profile and identities."""

    profile: Any | None = None
    identities: list[ResolvedIdentity] = Field(default_factory=list)
