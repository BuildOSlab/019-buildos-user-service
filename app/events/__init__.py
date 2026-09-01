"""
BuildOS User Service
Event package.
"""

from app.events.producer import EventProducer, event_producer
from app.events.schemas import (
    EventEnvelope,
    UserActivatedEvent,
    UserCreatedEvent,
    UserDeactivatedEvent,
    UserDeletedEvent,
    UserPreferencesUpdatedEvent,
    UserProfileUpdatedEvent,
    UserReactivatedEvent,
    UserRestrictedEvent,
    UserStatusChangedEvent,
    UserSuspendedEvent,
)

__all__ = [
    "EventEnvelope",
    "EventProducer",
    "UserActivatedEvent",
    "UserCreatedEvent",
    "UserDeactivatedEvent",
    "UserDeletedEvent",
    "UserPreferencesUpdatedEvent",
    "UserProfileUpdatedEvent",
    "UserReactivatedEvent",
    "UserRestrictedEvent",
    "UserStatusChangedEvent",
    "UserSuspendedEvent",
    "event_producer",
]
