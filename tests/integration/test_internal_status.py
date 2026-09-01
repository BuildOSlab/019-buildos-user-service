import uuid

from app.core.constants import USER_STATUS_DELETED
from app.database.models.user import User
from app.database.session import SESSION_LOCAL
from app.services.status_service import StatusService


def test_get_pending_user_status(
    client,
    internal_headers,
    registration_payload,
    cleanup_user,
):
    response = client.post(
        "/internal/v1/users/create",
        headers={
            **internal_headers,
            "Idempotency-Key": f"status-pending-{uuid.uuid4()}",
        },
        json=registration_payload,
    )

    assert response.status_code == 201

    data = response.json()
    user_id = data["user_id"]
    cleanup_user(user_id)

    response = client.get(
        f"/internal/v1/users/{user_id}/status",
        headers=internal_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == user_id
    assert body["status"] == "pending"
    assert body["is_active"] is False
    assert body["verification"]["status"] == "unverified"
    assert body["verification"]["level"] == "none"


def test_get_deleted_user_status(
    client,
    internal_headers,
    registration_payload,
    cleanup_user,
):
    response = client.post(
        "/internal/v1/users/create",
        headers={
            **internal_headers,
            "Idempotency-Key": f"status-deleted-{uuid.uuid4()}",
        },
        json=registration_payload,
    )

    assert response.status_code == 201

    data = response.json()
    user_id = data["user_id"]
    cleanup_user(user_id)

    db = SESSION_LOCAL()
    try:
        user = db.get(User, user_id)
        assert user is not None

        service = StatusService(db)
        service.transition(user_id, USER_STATUS_DELETED)

        db.commit()
    finally:
        db.close()

    response = client.get(
        f"/internal/v1/users/{user_id}/status",
        headers=internal_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == user_id
    assert body["status"] == "deleted"
    assert body["is_active"] is False


def test_get_status_unknown_user(
    client,
    internal_headers,
):
    user_id = uuid.uuid4()

    response = client.get(
        f"/internal/v1/users/{user_id}/status",
        headers=internal_headers,
    )

    assert response.status_code == 404


def test_get_status_invalid_api_key(
    client,
    registration_payload,
    internal_headers,
):
    response = client.post(
        "/internal/v1/users/create",
        headers={
            **internal_headers,
            "Idempotency-Key": f"status-auth-{uuid.uuid4()}",
        },
        json=registration_payload,
    )

    assert response.status_code == 201
    user_id = response.json()["user_id"]

    response = client.get(
        f"/internal/v1/users/{user_id}/status",
        headers={
            "Authorization": "Bearer wrong-key",
            "X-Service-ID": "buildos-auth-service",
        },
    )

    assert response.status_code == 401


def test_get_status_missing_service_identity(
    client,
    registration_payload,
    internal_headers,
):
    response = client.post(
        "/internal/v1/users/create",
        headers={
            **internal_headers,
            "Idempotency-Key": f"status-service-{uuid.uuid4()}",
        },
        json=registration_payload,
    )

    assert response.status_code == 201
    user_id = response.json()["user_id"]

    response = client.get(
        f"/internal/v1/users/{user_id}/status",
        headers={
            "Authorization": internal_headers["Authorization"],
        },
    )

    assert response.status_code == 401
