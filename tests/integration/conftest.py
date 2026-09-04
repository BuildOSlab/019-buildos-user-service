"""
Integration test fixtures for the BuildOS User Service.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.database.models.user import User
from app.database.session import SESSION_LOCAL
from app.main import app

INTERNAL_HEADERS = {
    "Authorization": f"Bearer {settings.internal_api_key}",
    "X-Service-ID": "buildos-auth-service",
}


@pytest.fixture
def client():
    """Provide a FastAPI test client for integration tests."""
    return TestClient(app)


@pytest.fixture
def internal_headers():
    """Provide authenticated internal service headers."""
    return INTERNAL_HEADERS.copy()


@pytest.fixture
def registration_payload():
    """Provide a unique valid payload for user registration tests."""
    unique = uuid.uuid4().hex[:10]

    # Use a valid numeric Nigerian mobile number.
    phone_suffix = str(int(unique, 16))[-8:].zfill(8)

    return {
        "email": f"integration_{unique}@example.com",
        "phone": f"+234801{phone_suffix}",
        "username": f"integration_{unique}",
        "first_name": "Integration",
        "last_name": "Test",
        "display_name": "Integration Test",
        "country": "NG",
        "timezone": "Africa/Lagos",
        "language": "en",
    }


@pytest.fixture
def cleanup_user():
    """Register created user IDs and remove them after each test."""
    created_user_ids = []

    def register(user_id):
        """Track a user ID for cleanup after the test."""
        created_user_ids.append(user_id)

    yield register

    db = SESSION_LOCAL()
    try:
        for user_id in created_user_ids:
            user = db.get(User, user_id)
            if user is not None:
                db.delete(user)
        db.commit()
    finally:
        db.close()
