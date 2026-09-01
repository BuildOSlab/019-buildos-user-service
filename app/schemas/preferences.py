"""
BuildOS User Service
User preference API schemas.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PreferenceCreateRequest(BaseModel):
    """Request to create a user preference."""

    model_config = ConfigDict(extra="forbid")

    key: str = Field(min_length=1, max_length=100)
    value: str = Field(max_length=1000)


class PreferenceUpdateRequest(BaseModel):
    """Request to update a user preference."""

    model_config = ConfigDict(extra="forbid")

    value: str = Field(max_length=1000)


class PreferenceResponse(BaseModel):
    """User preference response."""

    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str
    updated_at: datetime
