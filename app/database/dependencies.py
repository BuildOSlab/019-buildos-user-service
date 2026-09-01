"""
BuildOS User Service
Database Dependencies
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.session import SESSION_LOCAL


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for dependency injection."""
    db = SESSION_LOCAL()

    try:
        yield db
    finally:
        db.close()
