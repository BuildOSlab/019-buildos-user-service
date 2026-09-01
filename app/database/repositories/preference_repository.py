"""
BuildOS User Service
User Preference Repository
"""

from uuid import UUID

from sqlalchemy import select

from app.database.models.preference import UserPreference
from app.database.repositories.base import BaseRepository


class PreferenceRepository(BaseRepository[UserPreference]):
    """Database operations for user preferences."""

    model = UserPreference

    def get_by_user_and_key(
        self,
        user_id: UUID,
        key: str,
    ) -> UserPreference | None:
        """Return a preference by user and key."""
        statement = select(UserPreference).where(
            UserPreference.user_id == user_id,
            UserPreference.key == key,
        )
        return self.db.scalar(statement)

    def get_by_user_id(
        self,
        user_id: UUID,
    ) -> list[UserPreference]:
        """Return all preferences belonging to a user."""
        statement = select(UserPreference).where(
            UserPreference.user_id == user_id,
        )
        return list(self.db.scalars(statement).all())

    def create_preference(
        self,
        *,
        user_id: UUID,
        key: str,
        value: str,
    ) -> UserPreference:
        """Create and persist a user preference."""
        preference = UserPreference(
            user_id=user_id,
            key=key,
            value=value,
        )
        return self.create(preference)

    def update(
        self,
        preference: UserPreference,
    ) -> UserPreference:
        """Persist changes to a preference."""
        self.db.add(preference)
        self.db.flush()
        self.db.refresh(preference)
        return preference

    def delete_by_user_and_key(
        self,
        user_id: UUID,
        key: str,
    ) -> bool:
        """Delete a preference by user and key."""
        preference = self.get_by_user_and_key(user_id, key)

        if preference is None:
            return False

        self.delete(preference)
        return True
