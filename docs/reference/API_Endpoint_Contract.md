# BuildOS User Service — API Endpoint Contract

**Service:** `019-buildos-user-service`
**Base API:** `/api/v1`
**Internal API:** `/internal/v1`
**Status:** Phase 1 endpoint contract

---

# 1. API Overview

The User Service is responsible for canonical user identity, profile, preferences, and account lifecycle.

It exposes two API surfaces:

```text
Public API
/api/v1/...

Internal Service API
/internal/v1/...
```

The public API is used by authenticated BuildOS clients.

The internal API is used by trusted BuildOS services such as the Authentication Service (`018-buildos-auth-service`).

---

# 2. Public User Endpoints

## 2.1 Get Current User

```http
GET /api/v1/users/me
```

### Authentication

Required:

```http
Authorization: Bearer <access_token>
```

The authenticated user's UUID is obtained from the JWT `sub` claim.

### Purpose

Returns the canonical user's public account information.

### Success

```http
200 OK
```

### Errors

```text
401 Unauthorized
404 Not Found
```

---

## 2.2 Update Current User

```http
PATCH /api/v1/users/me
```

### Authentication

Required.

### Request

```json
{
  "display_name": "Gerard"
}
```

### Allowed fields

```text
display_name
```

### Success

```http
200 OK
```

### Errors

```text
401 Unauthorized
404 Not Found
```

Unknown fields must be rejected.

---

# 3. Public Profile Endpoints

## 3.1 Get Current Profile

```http
GET /api/v1/profiles/me
```

### Authentication

Required.

### Success

```http
200 OK
```

Returns profile information including:

```text
first_name
last_name
bio
profile_photo_reference
country
timezone
language
visibility
completion_percentage
profile_metadata
created_at
updated_at
```

### Errors

```text
401 Unauthorized
404 Not Found
```

---

## 3.2 Update Current Profile

```http
PATCH /api/v1/profiles/me
```

### Authentication

Required.

### Request example

```json
{
  "first_name": "Gerard",
  "last_name": "Ugwu",
  "bio": "BuildOS developer",
  "country": "NG",
  "timezone": "Africa/Lagos",
  "language": "en",
  "visibility": "authenticated"
}
```

### Success

```http
200 OK
```

### Errors

```text
401 Unauthorized
404 Not Found
422 Unprocessable Entity
```

Only fields explicitly supplied by the client should be updated.

---

# 4. Public Preference Endpoints

## 4.1 List Preferences

```http
GET /api/v1/preferences
```

### Authentication

Required.

### Success

```http
200 OK
```

---

## 4.2 Get Preference

```http
GET /api/v1/preferences/{key}
```

### Authentication

Required.

### Example

```http
GET /api/v1/preferences/theme
```

### Success

```http
200 OK
```

### Errors

```text
401 Unauthorized
404 Not Found
```

---

## 4.3 Create Preference

```http
POST /api/v1/preferences
```

### Authentication

Required.

### Request

```json
{
  "key": "theme",
  "value": "dark"
}
```

### Success

```http
201 Created
```

### Errors

```text
401 Unauthorized
409 Conflict
422 Unprocessable Entity
```

---

## 4.4 Update Preference

```http
PUT /api/v1/preferences/{key}
```

### Authentication

Required.

### Request

```json
{
  "value": "light"
}
```

### Success

```http
200 OK
```

### Errors

```text
401 Unauthorized
404 Not Found
422 Unprocessable Entity
```

---

## 4.5 Delete Preference

```http
DELETE /api/v1/preferences/{key}
```

### Authentication

Required.

### Success

```http
204 No Content
```

### Errors

```text
401 Unauthorized
404 Not Found
```

---

# 5. Public Account Status Endpoint

## 5.1 Get Current Account Status

```http
GET /api/v1/status/me
```

### Authentication

Required.

### Success

```http
200 OK
```

### Response

```json
{
  "user_id": "82298225-a2af-4691-bc47-1514be4ceb88",
  "status": "pending",
  "is_active": false,
  "status_changed_at": null,
  "verification": {
    "status": "unverified",
    "level": "none"
  }
}
```

### Errors

```text
401 Unauthorized
404 Not Found
```

---

# 6. Internal Service Endpoints

These endpoints are **not client-facing**.

They are intended for trusted BuildOS services.

Primary consumer:

```text
018-buildos-auth-service
```

---

# 7. Internal Create User

## 7.1 Create Canonical User

```http
POST /internal/v1/users/create
```

### Authentication

Required:

```http
Authorization: Bearer <internal_api_key>
X-Service-ID: buildos-auth-service
Idempotency-Key: <unique-registration-key>
```

### Request

```json
{
  "email": "user@example.com",
  "phone": "+2348012345678",
  "username": "gerard",
  "first_name": "Gerard",
  "last_name": "Ugwu",
  "display_name": "Gerard",
  "country": "NG",
  "timezone": "Africa/Lagos",
  "language": "en"
}
```

At least one identity must be supplied:

```text
email
phone
username
```

### Success

```http
201 Created
```

### Response

```json
{
  "user_id": "82298225-a2af-4691-bc47-1514be4ceb88",
  "public_id": "usr_kot7uPXWWYriHyIoja1pybSS",
  "status": "pending",
  "created_at": "2026-09-01T22:11:10.901384+01:00"
}
```

### Errors

```text
400 Bad Request
401 Unauthorized
409 Conflict
422 Unprocessable Entity
500 Internal Server Error
```

---

# 8. Internal User Resolution

## 8.1 Resolve User Identity

```http
POST /internal/v1/users/resolve
```

### Authentication

Required.

### Request

```json
{
  "identifier": "user@example.com",
  "type": "email"
}
```

Supported types:

```text
email
phone
username
```

### Success

```http
200 OK
```

### Response

```json
{
  "user_id": "82298225-a2af-4691-bc47-1514be4ceb88",
  "status": "pending",
  "identities": [
    {
      "type": "email",
      "value": "user@example.com",
      "is_verified": false
    }
  ]
}
```

### Errors

```text
401 Unauthorized
404 Not Found
422 Unprocessable Entity
```

---

# 9. Internal User Status

## 9.1 Get User Status

```http
GET /internal/v1/users/{user_id}/status
```

### Authentication

Required.

### Path parameter

```text
user_id = canonical UUID
```

Example:

```http
GET /internal/v1/users/82298225-a2af-4691-bc47-1514be4ceb88/status
```

### Success

```http
200 OK
```

### Response

```json
{
  "user_id": "82298225-a2af-4691-bc47-1514be4ceb88",
  "status": "active",
  "is_active": true,
  "status_changed_at": "2026-09-01T22:30:00+01:00",
  "verification": {
    "status": "verified",
    "level": "contact_verified"
  }
}
```

### Errors

```text
401 Unauthorized
404 Not Found
422 Unprocessable Entity
```

---

# 10. Authentication Contract

All public authenticated endpoints expect an access token issued by:

```text
018-buildos-auth-service
```

Expected issuer:

```text
buildos-auth-service
```

Expected claims:

```text
sub
iss
aud
iat
exp
jti
token_type
```

The `sub` claim must contain the canonical 019 user UUID.

Example:

```json
{
  "sub": "82298225-a2af-4691-bc47-1514be4ceb88",
  "iss": "buildos-auth-service",
  "aud": "buildos-api",
  "token_type": "access"
}
```

019 must not create a second independent authentication/token system for normal client authentication.

---

# 11. Internal Authentication Contract

Trusted services authenticate using:

```http
Authorization: Bearer <internal-api-key>
X-Service-ID: buildos-auth-service
```

The internal API key must be supplied through secure environment configuration in production.

Development placeholder:

```text
change-me-in-production
```

---

# 12. Endpoint Ownership

| Endpoint                                  | Owner | Consumer        |
| ----------------------------------------- | ----- | --------------- |
| `GET /api/v1/users/me`                    | 019   | BuildOS clients |
| `PATCH /api/v1/users/me`                  | 019   | BuildOS clients |
| `GET /api/v1/profiles/me`                 | 019   | BuildOS clients |
| `PATCH /api/v1/profiles/me`               | 019   | BuildOS clients |
| `GET /api/v1/preferences`                 | 019   | BuildOS clients |
| `GET /api/v1/preferences/{key}`           | 019   | BuildOS clients |
| `POST /api/v1/preferences`                | 019   | BuildOS clients |
| `PUT /api/v1/preferences/{key}`           | 019   | BuildOS clients |
| `DELETE /api/v1/preferences/{key}`        | 019   | BuildOS clients |
| `GET /api/v1/status/me`                   | 019   | BuildOS clients |
| `POST /internal/v1/users/create`          | 019   | 018             |
| `POST /internal/v1/users/resolve`         | 019   | 018             |
| `GET /internal/v1/users/{user_id}/status` | 019   | 018             |

---

# 13. Registration Integration

The endpoint that connects 018 and 019 during registration is:

```http
POST /internal/v1/users/create
```

Expected flow:

```text
Client
   │
   │ register
   ▼
018 Auth
   │
   │ create canonical user
   ▼
019 User
   │
   │ user_id
   ▼
018 Auth
   │
   │ create credentials
   │ issue tokens
   ▼
Client
```

The `user_id` returned by 019 becomes the canonical identity used by 018.

---

# 14. Login Integration

The endpoint that connects 018 and 019 during login is:

```http
POST /internal/v1/users/resolve
```

Expected flow:

```text
Client
   │
   │ login(identifier, password)
   ▼
018 Auth
   │
   │ resolve identifier
   ▼
019 User
   │
   │ canonical user_id
   ▼
018 Auth
   │
   │ verify credentials
   │ issue access/refresh tokens
   ▼
Client
```

019 does not verify the password.

018 remains responsible for authentication.

---

# 15. Status Integration

018 can query:

```http
GET /internal/v1/users/{user_id}/status
```

This allows authentication decisions to respect the User Service account lifecycle.

Future event-driven synchronization should additionally allow:

```text
019 status changed
       ↓
USER_STATUS_CHANGED
       ↓
018
       ↓
invalidate/revoke authentication state
```

---

# 16. API Security Rules

The following rules apply to the entire endpoint contract:

### Public APIs

```text
Require valid BuildOS access token.
```

### Internal APIs

```text
Require service authentication.
```

### User identity

```text
Never trust user_id supplied by a normal client
when the authenticated JWT already identifies the user.
```

### Request schemas

Unexpected fields must be rejected.

### Cross-user access

A normal authenticated user must not be able to use the API to access or modify another user's account.

### Authentication errors

Do not expose sensitive authentication details that enable user enumeration.

---

# 17. Endpoint Contract Status

### Implemented and tested

```text
✅ GET    /api/v1/users/me
✅ PATCH  /api/v1/users/me

✅ GET    /api/v1/profiles/me
✅ PATCH  /api/v1/profiles/me

✅ GET    /api/v1/preferences
✅ GET    /api/v1/preferences/{key}
✅ POST   /api/v1/preferences
✅ PUT    /api/v1/preferences/{key}
✅ DELETE /api/v1/preferences/{key}

✅ GET    /api/v1/status/me

✅ POST   /internal/v1/users/create
✅ POST   /internal/v1/users/resolve
✅ GET    /internal/v1/users/{user_id}/status
```

### Validation

```text
33 tests passed
Ruff clean
Compilation clean
Database migrations applied
Internal API manually verified
JWT authentication manually/integration verified
```

---

# 18. Next Contract

The next API contract to document and implement is the **018 Auth Service endpoint contract**.

The two contracts will then be mapped together:

```text
018 Auth API
     │
     ├── Register ──────► 019 Create User
     │
     ├── Login ─────────► 019 Resolve User
     │
     ├── Account checks ─► 019 User Status
     │
     └── Logout ────────► 018 only
```

This gives BuildOS a clear separation:

> **019 answers "Who is this user?"**

> **018 answers "Can this user authenticate, and what authentication state do they have?"**
