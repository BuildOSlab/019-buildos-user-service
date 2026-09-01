"""
BuildOS User Service
User Status History Repository
"""

from uuid import UUID

from sqlalchemy import select

from app.database.models.status_history import UserStatusHistory
from app.database.repositories.base import BaseRepository


class StatusHistoryRepository(BaseRepository[UserStatusHistory]):
    """Database operations for user status history."""

    model = UserStatusHistory

    def get_by_user_id(
        self,
        user_id: UUID,
    ) -> list[UserStatusHistory]:
        """Return status history for a user."""
        statement = (
            select(UserStatusHistory)
            .where(UserStatusHistory.user_id == user_id)
            .order_by(UserStatusHistory.created_at.asc())
        )
        return list(self.db.scalars(statement).all())

    def get_latest(
        self,
        user_id: UUID,
    ) -> UserStatusHistory | None:
        """Return the most recent status transition for a user."""
        statement = (
            select(UserStatusHistory)
            .where(UserStatusHistory.user_id == user_id)
            .order_by(UserStatusHistory.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(statement)

    def create_status_history(
        self,
        *,
        user_id: UUID,
        from_status: str,
        to_status: str,
        reason: str | None = None,
        actor_id: str | None = None,
    ) -> UserStatusHistory:
        """Create and persist a user status transition."""
        history = UserStatusHistory(
            user_id=user_id,
            from_status=from_status,
            to_status=to_status,
            reason=reason,
            actor_id=actor_id,
        )
        return self.create(history)
