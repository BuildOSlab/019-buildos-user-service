"""
BuildOS User Service
Event Schemas
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class EventEnvelope(BaseModel):
    """Common envelope for all published user-service events."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    event_version: str = "1.0"
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )
    producer: str = "user-service"
    user_id: UUID
    data: dict[str, Any] = Field(default_factory=dict)


class UserCreatedEvent(EventEnvelope):
    """Published when a canonical user is created."""

    event_type: str = "USER_CREATED"


class UserActivatedEvent(EventEnvelope):
    """Published when a user becomes active."""

    event_type: str = "USER_ACTIVATED"


class UserSuspendedEvent(EventEnvelope):
    """Published when a user is suspended."""

    event_type: str = "USER_SUSPENDED"


class UserDeactivatedEvent(EventEnvelope):
    """Published when a user is deactivated."""

    event_type: str = "USER_DEACTIVATED"


class UserReactivatedEvent(EventEnvelope):
    """Published when a user is reactivated."""

    event_type: str = "USER_REACTIVATED"


class UserDeletedEvent(EventEnvelope):
    """Published when a user is deleted."""

    event_type: str = "USER_DELETED"


class UserRestrictedEvent(EventEnvelope):
    """Published when a user is restricted."""

    event_type: str = "USER_RESTRICTED"


class UserStatusChangedEvent(EventEnvelope):
    """Published when a user's status changes."""

    event_type: str = "USER_STATUS_CHANGED"


class UserProfileUpdatedEvent(EventEnvelope):
    """Published when a user's profile changes."""

    event_type: str = "USER_PROFILE_UPDATED"


class UserPreferencesUpdatedEvent(EventEnvelope):
    """Published when a user's preferences change."""

    event_type: str = "USER_PREFERENCES_UPDATED"
