import pytest

from app.utils.validators import (
    normalize_email,
    normalize_phone,
    normalize_username,
)


def test_normalize_email():
    assert normalize_email("  USER@Example.COM ") == "user@example.com"


def test_normalize_username():
    assert normalize_username("  Gerard_Test  ") == "gerard_test"


def test_normalize_phone():
    assert normalize_phone(" +234 801 234 5001 ") == "+2348012345001"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "not-an-email",
        "user@",
    ],
)
def test_invalid_email_is_rejected(value):
    with pytest.raises(ValueError):
        normalize_email(value)
