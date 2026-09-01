from app.core.idempotency import create_request_hash


def test_request_hash_is_deterministic():
    payload_a = {
        "email": "user@example.com",
        "username": "user",
        "country": "NG"
    }
    payload_b = {
        "country": "NG",
        "username": "user",
        "email": "user@example.com",
    }

    assert create_request_hash(payload_a) == create_request_hash(payload_b)


def test_request_hash_changes_when_payload_changes():
    payload_a = {"email": "user@example.com"}
    payload_b = {"email": "other@example.com"}

    assert create_request_hash(payload_a) != create_request_hash(payload_b)
