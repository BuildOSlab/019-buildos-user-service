"""
BuildOS User Service
Application Constants
"""

# ---------------------------------------------------------------------------
# User statuses
# ---------------------------------------------------------------------------

USER_STATUS_PENDING = "pending"
USER_STATUS_VERIFICATION_PENDING = "verification_pending"
USER_STATUS_ACTIVE = "active"
USER_STATUS_SUSPENDED = "suspended"
USER_STATUS_DEACTIVATED = "deactivated"
USER_STATUS_RESTRICTED = "restricted"
USER_STATUS_DELETED = "deleted"

VALID_USER_STATUSES = {
    USER_STATUS_PENDING,
    USER_STATUS_VERIFICATION_PENDING,
    USER_STATUS_ACTIVE,
    USER_STATUS_SUSPENDED,
    USER_STATUS_DEACTIVATED,
    USER_STATUS_RESTRICTED,
    USER_STATUS_DELETED,
}

# ---------------------------------------------------------------------------
# Identity types
# ---------------------------------------------------------------------------

IDENTITY_TYPE_EMAIL = "email"
IDENTITY_TYPE_PHONE = "phone"
IDENTITY_TYPE_USERNAME = "username"
IDENTITY_TYPE_EXTERNAL = "external_identity"

VALID_IDENTITY_TYPES = {
    IDENTITY_TYPE_EMAIL,
    IDENTITY_TYPE_PHONE,
    IDENTITY_TYPE_USERNAME,
    IDENTITY_TYPE_EXTERNAL,
}

# ---------------------------------------------------------------------------
# Profile visibility
# ---------------------------------------------------------------------------

PROFILE_VISIBILITY_PUBLIC = "public"
PROFILE_VISIBILITY_AUTHENTICATED = "authenticated"
PROFILE_VISIBILITY_PRIVATE = "private"

VALID_VISIBILITY_LEVELS = {
    PROFILE_VISIBILITY_PUBLIC,
    PROFILE_VISIBILITY_AUTHENTICATED,
    PROFILE_VISIBILITY_PRIVATE,
}

# ---------------------------------------------------------------------------
# Organization membership status
# ---------------------------------------------------------------------------

ORG_MEMBERSHIP_ACTIVE = "active"
ORG_MEMBERSHIP_INACTIVE = "inactive"

# ---------------------------------------------------------------------------
# Event types
# ---------------------------------------------------------------------------

EVENT_USER_CREATED = "USER_CREATED"
EVENT_USER_ACTIVATED = "USER_ACTIVATED"
EVENT_USER_SUSPENDED = "USER_SUSPENDED"
EVENT_USER_DEACTIVATED = "USER_DEACTIVATED"
EVENT_USER_REACTIVATED = "USER_REACTIVATED"
EVENT_USER_DELETED = "USER_DELETED"
EVENT_USER_RESTRICTED = "USER_RESTRICTED"
EVENT_USER_STATUS_CHANGED = "USER_STATUS_CHANGED"
EVENT_USER_PROFILE_UPDATED = "USER_PROFILE_UPDATED"
EVENT_USER_PREFERENCES_UPDATED = "USER_PREFERENCES_UPDATED"
