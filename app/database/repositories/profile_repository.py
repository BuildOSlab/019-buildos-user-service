"""
BuildOS User Service
User Profile Repository
"""

from uuid import UUID

from sqlalchemy import select

from app.database.models.profile import UserProfile
from app.database.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[UserProfile]):
    """Database operations for user profiles."""

    model = UserProfile

    def get_by_user_id(
        self,
        user_id: UUID,
    ) -> UserProfile | None:
        """Return the profile belonging to a user."""
        statement = select(UserProfile).where(
            UserProfile.user_id == user_id,
        )
        return self.db.scalar(statement)

    # pylint: disable=too-many-arguments
    def create_profile(
        self,
        *,
        user_id: UUID,
        first_name: str | None = None,
        last_name: str | None = None,
        bio: str | None = None,
        profile_photo_reference: str | None = None,
        country: str | None = None,
        timezone: str = "Africa/Lagos",
        language: str = "en",
        visibility: str = "authenticated",
        completion_percentage: int = 0,
        profile_metadata: dict | None = None,
    ) -> UserProfile:
        """Create and persist a user profile."""
        profile = UserProfile(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            profile_photo_reference=profile_photo_reference,
            country=country,
            timezone=timezone,
            language=language,
            visibility=visibility,
            completion_percentage=completion_percentage,
            profile_metadata=profile_metadata or {},
        )
        return self.create(profile)

    def update(
        self,
        profile: UserProfile,
    ) -> UserProfile:
        """Persist changes to a user profile."""
        self.db.add(profile)
        self.db.flush()
        self.db.refresh(profile)
        return profile
