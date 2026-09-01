"""
BuildOS User Service
Pydantic API schemas.
"""

from app.schemas.admin import (
    AdminStatusUpdateRequest,
    AdminUserResponse,
    AdminUserUpdateRequest,
)
from app.schemas.identity import (
    IdentityCreateRequest,
    IdentityResponse,
    IdentityUpdateRequest,
)
from app.schemas.preferences import (
    PreferenceCreateRequest,
    PreferenceResponse,
    PreferenceUpdateRequest,
)
from app.schemas.profile import (
    ProfileCreateRequest,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.schemas.status import (
    StatusHistoryResponse,
    StatusLifecycleResponse,
    StatusResponse,
    StatusTransitionRequest,
)
from app.schemas.user import (
    ResolvedIdentity,
    UserCreateRequest,
    UserCreateResponse,
    UserDetailResponse,
    UserResolveRequest,
    UserResolveResponse,
    UserResponse,
    UserStatusResponse,
)

__all__ = [
    "AdminStatusUpdateRequest",
    "AdminUserResponse",
    "AdminUserUpdateRequest",
    "IdentityCreateRequest",
    "IdentityResponse",
    "IdentityUpdateRequest",
    "PreferenceCreateRequest",
    "PreferenceResponse",
    "PreferenceUpdateRequest",
    "ProfileCreateRequest",
    "ProfileResponse",
    "ProfileUpdateRequest",
    "ResolvedIdentity",
    "StatusHistoryResponse",
    "StatusLifecycleResponse",
    "StatusResponse",
    "StatusTransitionRequest",
    "UserCreateRequest",
    "UserCreateResponse",
    "UserDetailResponse",
    "UserResolveRequest",
    "UserResolveResponse",
    "UserResponse",
    "UserStatusResponse",
]
