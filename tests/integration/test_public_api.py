"""
Integration tests for the public User Service API.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt


def make_access_token(user_id: UUID) -> str:
    """Create an access token matching the BuildOS Auth Service contract."""
    from app.core.config import settings

    now = datetime.now(UTC)

    payload = {
        "sub": str(user_id),
        "iss": settings.auth_jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "jti": str(uuid4()),
        "token_type": "access",
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_test_user(client, internal_headers, registration_payload):
    """Create a real user through the internal API."""
    response = client.post(
        "/internal/v1/users/create",
        json=registration_payload,
        headers={
            **internal_headers,
            "Idempotency-Key": str(uuid4()),
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    return UUID(data["user_id"])


def test_public_user_api(
    client,
    internal_headers,
    registration_payload,
    cleanup_user,
):
    """Exercise the authenticated public user API against PostgreSQL."""
    user_id = create_test_user(
        client,
        internal_headers,
        registration_payload,
    )
    cleanup_user(user_id)

    headers = {
        "Authorization": f"Bearer {make_access_token(user_id)}",
    }

    # GET /users/me
    response = client.get(
        "/api/v1/users/me",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    user = response.json()

    assert user["public_id"].startswith("usr_")
    assert user["status"] == "pending"
    assert user["display_name"] == "Integration Test"

    # PATCH /users/me
    response = client.patch(
        "/api/v1/users/me",
        json={"display_name": "Updated Integration User"},
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["display_name"] == "Updated Integration User"

    # GET /profiles/me
    response = client.get(
        "/api/v1/profiles/me",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    profile = response.json()

    assert profile["first_name"] == "Integration"
    assert profile["last_name"] == "Test"

    # PATCH /profiles/me
    response = client.patch(
        "/api/v1/profiles/me",
        json={
            "bio": "Integration test profile",
            "language": "en",
        },
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["bio"] == "Integration test profile"

    # GET /preferences
    response = client.get(
        "/api/v1/preferences",
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)

    # POST /preferences
    response = client.post(
        "/api/v1/preferences",
        json={
            "key": "theme",
            "value": "dark",
        },
        headers=headers,
    )

    assert response.status_code == 201, response.text
    assert response.json()["key"] == "theme"
    assert response.json()["value"] == "dark"

    # GET /preferences/{key}
    response = client.get(
        "/api/v1/preferences/theme",
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["value"] == "dark"

    # PUT /preferences/{key}
    response = client.put(
        "/api/v1/preferences/theme",
        json={"value": "light"},
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["value"] == "light"

    # DELETE /preferences/{key}
    response = client.delete(
        "/api/v1/preferences/theme",
        headers=headers,
    )

    assert response.status_code == 204, response.text

    # Confirm deletion.
    response = client.get(
        "/api/v1/preferences/theme",
        headers=headers,
    )

    assert response.status_code == 404, response.text

    # GET /status/me
    response = client.get(
        "/api/v1/status/me",
        headers=headers,
    )

    assert response.status_code == 200, response.text

    status_data = response.json()

    assert status_data["user_id"] == str(user_id)
    assert status_data["status"] == "pending"
    assert status_data["is_active"] is False


def test_public_api_requires_authentication(client):
    """Public account endpoints must reject unauthenticated requests."""
    endpoints = [
        ("GET", "/api/v1/users/me"),
        ("GET", "/api/v1/profiles/me"),
        ("GET", "/api/v1/preferences"),
        ("GET", "/api/v1/status/me"),
    ]

    for method, endpoint in endpoints:
        response = client.request(method, endpoint)

        assert response.status_code == 401, (
            f"{method} {endpoint}: "
            f"expected 401, got {response.status_code}: {response.text}"
        )


def test_public_api_rejects_invalid_token(client):
    """Public account endpoints must reject invalid JWTs."""
    headers = {
        "Authorization": "Bearer invalid-token",
    }

    response = client.get(
        "/api/v1/users/me",
        headers=headers,
    )

    assert response.status_code == 401, response.text


def test_public_api_rejects_wrong_token_type(
    client,
    internal_headers,
    registration_payload,
    cleanup_user,
):
    """A refresh token must not authenticate public APIs."""
    user_id = create_test_user(
        client,
        internal_headers,
        registration_payload,
    )
    cleanup_user(user_id)

    from app.core.config import settings

    now = datetime.now(UTC)

    payload = {
        "sub": str(user_id),
        "iss": settings.auth_jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "jti": str(uuid4()),
        "token_type": "refresh",
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401, response.text
