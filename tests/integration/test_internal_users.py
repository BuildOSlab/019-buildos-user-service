def test_create_user_success(
    client,
    internal_headers,
    registration_payload,
    cleanup_user,
):
    response = client.post(
        "/internal/v1/users/create",
        headers={
            **internal_headers,
            "Idempotency-Key": "integration-create-success-001",
        },
        json=registration_payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"]
    assert data["public_id"].startswith("usr_")
    assert data["status"] == "pending"
    assert data["created_at"]

    cleanup_user(data["user_id"])


def test_create_user_idempotency_replay(
    client,
    internal_headers,
    registration_payload,
    cleanup_user,
):
    idempotency_key = f"integration-replay-{registration_payload['username']}"

    first = client.post(
        "/internal/v1/users/create",
        headers={
            **internal_headers,
            "Idempotency-Key": idempotency_key,
        },
        json=registration_payload,
    )

    assert first.status_code == 201

    first_data = first.json()

    second = client.post(
        "/internal/v1/users/create",
        headers={
            **internal_headers,
            "Idempotency-Key": idempotency_key,
        },
        json=registration_payload,
    )

    assert second.status_code == 201

    second_data = second.json()

    assert second_data["user_id"] == first_data["user_id"]
    assert second_data["public_id"] == first_data["public_id"]
    assert second_data["status"] == first_data["status"]

    cleanup_user(first_data["user_id"])


def test_create_user_idempotency_conflict(
    client,
    internal_headers,
    registration_payload,
    cleanup_user,
):
    idempotency_key = f"integration-conflict-{registration_payload['username']}"

    first = client.post(
        "/internal/v1/users/create",
        headers={
            **internal_headers,
            "Idempotency-Key": idempotency_key,
        },
        json=registration_payload,
    )

    assert first.status_code == 201

    first_data = first.json()

    conflicting_payload = {
        **registration_payload,
        "display_name": "Different Registration",
    }

    second = client.post(
        "/internal/v1/users/create",
        headers={
            **internal_headers,
            "Idempotency-Key": idempotency_key,
        },
        json=conflicting_payload,
    )

    assert second.status_code == 409

    data = second.json()

    assert data["detail"]["code"] == "IDEMPOTENCY_CONFLICT"

    cleanup_user(first_data["user_id"])


def test_create_user_rejects_missing_authentication(
    client,
    registration_payload,
):
    response = client.post(
        "/internal/v1/users/create",
        headers={
            "Idempotency-Key": "integration-missing-auth-001",
        },
        json=registration_payload,
    )

    assert response.status_code == 401


def test_create_user_rejects_invalid_api_key(
    client,
    registration_payload,
):
    response = client.post(
        "/internal/v1/users/create",
        headers={
            "Authorization": "Bearer wrong-key",
            "X-Service-ID": "buildos-auth-service",
            "Idempotency-Key": "integration-invalid-auth-001",
        },
        json=registration_payload,
    )

    assert response.status_code == 401


def test_create_user_rejects_missing_service_identity(
    client,
    registration_payload,
):
    response = client.post(
        "/internal/v1/users/create",
        headers={
            "Authorization": "Bearer change-me-in-production",
            "Idempotency-Key": "integration-missing-service-id-001",
        },
        json=registration_payload,
    )

    assert response.status_code == 401
