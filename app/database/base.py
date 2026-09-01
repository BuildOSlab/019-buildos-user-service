"""
BuildOS User Service
Database Declarative Base
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all User Service SQLAlchemy models."""
