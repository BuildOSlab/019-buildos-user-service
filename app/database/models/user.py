"""
BuildOS User Service
User Model (canonical user record)
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import USER_STATUS_PENDING
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.identity import UserIdentity
    from app.database.models.organization import UserOrganization
    from app.database.models.preference import UserPreference
    from app.database.models.profile import UserProfile
    from app.database.models.role_reference import UserRoleReference
    from app.database.models.status_history import UserStatusHistory


class User(Base):
    """Canonical user account record."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    public_id: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
        index=True,
    )

    # The key supplied by the caller for registration idempotency.
    # It is globally unique so a retried registration maps to the
    # same canonical user rather than creating another user.
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    # SHA-256 fingerprint of the normalized registration request.
    # This prevents the same idempotency key from being reused
    # with different registration data.
    idempotency_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=USER_STATUS_PENDING,
        server_default=USER_STATUS_PENDING,
        index=True,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    deactivated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # pylint: disable=not-callable
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # pylint: disable=not-callable
        onupdate=func.now(),  # pylint: disable=not-callable
    )

    profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    identities: Mapped[list["UserIdentity"]] = relationship(
        "UserIdentity",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    preferences: Mapped[list["UserPreference"]] = relationship(
        "UserPreference",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    status_history: Mapped[list["UserStatusHistory"]] = relationship(
        "UserStatusHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    organizations: Mapped[list["UserOrganization"]] = relationship(
        "UserOrganization",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    role_references: Mapped[list["UserRoleReference"]] = relationship(
        "UserRoleReference",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<User public_id={self.public_id} "
            f"status={self.status}>"
        )
    