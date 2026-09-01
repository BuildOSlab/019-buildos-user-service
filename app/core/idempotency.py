"""
BuildOS User Service
Registration idempotency helpers.
"""

import hashlib
import json
from typing import Any


def create_request_hash(payload: dict[str, Any]) -> str:
    """Create a deterministic SHA-256 fingerprint for a request."""
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
