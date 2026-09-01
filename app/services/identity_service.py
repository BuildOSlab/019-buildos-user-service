"""
BuildOS User Service
Identity business logic.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.constants import (
    IDENTITY_TYPE_EMAIL,
    IDENTITY_TYPE_PHONE,
    IDENTITY_TYPE_USERNAME,
    USER_STATUS_DELETED,
)
from app.core.exceptions import (
    IdentityAlreadyExistsError,
    UserNotFoundError,
)
from app.database.models.identity import UserIdentity
from app.database.repositories.identity_repository import IdentityRepository
from app.database.repositories.user_repository import UserRepository
from app.schemas.identity import IdentityCreateRequest
from app.utils.validators import normalize_identity


class IdentityService:
    """Business logic for user identities."""

    def __init__(self, db: Session) -> None:
        """Initialize the identity service."""
        self.db = db
        self.identities = IdentityRepository(db)
        self.users = UserRepository(db)

    def create_identity(
        self,
        user_id: UUID,
        request: IdentityCreateRequest,
    ) -> UserIdentity:
        """Create a new identity for an existing user."""
        user = self.users.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found.")

        identity_type = request.type.strip().lower()
        value = normalize_identity(identity_type, request.value)

        existing = self.identities.get_by_type_and_value(
            identity_type,
            value,
        )

        if existing is not None:
            raise IdentityAlreadyExistsError(
                "This identity is already registered."
            )

        return self.identities.create_identity(
            user_id=user_id,
            identity_type=identity_type,
            value=value,
        )

    def get_user_id_by_identifier(
        self,
        identity_type: str,
        identifier: str,
    ) -> UUID | None:
        """Resolve an identity to its internal user UUID."""
        normalized_type = identity_type.strip().lower()

        value = normalize_identity(
            normalized_type,
            identifier,
        )

        identity = self.identities.get_by_type_and_value(
            normalized_type,
            value,
        )

        if identity is None:
            return None

        return identity.user_id

    def resolve(
        self,
        identity_type: str,
        identifier: str,
    ) -> tuple[UUID | None, str, list[UserIdentity]]:
        """
        Resolve an identity.

        Deleted users are returned to the caller so the API can map the
        condition to the contract's 410 USER_DELETED response.
        """
        normalized_type = identity_type.strip().lower()

        if normalized_type not in {
            IDENTITY_TYPE_EMAIL,
            IDENTITY_TYPE_PHONE,
            IDENTITY_TYPE_USERNAME,
        }:
            raise ValueError("Unsupported identity type.")

        value = normalize_identity(
            normalized_type,
            identifier,
        )

        identity = self.identities.get_by_type_and_value(
            normalized_type,
            value,
        )

        if identity is None:
            return None, "not_found", []

        user = self.users.get_by_id(identity.user_id)

        if user is None:
            return None, "not_found", []

        identities = self.identities.get_by_user_id(user.id)

        if user.status == USER_STATUS_DELETED:
            return user.id, "deleted", identities

        return user.id, user.status, identities

    def mark_verified(
        self,
        identity: UserIdentity,
    ) -> UserIdentity:
        """Mark an identity as verified."""
        identity.is_verified = True
        identity.verified_at = datetime.now(UTC)
        return self.identities.update(identity)

    def set_primary(
        self,
        user_id: UUID,
        identity: UserIdentity,
    ) -> UserIdentity:
        """Make an identity primary for the user."""
        identities = self.identities.get_by_user_id(user_id)

        for existing in identities:
            if existing.id != identity.id and existing.is_primary:
                existing.is_primary = False
                self.identities.update(existing)

        identity.is_primary = True

        return self.identities.update(identity)
