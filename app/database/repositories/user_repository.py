"""
BuildOS User Service
User Repository
"""

from uuid import UUID

from sqlalchemy import select

from app.core.constants import USER_STATUS_ACTIVE
from app.database.models.user import User
from app.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Database operations for canonical users."""

    model = User

    def get_by_public_id(
        self,
        public_id: str,
    ) -> User | None:
        """Return a user by public identifier."""
        statement = select(User).where(
            User.public_id == public_id,
        )
        return self.db.scalar(statement)

    def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> User | None:
        """Return a user created with the supplied idempotency key."""
        statement = select(User).where(
            User.idempotency_key == idempotency_key,
        )
        return self.db.scalar(statement)

    def get_active_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        """Return an active user by UUID."""
        statement = select(User).where(
            User.id == user_id,
            User.status == USER_STATUS_ACTIVE,
            User.deleted_at.is_(None),
        )
        return self.db.scalar(statement)

    def list_by_status(
        self,
        status: str,
    ) -> list[User]:
        """Return users with the requested status."""
        statement = select(User).where(
            User.status == status,
        )
        return list(self.db.scalars(statement).all())

    def create_user(
        self,
        *,
        public_id: str,
        status: str,
        idempotency_key: str,
        idempotency_hash: str,
        display_name: str | None = None,
    ) -> User:
        """Create and persist a canonical user record."""
        user = User(
            public_id=public_id,
            status=status,
            idempotency_key=idempotency_key,
            idempotency_hash=idempotency_hash,
            display_name=display_name,
        )
        return self.create(user)

    def update(
        self,
        user: User,
    ) -> User:
        """Persist changes to a user."""
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user
