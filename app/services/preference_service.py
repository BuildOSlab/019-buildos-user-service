"""
BuildOS User Service
User preference business logic.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import UserNotFoundError
from app.database.models.preference import UserPreference
from app.database.repositories.preference_repository import (
    PreferenceRepository,
)
from app.database.repositories.user_repository import UserRepository
from app.schemas.preferences import (
    PreferenceCreateRequest,
    PreferenceUpdateRequest,
)


class PreferenceService:
    """Business logic for user preferences."""

    def __init__(self, db: Session) -> None:
        """Initialize the preference service."""
        self.db = db
        self.preferences = PreferenceRepository(db)
        self.users = UserRepository(db)

    def list_preferences(
        self,
        user_id: UUID,
    ) -> list[UserPreference]:
        """Return all preferences belonging to a user."""
        self._require_user(user_id)
        return self.preferences.get_by_user_id(user_id)

    def get_preference(
        self,
        user_id: UUID,
        key: str,
    ) -> UserPreference | None:
        """Return a single preference."""
        self._require_user(user_id)

        return self.preferences.get_by_user_and_key(
            user_id,
            key,
        )

    def create_or_update(
        self,
        user_id: UUID,
        request: PreferenceCreateRequest,
    ) -> UserPreference:
        """Create a preference or replace its value."""
        self._require_user(user_id)

        existing = self.preferences.get_by_user_and_key(
            user_id,
            request.key,
        )

        if existing is None:
            return self.preferences.create_preference(
                user_id=user_id,
                key=request.key,
                value=request.value,
            )

        existing.value = request.value

        return self.preferences.update(existing)

    def update(
        self,
        user_id: UUID,
        key: str,
        request: PreferenceUpdateRequest,
    ) -> UserPreference:
        """Update an existing preference."""
        self._require_user(user_id)

        preference = self.preferences.get_by_user_and_key(
            user_id,
            key,
        )

        if preference is None:
            raise UserNotFoundError("Preference not found.")

        preference.value = request.value

        return self.preferences.update(preference)

    def delete(
        self,
        user_id: UUID,
        key: str,
    ) -> bool:
        """Delete a preference."""
        self._require_user(user_id)

        return self.preferences.delete_by_user_and_key(
            user_id,
            key,
        )

    def _require_user(self, user_id: UUID) -> None:
        """Ensure the user exists."""
        if self.users.get_by_id(user_id) is None:
            raise UserNotFoundError("User not found.")
