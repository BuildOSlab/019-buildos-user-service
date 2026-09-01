"""
BuildOS User Service
User Status History Model
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.user import User


class UserStatusHistory(Base):
    """Audit trail of user status changes."""

    __tablename__ = "user_status_history"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    from_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    to_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    actor_id: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # pylint: disable=not-callable
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="status_history",
    )

    def __repr__(self) -> str:
        return (
            f"<UserStatusHistory user_id={self.user_id} "
            f"{self.from_status}->{self.to_status}>"
        )
