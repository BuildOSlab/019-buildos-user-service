"""
BuildOS User Service
Profile business logic.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.constants import (
    PROFILE_VISIBILITY_AUTHENTICATED,
    PROFILE_VISIBILITY_PRIVATE,
    PROFILE_VISIBILITY_PUBLIC,
)
from app.core.exceptions import (
    ProfileUpdateError,
    UserNotFoundError,
)
from app.database.models.profile import UserProfile
from app.database.repositories.profile_repository import ProfileRepository
from app.database.repositories.user_repository import UserRepository
from app.schemas.profile import (
    ProfileCreateRequest,
    ProfileUpdateRequest,
)


class ProfileService:
    """Business logic for user profiles."""

    def __init__(self, db: Session) -> None:
        """Initialize the profile service."""
        self.db = db
        self.profiles = ProfileRepository(db)
        self.users = UserRepository(db)

    def get_profile(self, user_id: UUID) -> UserProfile:
        """Return a user's profile."""
        user = self.users.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found.")

        profile = self.profiles.get_by_user_id(user_id)

        if profile is None:
            raise ProfileUpdateError("User profile does not exist.")

        return profile

    def create_profile(
        self,
        user_id: UUID,
        request: ProfileCreateRequest,
    ) -> UserProfile:
        """Create a profile for an existing user."""
        user = self.users.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found.")

        existing = self.profiles.get_by_user_id(user_id)

        if existing is not None:
            raise ProfileUpdateError("User profile already exists.")

        self._validate_visibility(request.visibility)

        return self.profiles.create_profile(
            user_id=user_id,
            first_name=request.first_name,
            last_name=request.last_name,
            bio=request.bio,
            profile_photo_reference=request.profile_photo_reference,
            country=request.country,
            timezone=request.timezone,
            language=request.language,
            visibility=request.visibility,
            profile_metadata=request.profile_metadata,
            completion_percentage=self._calculate_completion(
                request.first_name,
                request.last_name,
                request.bio,
                request.country,
                request.profile_photo_reference,
            ),
        )

    def update_profile(
        self,
        user_id: UUID,
        request: ProfileUpdateRequest,
    ) -> UserProfile:
        """Update allowed profile fields."""
        profile = self.get_profile(user_id)

        if request.visibility is not None:
            self._validate_visibility(request.visibility)
            profile.visibility = request.visibility

        if request.first_name is not None:
            profile.first_name = request.first_name

        if request.last_name is not None:
            profile.last_name = request.last_name

        if request.bio is not None:
            profile.bio = request.bio

        if request.profile_photo_reference is not None:
            profile.profile_photo_reference = (
                request.profile_photo_reference
            )

        if request.country is not None:
            profile.country = request.country

        if request.timezone is not None:
            profile.timezone = request.timezone

        if request.language is not None:
            profile.language = request.language

        if request.profile_metadata is not None:
            profile.profile_metadata = request.profile_metadata

        profile.completion_percentage = self._calculate_completion(
            profile.first_name,
            profile.last_name,
            profile.bio,
            profile.country,
            profile.profile_photo_reference,
        )

        return self.profiles.update(profile)

    @staticmethod
    def _validate_visibility(value: str) -> None:
        """Validate profile visibility."""
        if value not in {
            PROFILE_VISIBILITY_PUBLIC,
            PROFILE_VISIBILITY_AUTHENTICATED,
            PROFILE_VISIBILITY_PRIVATE,
        }:
            raise ProfileUpdateError("Invalid profile visibility.")

    @staticmethod
    def _calculate_completion(
        first_name: str | None,
        last_name: str | None,
        bio: str | None,
        country: str | None,
        photo_reference: str | None,
    ) -> int:
        """Calculate a simple profile completion percentage."""
        fields = (
            first_name,
            last_name,
            bio,
            country,
            photo_reference,
        )

        completed = sum(
            1
            for value in fields
            if value is not None and value.strip()
        )

        return int(completed / len(fields) * 100)
