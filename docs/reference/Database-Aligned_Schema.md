# 019 BuildOS User Service — Database-Aligned Schema Contract

## 1. Schema Principle

The schema layer follows this rule:

```text
SQLAlchemy Model
       ↓
Database truth
       ↓
Pydantic schema
       ↓
API contract
```

A Pydantic model must not introduce a field that has no corresponding domain/database meaning.

A database field does not automatically become publicly exposed.

---

# 2. User Database Model → API Schemas

## Database-owned fields

```text
users
├── id
├── public_id
├── idempotency_key
├── idempotency_hash
├── status
├── display_name
├── last_active_at
├── deactivated_at
├── deleted_at
├── created_at
└── updated_at
```

## Public representation

```python
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: str
    status: str
    display_name: str | None
    last_active_at: datetime | None
    deactivated_at: datetime | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

### Deliberately hidden

```text
id
idempotency_key
idempotency_hash
```

These are internal service/database fields.

---

# 3. Internal User Creation

The internal create operation needs the information required to construct the actual user and its identities/profile.

```python
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
        max_length=100,
    )
    last_name: str | None = Field(
        default=None,
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

The service generates:

```text
id
public_id
status
idempotency_hash
created_at
updated_at
```

The `idempotency_key` comes from the request header, not from the JSON body.

---

# 4. User Creation Response

```python
class UserCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    public_id: str
    status: str
    created_at: datetime
```

This is intentionally different from `UserResponse`.

The internal response exposes:

```text
user_id
```

because 018 needs the canonical UUID.

The public user response does not need to expose the internal UUID.

---

# 5. User Identity Schema

The identity database relationship should be represented explicitly.

```python
class UserIdentityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str
    value: str
    is_verified: bool
```

For internal resolution:

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
```

Response:

```python
class UserResolveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    status: str
    identities: list[UserIdentityResponse]
```

This is the key 018 → 019 login contract.

---

# 6. User Detail Schema

Instead of:

```python
profile: Any | None
```

use an explicit profile schema.

```python
class UserDetailResponse(UserResponse):
    model_config = ConfigDict(from_attributes=True)

    profile: ProfileResponse | None = None
    identities: list[UserIdentityResponse] = Field(
        default_factory=list,
    )
```

Organizations and role references should only be included when their actual API contract requires them.

They should not be fabricated into the current public user response.

---

# 7. User Profile Schema

The profile relationship is represented by:

```python
class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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

# 8. Profile Creation

```python
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

# 9. Profile Update

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

# 10. Preference Schemas

The preference model is represented as a key/value record.

```python
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
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str
    updated_at: datetime
```

No artificial preference fields should be introduced.

---

# 11. Verification Schema

Verification is currently represented as a derived API value based on identity verification state.

Therefore:

```python
class VerificationStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    level: str
```

Then:

```python
class UserStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    status: str
    is_active: bool
    status_changed_at: datetime | None
    verification: VerificationStatus
```

---

# 12. Status History

The status-history relationship becomes:

```python
class StatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    from_status: str
    to_status: str
    reason: str | None
    actor_id: str | None
    created_at: datetime
```

Lifecycle response:

```python
class StatusLifecycleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    status: str
    is_active: bool
    status_changed_at: datetime | None
    history: list[StatusHistoryResponse]
```

---

# 13. Status Transition Request

The existing status transition model remains an operation schema:

```python
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

This is an **operation request**, not a representation of the database model.

It must remain protected and must not be exposed as unrestricted self-service.

---

# 14. Organization Relationship

The User model has an organization relationship.

The API should eventually have a dedicated schema:

```python
class UserOrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Fields must match the actual UserOrganization ORM model.
    ...
```

Do **not** implement guessed fields here.

The actual `UserOrganization` ORM model must be treated as the source of truth before exposing this relationship.

---

# 15. Role Reference Relationship

The User model also has:

```text
role_references
```

This is a reference to role ownership/assignment data.

Because BuildOS has a dedicated Role Service, 019 should not invent role definitions.

Use a dedicated schema only after the actual ORM model is verified:

```python
class UserRoleReferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Exact fields must mirror UserRoleReference.
    ...
```

The role service remains authoritative for role definitions.

---

# 16. Database vs API Visibility

| Database field     | API visibility           |
| ------------------ | ------------------------ |
| `id`               | Internal                 |
| `public_id`        | Public                   |
| `idempotency_key`  | Internal                 |
| `idempotency_hash` | Internal                 |
| `status`           | Public                   |
| `display_name`     | Public                   |
| `last_active_at`   | Public where appropriate |
| `deactivated_at`   | Public where appropriate |
| `deleted_at`       | Public where appropriate |
| `created_at`       | Public                   |
| `updated_at`       | Public                   |
| Identity records   | Controlled               |
| Profile            | Controlled               |
| Preferences        | Owner only               |
| Status history     | Controlled               |
| Organizations      | Controlled               |
| Role references    | Controlled               |

---

# 17. Canonical Identity Rule

There are two identifiers with different purposes:

```text
user.id
   ↓
Canonical UUID
   ↓
018 ↔ 019 service-to-service identity


user.public_id
   ↓
usr_...
   ↓
External BuildOS user identifier
```

They must never be treated as interchangeable.

---

# 18. Standard Response Envelope

All JSON API resources are wrapped with:

```python
class ResponseMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    correlation_id: str | None = None
    timestamp: datetime


class ApiResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="forbid")

    success: Literal[True] = True
    data: T
    meta: ResponseMeta
```

Example:

```json
{
  "success": true,
  "data": {
    "public_id": "usr_...",
    "status": "active",
    "display_name": "Gerard"
  },
  "meta": {
    "request_id": "req_123",
    "correlation_id": "corr_123",
    "timestamp": "2026-09-01T22:30:00+01:00"
  }
}
```

---

# 19. Standard Error Envelope

```python
class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    details: dict[str, object] | list[object] | None = None


class ApiErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: Literal[False] = False
    error: ErrorDetail
    meta: ResponseMeta
```

---

# 20. Important Correction From Previous Schema Draft

The following should **not** be blindly added:

```python
profile: Any
organizations: list[Any]
roles: list[Any]
```

Nor should we create fields merely because BuildOS may eventually need them.

The ORM model is the authority.

For relationships whose exact ORM structure has not yet been verified:

```text
UserOrganization
UserRoleReference
```

we leave their response schemas pending rather than guessing.

---

# 21. Final Schema-to-Database Map

```text
users
 │
 ├── UserResponse
 │
 ├── UserCreateRequest
 │
 ├── UserCreateResponse
 │
 ├── UserUpdateRequest
 │
 └── UserDetailResponse
 │
 ├── user_identities
 │      └── UserIdentityResponse
 │
 ├── user_profiles
 │      ├── ProfileCreateRequest
 │      ├── ProfileUpdateRequest
 │      └── ProfileResponse
 │
 ├── user_preferences
 │      ├── PreferenceCreateRequest
 │      ├── PreferenceUpdateRequest
 │      └── PreferenceResponse
 │
 ├── user_status_history
 │      └── StatusHistoryResponse
 │
 ├── user_organizations
 │      └── UserOrganizationResponse
 │
 └── user_role_references
        └── UserRoleReferenceResponse
```

---

# 22. Contract Rule

Before adding any schema field:

```text
Does it exist in the actual ORM model?
        │
        ├── YES → Is it appropriate for this API?
        │             │
        │             ├── YES → expose it
        │             └── NO  → keep internal
        │
        └── NO → Do not invent it
```

This keeps the 019 API synchronized with the real PostgreSQL schema and prevents the API contract from drifting away from the database.

---

# 23. Next Required Verification

Before we call the schema contract final, inspect the actual ORM definitions for:

```text
app/database/models/user.py
app/database/models/user_identity.py
app/database/models/user_profile.py
app/database/models/user_preference.py
app/database/models/user_status_history.py
app/database/models/user_organization.py
app/database/models/user_role_reference.py
```

Then produce the final **field-by-field ORM → Pydantic mapping**.

Only after that should we modify the schema files.
