"""
BuildOS User Service
User status lifecycle business logic.
"""

from datetime import UTC, datetime
from typing import ClassVar
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.constants import (
    USER_STATUS_ACTIVE,
    USER_STATUS_DEACTIVATED,
    USER_STATUS_DELETED,
    USER_STATUS_PENDING,
    USER_STATUS_RESTRICTED,
    USER_STATUS_SUSPENDED,
    USER_STATUS_VERIFICATION_PENDING,
    VALID_USER_STATUSES,
)
from app.core.exceptions import (
    InvalidUserStatusTransitionError,
    UserNotFoundError,
)
from app.database.models.status_history import UserStatusHistory
from app.database.models.user import User
from app.database.repositories.status_history_repository import (
    StatusHistoryRepository,
)
from app.database.repositories.user_repository import UserRepository


class StatusService:
    """Business logic for user status transitions."""

    ALLOWED_TRANSITIONS: ClassVar[dict[str, set[str]]] = {
        USER_STATUS_PENDING: {
            USER_STATUS_VERIFICATION_PENDING,
            USER_STATUS_ACTIVE,
            USER_STATUS_DEACTIVATED,
            USER_STATUS_DELETED,
        },
        USER_STATUS_VERIFICATION_PENDING: {
            USER_STATUS_ACTIVE,
            USER_STATUS_DEACTIVATED,
            USER_STATUS_DELETED,
        },
        USER_STATUS_ACTIVE: {
            USER_STATUS_SUSPENDED,
            USER_STATUS_DEACTIVATED,
            USER_STATUS_RESTRICTED,
            USER_STATUS_DELETED,
        },
        USER_STATUS_SUSPENDED: {
            USER_STATUS_ACTIVE,
            USER_STATUS_DEACTIVATED,
            USER_STATUS_DELETED,
        },
        USER_STATUS_RESTRICTED: {
            USER_STATUS_ACTIVE,
            USER_STATUS_SUSPENDED,
            USER_STATUS_DEACTIVATED,
            USER_STATUS_DELETED,
        },
        USER_STATUS_DEACTIVATED: {
            USER_STATUS_ACTIVE,
            USER_STATUS_DELETED,
        },
        USER_STATUS_DELETED: set(),
    }

    def __init__(self, db: Session) -> None:
        """Initialize the status service."""
        self.db = db
        self.users = UserRepository(db)
        self.history = StatusHistoryRepository(db)

    def get_status(self, user_id: UUID) -> User:
        """Return the current user status."""
        user = self.users.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found.")

        return user

    def get_history(
        self,
        user_id: UUID,
    ) -> list[UserStatusHistory]:
        """Return status transition history."""
        self.get_status(user_id)
        return self.history.get_by_user_id(user_id)

    def transition(
        self,
        user_id: UUID,
        new_status: str,
        reason: str | None = None,
        actor_id: str | None = None,
    ) -> User:
        """Transition a user to a new status."""
        user = self.get_status(user_id)

        normalized_status = new_status.strip().lower()

        if normalized_status not in VALID_USER_STATUSES:
            raise InvalidUserStatusTransitionError(
                "Invalid user status."
            )

        current_status = user.status

        if current_status == normalized_status:
            return user

        allowed = self.ALLOWED_TRANSITIONS.get(
            current_status,
            set(),
        )

        if normalized_status not in allowed:
            raise InvalidUserStatusTransitionError(
                f"Cannot transition from {current_status} "
                f"to {normalized_status}."
            )

        previous_status = user.status
        user.status = normalized_status

        now = datetime.now(UTC)

        if normalized_status == USER_STATUS_DEACTIVATED:
            user.deactivated_at = now

        elif normalized_status == USER_STATUS_ACTIVE:
            user.deactivated_at = None

        if normalized_status == USER_STATUS_DELETED:
            user.deleted_at = now

        self.users.update(user)

        self.history.create_status_history(
            user_id=user.id,
            from_status=previous_status,
            to_status=normalized_status,
            reason=reason,
            actor_id=actor_id,
        )

        return user

    def is_active(self, user_id: UUID) -> bool:
        """Return whether a user is currently active."""
        user = self.get_status(user_id)
        return (
            user.status == USER_STATUS_ACTIVE
            and user.deleted_at is None
        )

    def get_status_changed_at(
        self,
        user_id: UUID,
    ) -> datetime | None:
        """Return when the current status was last changed."""
        latest = self.history.get_latest(user_id)

        if latest is None:
            return None

        return latest.created_at
