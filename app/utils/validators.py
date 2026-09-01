"""
BuildOS User Service
Input normalization and validation helpers.
"""

import re

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def normalize_email(value: str) -> str:
    """Normalize an email address."""
    normalized = value.strip().lower()

    if not EMAIL_PATTERN.fullmatch(normalized):
        raise ValueError("Invalid email format")

    return normalized


def normalize_phone(value: str) -> str:
    """Normalize a phone number to a basic E.164 representation."""
    normalized = re.sub(r"[\s().-]", "", value.strip())

    if not normalized.startswith("+"):
        raise ValueError("Invalid phone format")

    digits = normalized[1:]

    if not digits.isdigit() or not 7 <= len(digits) <= 15:
        raise ValueError("Invalid phone format")

    return normalized


def normalize_username(value: str) -> str:
    """Normalize a username."""
    normalized = value.strip().lower()

    if not normalized:
        raise ValueError("Invalid username format")

    return normalized


def normalize_identity(identity_type: str, value: str) -> str:
    """Normalize an identity according to its type."""
    identity_type = identity_type.strip().lower()

    if identity_type == "email":
        return normalize_email(value)

    if identity_type == "phone":
        return normalize_phone(value)

    if identity_type == "username":
        return normalize_username(value)

    return value.strip()
