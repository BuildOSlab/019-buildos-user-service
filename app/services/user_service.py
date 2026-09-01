"""
BuildOS User Service
Canonical user business logic.
"""

from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import (
    IDENTITY_TYPE_EMAIL,
    IDENTITY_TYPE_PHONE,
    IDENTITY_TYPE_USERNAME,
    USER_STATUS_PENDING,
)
from app.core.exceptions import (
    IdentityAlreadyExistsError,
    UserNotFoundError,
)
from app.core.idempotency import create_request_hash
from app.database.models.user import User
from app.database.repositories.identity_repository import IdentityRepository
from app.database.repositories.profile_repository import ProfileRepository
from app.database.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateRequest
from app.utils.id_generator import generate_public_id
from app.utils.validators import (
    normalize_email,
    normalize_phone,
    normalize_username,
)


class UserService:
    """Business logic for canonical users."""

    def __init__(self, db: Session) -> None:
        """Initialize the user service."""
        self.db = db
        self.users = UserRepository(db)
        self.identities = IdentityRepository(db)
        self.profiles = ProfileRepository(db)

    def get_user(self, user_id: UUID) -> User:
        """Return a user by internal UUID."""
        user = self.users.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found.")

        return user

    def get_user_by_public_id(self, public_id: str) -> User:
        """Return a user by public identifier."""
        user = self.users.get_by_public_id(public_id)

        if user is None:
            raise UserNotFoundError("User not found.")

        return user

    def create_user(
        self,
        request: UserCreateRequest,
        idempotency_key: str,
    ) -> User:
        """
        Create a canonical user and its initial identities/profile.

        The caller owns the transaction and must commit or rollback.
        """
        email = (
            normalize_email(request.email)
            if request.email is not None
            else None
        )
        phone = (
            normalize_phone(request.phone)
            if request.phone is not None
            else None
        )
        username = (
            normalize_username(request.username)
            if request.username is not None
            else None
        )

        if email is None and phone is None and username is None:
            raise ValueError("At least one identity is required.")

        normalized_payload = {
            "email": email,
            "phone": phone,
            "username": username,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "display_name": request.display_name,
            "country": request.country,
            "timezone": request.timezone,
            "language": request.language,
        }

        idempotency_hash = create_request_hash(normalized_payload)

        existing_user = self.users.get_by_idempotency_key(
            idempotency_key,
        )

        if existing_user is not None:
            if existing_user.idempotency_hash != idempotency_hash:
                raise ValueError(
                    "Idempotency key was already used with "
                    "different registration data."
                )

            return existing_user

        identity_values = (
            (IDENTITY_TYPE_EMAIL, email),
            (IDENTITY_TYPE_PHONE, phone),
            (IDENTITY_TYPE_USERNAME, username),
        )

        for identity_type, value in identity_values:
            if value is None:
                continue

            existing = self.identities.get_by_type_and_value(
                identity_type,
                value,
            )

            if existing is not None:
                raise IdentityAlreadyExistsError(
                    f"{identity_type} is already registered."
                )

        public_id = self._generate_unique_public_id()

        user = self.users.create_user(
            public_id=public_id,
            status=USER_STATUS_PENDING,
            idempotency_key=idempotency_key,
            idempotency_hash=idempotency_hash,
            display_name=request.display_name,
        )

        primary_assigned = False

        try:
            for identity_type, value in identity_values:
                if value is None:
                    continue

                identity = self.identities.create_identity(
                    user_id=user.id,
                    identity_type=identity_type,
                    value=value,
                    is_primary=not primary_assigned,
                    is_verified=False,
                )

                if identity.is_primary:
                    primary_assigned = True

            self.profiles.create_profile(
                user_id=user.id,
                first_name=request.first_name,
                last_name=request.last_name,
                country=request.country,
                timezone=request.timezone,
                language=request.language,
            )
        except IntegrityError as exc:
            raise IdentityAlreadyExistsError(
                "One or more identities are already registered."
            ) from exc

        return user

    def update_display_name(
        self,
        user_id: UUID,
        display_name: str | None,
    ) -> User:
        """Update a user's display name."""
        user = self.get_user(user_id)
        user.display_name = display_name
        return self.users.update(user)

    def _generate_unique_public_id(self) -> str:
        """Generate a public ID that does not already exist."""
        for _ in range(10):
            public_id = generate_public_id()

            if self.users.get_by_public_id(public_id) is None:
                return public_id

        raise RuntimeError("Unable to generate a unique public user ID.")
    