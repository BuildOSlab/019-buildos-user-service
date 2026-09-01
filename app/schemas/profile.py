"""
BuildOS User Service
Profile API schemas.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProfileCreateRequest(BaseModel):
    """Request to create a user profile."""

    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=1000)
    profile_photo_reference: str | None = Field(default=None, max_length=500)
    country: str | None = Field(default=None, max_length=100)
    timezone: str = Field(default="Africa/Lagos", max_length=100)
    language: str = Field(default="en", max_length=20)
    visibility: str = Field(default="authenticated", max_length=20)
    profile_metadata: dict[str, Any] = Field(default_factory=dict)


class ProfileUpdateRequest(BaseModel):
    """Request to update a user profile."""

    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=1000)
    profile_photo_reference: str | None = Field(default=None, max_length=500)
    country: str | None = Field(default=None, max_length=100)
    timezone: str | None = Field(default=None, max_length=100)
    language: str | None = Field(default=None, max_length=20)
    visibility: str | None = Field(default=None, max_length=20)
    profile_metadata: dict[str, Any] | None = None


class ProfileResponse(BaseModel):
    """Public representation of a user profile."""

    model_config = ConfigDict(from_attributes=True)

    first_name: str | None
    last_name: str | None
    bio: str | None
    profile_photo_reference: str | None
    country: str | None
    timezone: str
    language: str
    visibility: str
    completion_percentage: int
    profile_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime
