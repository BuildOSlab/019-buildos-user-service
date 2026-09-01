"""
BuildOS User Service
User Identity Repository
"""

from uuid import UUID

from sqlalchemy import select

from app.database.models.identity import UserIdentity
from app.database.repositories.base import BaseRepository


class IdentityRepository(BaseRepository[UserIdentity]):
    """Database operations for user identities."""

    model = UserIdentity

    def get_by_type_and_value(
        self,
        identity_type: str,
        value: str,
    ) -> UserIdentity | None:
        """Return an identity by type and value."""
        statement = select(UserIdentity).where(
            UserIdentity.type == identity_type,
            UserIdentity.value == value,
        )
        return self.db.scalar(statement)

    def get_by_user_id(
        self,
        user_id: UUID,
    ) -> list[UserIdentity]:
        """Return all identities belonging to a user."""
        statement = select(UserIdentity).where(
            UserIdentity.user_id == user_id,
        )
        return list(self.db.scalars(statement).all())

    def get_primary(
        self,
        user_id: UUID,
        identity_type: str | None = None,
    ) -> UserIdentity | None:
        """Return the primary identity for a user."""
        conditions = [
            UserIdentity.user_id == user_id,
            UserIdentity.is_primary.is_(True),
        ]

        if identity_type is not None:
            conditions.append(UserIdentity.type == identity_type)

        statement = select(UserIdentity).where(*conditions)
        return self.db.scalar(statement)

    def create_identity(
        self,
        *,
        user_id: UUID,
        identity_type: str,
        value: str,
        is_primary: bool = False,
        is_verified: bool = False,
    ) -> UserIdentity:
        """Create and persist a user identity."""
        identity = UserIdentity(
            user_id=user_id,
            type=identity_type,
            value=value,
            is_primary=is_primary,
            is_verified=is_verified,
        )
        return self.create(identity)

    def update(
        self,
        identity: UserIdentity,
    ) -> UserIdentity:
        """Persist changes to an identity."""
        self.db.add(identity)
        self.db.flush()
        self.db.refresh(identity)
        return identity
