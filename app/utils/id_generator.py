"""
BuildOS User Service
Public ID Generator
"""

import secrets
import string

from app.core.config import settings


def generate_public_id() -> str:
    """
    Generate a public-facing user ID with the configured prefix.

    Format: {prefix}_{24 random alphanumeric characters}
    Example: usr_01JXXXXXXXXXXXX
    """
    alphabet = string.ascii_letters + string.digits
    random_part = "".join(secrets.choice(alphabet) for _ in range(24))
    return f"{settings.public_id_prefix}_{random_part}"
