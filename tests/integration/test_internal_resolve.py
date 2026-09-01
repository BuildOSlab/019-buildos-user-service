def test_resolve_user_by_email(
    client,
    internal_headers,
    registration_payload,
    cleanup_user,
):
    create_response = client.post(
        "/internal/v1/users/create",
        headers={
            **internal_headers,
            "Idempotency-Key": f"resolve-email-{registration_payload['username']}",
        },
        json=registration_payload,
    )

    assert create_response.status_code == 201
    created = create_response.json()
    cleanup_user(created["user_id"])

    response = client.post(
        "/internal/v1/users/resolve",
        headers=internal_headers,
        json={
            "type": "email",
            "identifier": registration_payload["email"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == created["user_id"]
    assert data["status"] == "pending"

    identities = {
        identity["type"]: identity
        for identity in data["identities"]
    }

    assert identities["email"]["value"] == registration_payload["email"]
    assert identities["phone"]["value"] == registration_payload["phone"]
    assert identities["username"]["value"] == registration_payload["username"]


def test_resolve_user_by_phone(
    client,
    internal_headers,
    registration_payload,
    cleanup_user,
):
    create_response = client.post(
        "/internal/v1/users/create",
        headers={
            **internal_headers,
            "Idempotency-Key": f"resolve-phone-{registration_payload['username']}",
        },
        json=registration_payload,
    )

    assert create_response.status_code == 201
    created = create_response.json()
    cleanup_user(created["user_id"])

    response = client.post(
        "/internal/v1/users/resolve",
        headers=internal_headers,
        json={
            "type": "phone",
            "identifier": registration_payload["phone"],
        },
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == created["user_id"]


def test_resolve_user_by_username(
    client,
    internal_headers,
    registration_payload,
    cleanup_user,
):
    create_response = client.post(
        "/internal/v1/users/create",
        headers={
            **internal_headers,
            "Idempotency-Key": f"resolve-username-{registration_payload['username']}",
        },
        json=registration_payload,
    )

    assert create_response.status_code == 201
    created = create_response.json()
    cleanup_user(created["user_id"])

    response = client.post(
        "/internal/v1/users/resolve",
        headers=internal_headers,
        json={
            "type": "username",
            "identifier": registration_payload["username"],
        },
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == created["user_id"]


def test_resolve_unknown_identifier(
    client,
    internal_headers,
):
    response = client.post(
        "/internal/v1/users/resolve",
        headers=internal_headers,
        json={
            "type": "email",
            "identifier": "does-not-exist@example.com",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["code"] == "IDENTITY_NOT_FOUND"


def test_resolve_rejects_unsupported_identity_type(
    client,
    internal_headers,
):
    response = client.post(
        "/internal/v1/users/resolve",
        headers=internal_headers,
        json={
            "type": "passport",
            "identifier": "ABC123",
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"]["code"] == "VALIDATION_FAILED"


def test_resolve_rejects_invalid_api_key(
    client,
    registration_payload,
):
    response = client.post(
        "/internal/v1/users/resolve",
        headers={
            "Authorization": "Bearer wrong-key",
            "X-Service-ID": "buildos-auth-service",
        },
        json={
            "type": "email",
            "identifier": registration_payload["email"],
        },
    )

    assert response.status_code == 401


def test_resolve_rejects_missing_service_identity(
    client,
    registration_payload,
):
    response = client.post(
        "/internal/v1/users/resolve",
        headers={
            "Authorization": "Bearer change-me-in-production",
        },
        json={
            "type": "email",
            "identifier": registration_payload["email"],
        },
    )

    assert response.status_code == 401