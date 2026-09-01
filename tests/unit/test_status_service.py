from app.services.status_service import StatusService


def test_pending_allows_activation():
    allowed = StatusService.ALLOWED_TRANSITIONS["pending"]

    assert "active" in allowed


def test_active_allows_deactivation():
    allowed = StatusService.ALLOWED_TRANSITIONS["active"]

    assert "deactivated" in allowed


def test_deleted_has_no_allowed_transitions():
    assert StatusService.ALLOWED_TRANSITIONS["deleted"] == set()
