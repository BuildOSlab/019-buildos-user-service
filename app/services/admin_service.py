"""
BuildOS User Service
Administrative business logic.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.repositories.user_repository import UserRepository
from app.schemas.admin import (
    AdminStatusUpdateRequest,
    AdminUserUpdateRequest,
)
from app.services.status_service import StatusService


class AdminService:
    """Business logic for administrative user operations."""

    def __init__(self, db: Session) -> None:
        """Initialize the administrative service."""
        self.db = db
        self.users = UserRepository(db)
        self.status = StatusService(db)

    def get_user(self, user_id: UUID) -> User:
        """Return a user for administrative inspection."""
        return self.status.get_status(user_id)

    def update_user(
        self,
        user_id: UUID,
        request: AdminUserUpdateRequest,
    ) -> User:
        """Update explicitly permitted user fields."""
        user = self.status.get_status(user_id)

        if request.display_name is not None:
            user.display_name = request.display_name

        return self.users.update(user)

    def update_status(
        self,
        user_id: UUID,
        request: AdminStatusUpdateRequest,
        actor_id: str | None = None,
    ) -> User:
        """Change a user's account status."""
        return self.status.transition(
            user_id=user_id,
            new_status=request.status,
            reason=request.reason,
            actor_id=actor_id,
        )

    def list_users_by_status(
        self,
        status: str,
    ) -> list[User]:
        """List users matching an account status."""
        return self.users.list_by_status(status.strip().lower())
