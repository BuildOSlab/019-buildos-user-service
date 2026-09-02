"""
BuildOS User Service
Base Database Repository
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """Base repository providing common SQLAlchemy operations."""

    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        """Initialize the repository with a database session."""
        self.db = db

    def get_by_id(self, record_id: UUID) -> ModelT | None:
        """Return a record by its UUID primary key."""
        model: Any = self.model
        model_id = model.id
        statement = select(model).where(model_id == record_id)
        return self.db.scalar(statement)

    def create(self, instance: ModelT) -> ModelT:
        """Add and flush a model instance."""
        self.db.add(instance)
        self.db.flush()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        """Delete a model instance."""
        self.db.delete(instance)
        self.db.flush()
