# BuildOS User Service — Complete Schema Models

**Service:** `019-buildos-user-service`
**API Version:** `v1`
**Schema Standard:** Pydantic v2

---

# 1. Schema Organization

The schema layer should be organized as:

```text
app/schemas/
├── __init__.py
├── common.py
├── errors.py
├── user.py
├── profile.py
├── preferences.py
├── status.py
└── admin.py
```

The schemas are divided into:

```text
Request schemas
Response schemas
Shared/common schemas
Error schemas
Enum/value schemas
```

---

# 2. Shared Common Schemas

## `app/schemas/common.py`

```python
from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class ResponseMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(min_length=1, max_length=100)
    correlation_id: str | None = Field(
        default=None,
        max_length=100,
    )
    timestamp: datetime


class ApiResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="forbid")

    success: Literal[True] = True
    data: T
    meta: ResponseMeta


class PaginationMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(min_length=1, max_length=100)
    correlation_id: str | None = Field(
        default=None,
        max_length=100,
    )
    timestamp: datetime
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)


class PaginatedResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="forbid")

    success: Literal[True] = True
    data: list[T]
    meta: PaginationMeta
```

---

# 3. Error Schemas

## `app/schemas/errors.py`

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(
        min_length=1,
        max_length=100,
    )
    message: str = Field(
        min_length=1,
        max_length=1000,
    )
    details: dict[str, object] | list[object] | None = None


class ApiErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: Literal[False] = False
    error: ErrorDetail
    meta: "ResponseMeta"
```

The forward reference should be resolved by importing `ResponseMeta`:

```python
from app.schemas.common import ResponseMeta
```

Therefore the final version should use:

```python
from app.schemas.common import ResponseMeta


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=1000)
    details: dict[str, object] | list[object] | None = None


class ApiErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: Literal[False] = False
    error: ErrorDetail
    meta: ResponseMeta
```

---

# 4. Validation Error Schemas

Validation errors need field-level information.

```python
class ValidationErrorItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=1000)


class ValidationErrorDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fields: list[ValidationErrorItem]


class ValidationErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: Literal[False] = False
    error: ErrorDetail
    meta: ResponseMeta
```

Example:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": {
      "fields": [
        {
          "field": "email",
          "code": "INVALID_EMAIL",
          "message": "Invalid email address."
        }
      ]
    }
  },
  "meta": {
    "request_id": "req_123",
    "correlation_id": null,
    "timestamp": "2026-09-01T22:30:00+01:00"
  }
}
```

---

# 5. User Schemas

## `app/schemas/user.py`

### User creation request

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str | None = Field(
        default=None,
        max_length=255,
    )
    phone: str | None = Field(
        default=None,
        max_length=30,
    )
    username: str | None = Field(
        default=None,
        max_length=50,
    )

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    display_name: str | None = Field(
        default=None,
        max_length=100,
    )

    country: str | None = Field(
        default=None,
        min_length=2,
        max_length=2,
    )

    timezone: str = Field(
        default="Africa/Lagos",
        max_length=100,
    )
    language: str = Field(
        default="en",
        max_length=20,
    )
```

---

# 6. User Update Request

```python
class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(
        default=None,
        max_length=100,
    )
```

Only `display_name` is currently mutable through this endpoint.

---

# 7. User Creation Response

```python
class UserCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    public_id: str = Field(
        min_length=1,
        max_length=32,
    )
    status: str = Field(
        min_length=1,
        max_length=20,
    )
    created_at: datetime
```

---

# 8. User Response

```python
class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    public_id: str
    status: str
    display_name: str | None

    last_active_at: datetime | None
    deactivated_at: datetime | None
    deleted_at: datetime | None

    created_at: datetime
    updated_at: datetime
```

The public response deliberately does **not** expose:

```text
internal UUID
idempotency_key
idempotency_hash
password information
internal database fields
```

---

# 9. Identity Schemas

```python
class UserResolveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(
        min_length=1,
        max_length=255,
    )
    type: str = Field(
        min_length=1,
        max_length=20,
    )


class ResolvedIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(
        min_length=1,
        max_length=20,
    )
    value: str = Field(
        min_length=1,
        max_length=255,
    )
    is_verified: bool
```

---

# 10. User Resolution Response

```python
class UserResolveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    status: str
    identities: list[ResolvedIdentity]
```

This response is primarily consumed by:

```text
018-buildos-auth-service
```

The canonical UUID is the important integration field.

---

# 11. User Detail Response

```python
class UserDetailResponse(UserResponse):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    profile: object | None = None
    identities: list[ResolvedIdentity] = Field(
        default_factory=list,
    )
```

Sensitive identity information should only be returned where the endpoint contract explicitly permits it.

---

# 12. Profile Schemas

## `app/schemas/profile.py`

```python
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProfileCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(
        default=None,
        max_length=100,
    )
    last_name: str | None = Field(
        default=None,
        max_length=100,
    )
    bio: str | None = Field(
        default=None,
        max_length=1000,
    )
    profile_photo_reference: str | None = Field(
        default=None,
        max_length=500,
    )
    country: str | None = Field(
        default=None,
        max_length=100,
    )
    timezone: str = Field(
        default="Africa/Lagos",
        max_length=100,
    )
    language: str = Field(
        default="en",
        max_length=20,
    )
    visibility: str = Field(
        default="authenticated",
        max_length=20,
    )
    profile_metadata: dict[str, Any] = Field(
        default_factory=dict,
    )
```

---

# 13. Profile Update Request

```python
class ProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(
        default=None,
        max_length=100,
    )
    last_name: str | None = Field(
        default=None,
        max_length=100,
    )
    bio: str | None = Field(
        default=None,
        max_length=1000,
    )
    profile_photo_reference: str | None = Field(
        default=None,
        max_length=500,
    )
    country: str | None = Field(
        default=None,
        max_length=100,
    )
    timezone: str | None = Field(
        default=None,
        max_length=100,
    )
    language: str | None = Field(
        default=None,
        max_length=20,
    )
    visibility: str | None = Field(
        default=None,
        max_length=20,
    )
    profile_metadata: dict[str, Any] | None = None
```

---

# 14. Profile Response

```python
from datetime import datetime


class ProfileResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    first_name: str | None
    last_name: str | None
    bio: str | None
    profile_photo_reference: str | None

    country: str | None
    timezone: str
    language: str
    visibility: str

    completion_percentage: int = Field(
        ge=0,
        le=100,
    )

    profile_metadata: dict[str, Any]

    created_at: datetime
    updated_at: datetime
```

---

# 15. Preference Schemas

## `app/schemas/preferences.py`

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PreferenceCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(
        min_length=1,
        max_length=100,
    )
    value: str = Field(
        max_length=1000,
    )


class PreferenceUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: str = Field(
        max_length=1000,
    )


class PreferenceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    key: str
    value: str
    updated_at: datetime
```

---

# 16. Status Schemas

## `app/schemas/status.py`

```python
from pydantic import BaseModel, ConfigDict, Field


class StatusTransitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(
        min_length=1,
        max_length=20,
    )
    reason: str | None = Field(
        default=None,
        max_length=1000,
    )
```

This schema should **not** be exposed to ordinary self-service users.

It is intended for controlled internal/admin lifecycle operations.

---

# 17. Status History Response

```python
from datetime import datetime


class StatusHistoryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    from_status: str
    to_status: str
    reason: str | None
    actor_id: str | None
    created_at: datetime
```

---

# 18. Status Response

```python
class StatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    status: str
    is_active: bool
    status_changed_at: datetime | None = None

    verification: dict[str, str]
```

---

# 19. Status Lifecycle Response

```python
class StatusLifecycleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    status: str
    is_active: bool
    status_changed_at: datetime | None = None
    history: list[StatusHistoryResponse]
```

---

# 20. Verification Schema

The current verification response should be promoted from an untyped dictionary to a dedicated schema.

```python
class VerificationStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    level: str
```

Then:

```python
class StatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    status: str
    is_active: bool
    status_changed_at: datetime | None = None
    verification: VerificationStatus
```

And:

```python
class UserStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    status: str
    is_active: bool
    status_changed_at: datetime | None = None
    verification: VerificationStatus
```

This is preferred over:

```python
verification: dict[str, str]
```

because the API contract becomes explicit.

---

# 21. Admin Schemas

## `app/schemas/admin.py`

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminUserUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(
        default=None,
        max_length=100,
    )


class AdminStatusUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(
        min_length=1,
        max_length=20,
    )
    reason: str | None = Field(
        default=None,
        max_length=1000,
    )


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    public_id: str
    status: str
    display_name: str | None

    last_active_at: datetime | None
    deactivated_at: datetime | None
    deleted_at: datetime | None

    created_at: datetime
    updated_at: datetime
```

Admin schemas remain defined but admin endpoints should not be enabled until the actual authorization/role contract is confirmed.

---

# 22. Authentication Token Contract

019 does not issue the normal BuildOS access token.

The JWT consumed by 019 should have a dedicated claims model for validation/documentation:

```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AccessTokenClaims(BaseModel):
    model_config = ConfigDict(extra="allow")

    sub: UUID
    iss: str
    aud: str
    iat: datetime
    exp: datetime
    jti: str
    token_type: str
```

Expected:

```text
iss = buildos-auth-service
aud = buildos-api
token_type = access
sub = canonical user UUID
```

The token itself remains owned and issued by 018.

---

# 23. Internal Service Authentication

Internal request authentication is not a normal public API schema.

The contract is:

```http
Authorization: Bearer <internal-api-key>
X-Service-ID: buildos-auth-service
```

For registration:

```http
Idempotency-Key: <unique-registration-key>
```

---

# 24. Standard Response Type Mapping

The endpoint schemas should be wrapped using `ApiResponse[T]`.

Examples:

```python
ApiResponse[UserResponse]
```

```python
ApiResponse[ProfileResponse]
```

```python
ApiResponse[list[PreferenceResponse]]
```

```python
ApiResponse[StatusResponse]
```

```python
ApiResponse[UserCreateResponse]
```

```python
ApiResponse[UserResolveResponse]
```

```python
ApiResponse[UserStatusResponse]
```

---

# 25. Standard Error Mapping

All API errors should resolve to:

```python
ApiErrorResponse
```

with:

```python
ErrorDetail
```

Examples:

```text
USER_NOT_FOUND
USER_ALREADY_EXISTS
IDEMPOTENCY_CONFLICT
IDENTITY_REQUIRED
INVALID_IDENTITY_TYPE
PREFERENCE_NOT_FOUND
PREFERENCE_ALREADY_EXISTS
PROFILE_NOT_FOUND
INVALID_PROFILE_VISIBILITY
INVALID_STATUS_TRANSITION
INVALID_USER_STATUS
AUTHENTICATION_REQUIRED
INVALID_ACCESS_TOKEN
ACCESS_TOKEN_EXPIRED
FORBIDDEN
SERVICE_AUTHENTICATION_REQUIRED
INVALID_SERVICE_CREDENTIALS
RATE_LIMITED
INTERNAL_ERROR
SERVICE_UNAVAILABLE
UPSTREAM_TIMEOUT
```

---

# 26. Complete Schema Export

`app/schemas/__init__.py` should expose the public schema contract:

```python
from app.schemas.common import (
    ApiResponse,
    PaginatedResponse,
    PaginationMeta,
    ResponseMeta,
)
from app.schemas.errors import (
    ApiErrorResponse,
    ErrorDetail,
    ValidationErrorItem,
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
    UserStatusResponse,
    VerificationStatus,
)
from app.schemas.user import (
    ResolvedIdentity,
    UserCreateRequest,
    UserCreateResponse,
    UserDetailResponse,
    UserResolveRequest,
    UserResolveResponse,
    UserResponse,
    UserUpdateRequest,
)

__all__ = [
    "ApiErrorResponse",
    "ApiResponse",
    "ErrorDetail",
    "PaginatedResponse",
    "PaginationMeta",
    "PreferenceCreateRequest",
    "PreferenceResponse",
    "PreferenceUpdateRequest",
    "ProfileCreateRequest",
    "ProfileResponse",
    "ProfileUpdateRequest",
    "ResolvedIdentity",
    "ResponseMeta",
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
    "UserUpdateRequest",
    "ValidationErrorItem",
    "VerificationStatus",
]
```

---

# 27. Final Schema Architecture

The complete contract is:

```text
                    ┌─────────────────────┐
                    │   Common Schemas    │
                    │                     │
                    │ ApiResponse[T]      │
                    │ ResponseMeta        │
                    │ PaginatedResponse   │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
       User Schemas      Profile Schemas   Preference Schemas
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                         Status Schemas
                               │
                               ▼
                        Admin Schemas


                    ┌─────────────────────┐
                    │    Error Schemas    │
                    │                     │
                    │ ApiErrorResponse    │
                    │ ErrorDetail         │
                    │ ValidationError     │
                    └─────────────────────┘
```

---

# 28. Schema Rules

The following rules are now part of the API contract:

1. All request models use `extra="forbid"`.
2. Public response models use `from_attributes=True` where ORM serialization is required.
3. Canonical `user_id` is a UUID.
4. `public_id` is the external `usr_...` identifier.
5. 018 remains the JWT issuer.
6. 019 validates 018-issued access tokens.
7. Passwords and password hashes never appear in 019 response schemas.
8. Internal database fields never appear in public schemas.
9. Error codes are stable machine-readable identifiers.
10. Human-readable error messages are not API identifiers.
11. `request_id` is present in every JSON response envelope.
12. `correlation_id` is supported for distributed workflows.
13. `204 No Content` has no JSON response envelope.
14. Admin schemas exist independently from admin endpoint authorization.
15. `StatusTransitionRequest` is not exposed as unrestricted public self-service functionality.
16. Verification should use a dedicated `VerificationStatus` model rather than an untyped dictionary.
17. Response envelopes are generic and reusable across every API resource.

---

# 29. Implementation Gate

Before connecting `018-buildos-auth-service` to `019-buildos-user-service`, the following must be true:

```text
☐ Common response schemas implemented
☐ Error schemas implemented
☐ Validation error handler standardized
☐ User schemas finalized
☐ Profile schemas finalized
☐ Preference schemas finalized
☐ Status schemas finalized
☐ Internal API schemas finalized
☐ OpenAPI output reviewed
☐ Existing 33 integration tests updated
☐ All tests pass
☐ No existing endpoint contract is accidentally changed
☐ 018 integration contract verified against these schemas
```

**This schema layer is the contract boundary.** Once finalized, endpoint implementations and the 018 client should consume these models rather than defining ad-hoc response dictionaries.

