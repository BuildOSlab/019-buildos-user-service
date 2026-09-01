"""
BuildOS User Service
Identity schemas and normalization contracts.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IdentityCreateRequest(BaseModel):
    """Request for adding an identity to a user."""

    model_config = ConfigDict(extra="forbid")

    type: str = Field(min_length=1, max_length=20)
    value: str = Field(min_length=1, max_length=255)


class IdentityUpdateRequest(BaseModel):
    """Request for updating identity verification state."""

    model_config = ConfigDict(extra="forbid")

    is_primary: bool | None = None
    is_verified: bool | None = None


class IdentityResponse(BaseModel):
    """Identity API response."""

    model_config = ConfigDict(from_attributes=True)

    type: str
    value: str
    is_primary: bool
    is_verified: bool
    verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
