# BuildOS User Service — Standard Response & Error Contract

**Service:** `019-buildos-user-service`
**API Version:** `v1`
**Status:** Proposed standard for Phase 1/2 integration

---

# 1. Standard Success Response

All successful JSON API responses should use:

```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "req_01J...",
    "timestamp": "2026-09-01T22:30:00+01:00"
  }
}
```

## Fields

| Field             | Type              | Required | Description                        |
| ----------------- | ----------------- | -------: | ---------------------------------- |
| `success`         | boolean           |      Yes | Always `true`                      |
| `data`            | object/array/null |      Yes | Endpoint-specific response payload |
| `meta`            | object            |      Yes | Request/response metadata          |
| `meta.request_id` | string            |      Yes | Unique request correlation ID      |
| `meta.timestamp`  | datetime          |      Yes | Response timestamp in ISO-8601     |

---

# 2. Single Resource Response

Example:

```http
GET /api/v1/users/me
```

```json
{
  "success": true,
  "data": {
    "public_id": "usr_kot7uPXWWYriHyIoja1pybSS",
    "status": "active",
    "display_name": "Gerard",
    "last_active_at": "2026-09-01T22:30:00+01:00",
    "deactivated_at": null,
    "deleted_at": null,
    "created_at": "2026-09-01T21:00:00+01:00",
    "updated_at": "2026-09-01T22:30:00+01:00"
  },
  "meta": {
    "request_id": "req_01J...",
    "timestamp": "2026-09-01T22:30:00+01:00"
  }
}
```

---

# 3. Collection Response

For endpoints returning multiple resources:

```json
{
  "success": true,
  "data": [
    {
      "key": "theme",
      "value": "dark",
      "updated_at": "2026-09-01T22:00:00+01:00"
    },
    {
      "key": "language",
      "value": "en",
      "updated_at": "2026-09-01T22:00:00+01:00"
    }
  ],
  "meta": {
    "request_id": "req_01J...",
    "timestamp": "2026-09-01T22:30:00+01:00"
  }
}
```

---

# 4. Empty Success Response

For operations that have no response body:

```http
204 No Content
```

No JSON envelope is returned.

This applies to:

```http
DELETE /api/v1/preferences/{key}
```

---

# 5. Standard Error Response

Every JSON error response should use:

```json
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User not found.",
    "details": null
  },
  "meta": {
    "request_id": "req_01J...",
    "timestamp": "2026-09-01T22:30:00+01:00"
  }
}
```

---

# 6. Error Schema

## Error object

```json
{
  "code": "USER_NOT_FOUND",
  "message": "User not found.",
  "details": null
}
```

### Fields

| Field     | Type              | Required | Description                           |
| --------- | ----------------- | -------: | ------------------------------------- |
| `code`    | string            |      Yes | Stable machine-readable error code    |
| `message` | string            |      Yes | Safe human-readable message           |
| `details` | object/array/null |      Yes | Optional structured error information |

The `code` is the value clients should use for programmatic handling.

Clients should **not** branch on the human-readable `message`.

---

# 7. Validation Error

Validation failures should use:

```http
422 Unprocessable Entity
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
    "request_id": "req_01J...",
    "timestamp": "2026-09-01T22:30:00+01:00"
  }
}
```

---

# 8. Standard Error Codes

## Authentication

| HTTP | Code                            | Meaning                           |
| ---: | ------------------------------- | --------------------------------- |
|  401 | `AUTHENTICATION_REQUIRED`       | No authentication supplied        |
|  401 | `INVALID_ACCESS_TOKEN`          | Access token is invalid           |
|  401 | `ACCESS_TOKEN_EXPIRED`          | Access token has expired          |
|  401 | `INVALID_AUTHENTICATION_SCHEME` | Unsupported authentication scheme |

---

## Authorization / Service Authentication

| HTTP | Code                              | Meaning                               |
| ---: | --------------------------------- | ------------------------------------- |
|  401 | `SERVICE_AUTHENTICATION_REQUIRED` | Internal service credentials missing  |
|  401 | `INVALID_SERVICE_CREDENTIALS`     | Internal service credentials invalid  |
|  403 | `FORBIDDEN`                       | Authenticated caller lacks permission |

---

## Users

| HTTP | Code                    | Meaning                                               |
| ---: | ----------------------- | ----------------------------------------------------- |
|  404 | `USER_NOT_FOUND`        | User does not exist                                   |
|  409 | `USER_ALREADY_EXISTS`   | User conflicts with existing identity                 |
|  409 | `IDEMPOTENCY_CONFLICT`  | Same idempotency key used with different request data |
|  422 | `IDENTITY_REQUIRED`     | At least one identity is required                     |
|  422 | `INVALID_IDENTITY_TYPE` | Unsupported identity type                             |

---

## Preferences

| HTTP | Code                        | Meaning                                       |
| ---: | --------------------------- | --------------------------------------------- |
|  404 | `PREFERENCE_NOT_FOUND`      | Preference does not exist                     |
|  409 | `PREFERENCE_ALREADY_EXISTS` | Preference conflicts with existing preference |

---

## Profiles

| HTTP | Code                         | Meaning                      |
| ---: | ---------------------------- | ---------------------------- |
|  404 | `PROFILE_NOT_FOUND`          | Profile does not exist       |
|  422 | `INVALID_PROFILE_VISIBILITY` | Unsupported visibility value |

---

## Account Status

| HTTP | Code                        | Meaning                                       |
| ---: | --------------------------- | --------------------------------------------- |
|  404 | `USER_NOT_FOUND`            | User does not exist                           |
|  409 | `INVALID_STATUS_TRANSITION` | Requested lifecycle transition is not allowed |
|  422 | `INVALID_USER_STATUS`       | Unsupported status value                      |

---

## Infrastructure

| HTTP | Code                  | Meaning                             |
| ---: | --------------------- | ----------------------------------- |
|  409 | `RESOURCE_CONFLICT`   | Generic resource conflict           |
|  429 | `RATE_LIMITED`        | Request rate exceeded               |
|  500 | `INTERNAL_ERROR`      | Unexpected server failure           |
|  503 | `SERVICE_UNAVAILABLE` | Service temporarily unavailable     |
|  504 | `UPSTREAM_TIMEOUT`    | Required upstream service timed out |

---

# 9. Security Rules for Errors

Error responses must never expose:

```text
password hashes
passwords
JWT signing secrets
internal API keys
database credentials
database connection strings
stack traces
SQL statements
internal filesystem paths
raw exception messages
```

For example, do **not** return:

```json
{
  "error": {
    "message": "psycopg2.errors.UniqueViolation: duplicate key..."
  }
}
```

Instead:

```json
{
  "success": false,
  "error": {
    "code": "USER_ALREADY_EXISTS",
    "message": "A user with the supplied identity already exists.",
    "details": null
  },
  "meta": {
    "request_id": "req_01J..."
  }
}
```

---

# 10. Request ID

Every request should have a request ID.

Preferred behavior:

```text
Client
  │
  │ X-Request-ID: req_client_123
  ▼
019 User Service
  │
  │ response
  ▼
X-Request-ID: req_client_123
```

If the client does not provide one, 019 generates one.

The request ID must be included in:

```text
response metadata
application logs
error logs
service-to-service logs
```

For internal 018 ↔ 019 calls, the request ID should be propagated where possible.

---

# 11. Correlation ID

For distributed workflows, use a separate correlation ID where appropriate.

Example:

```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "req_01J...",
    "correlation_id": "corr_01J...",
    "timestamp": "2026-09-01T22:30:00+01:00"
  }
}
```

Use the correlation ID to connect a multi-service operation such as:

```text
018 Registration
      │
      ├── 019 Create User
      │
      ├── 018 Create Credentials
      │
      └── Issue Tokens
```

---

# 12. Internal API Errors

Internal endpoints use the same error envelope.

Example:

```http
POST /internal/v1/users/create
```

Duplicate identity:

```http
409 Conflict
```

```json
{
  "success": false,
  "error": {
    "code": "USER_ALREADY_EXISTS",
    "message": "A user with the supplied identity already exists.",
    "details": null
  },
  "meta": {
    "request_id": "req_01J...",
    "timestamp": "2026-09-01T22:30:00+01:00"
  }
}
```

Idempotency conflict:

```http
409 Conflict
```

```json
{
  "success": false,
  "error": {
    "code": "IDEMPOTENCY_CONFLICT",
    "message": "The idempotency key has already been used with different request data.",
    "details": null
  },
  "meta": {
    "request_id": "req_01J...",
    "timestamp": "2026-09-01T22:30:00+01:00"
  }
}
```

---

# 13. HTTP Status Rules

| HTTP Status | Usage                                      |
| ----------: | ------------------------------------------ |
|       `200` | Successful read/update                     |
|       `201` | Resource successfully created              |
|       `204` | Successful operation with no response body |
|       `400` | Malformed/invalid request                  |
|       `401` | Authentication failure                     |
|       `403` | Authenticated but not authorized           |
|       `404` | Resource not found                         |
|       `409` | Resource/state/idempotency conflict        |
|       `422` | Schema/business validation failure         |
|       `429` | Rate limited                               |
|       `500` | Unexpected server failure                  |
|       `503` | Service unavailable                        |
|       `504` | Upstream timeout                           |

---

# 14. Endpoint Response Mapping

| Endpoint                               | Success | Response data          |
| -------------------------------------- | ------: | ---------------------- |
| `GET /users/me`                        |   `200` | `UserResponse`         |
| `PATCH /users/me`                      |   `200` | `UserResponse`         |
| `GET /profiles/me`                     |   `200` | `ProfileResponse`      |
| `PATCH /profiles/me`                   |   `200` | `ProfileResponse`      |
| `GET /preferences`                     |   `200` | `PreferenceResponse[]` |
| `GET /preferences/{key}`               |   `200` | `PreferenceResponse`   |
| `POST /preferences`                    |   `201` | `PreferenceResponse`   |
| `PUT /preferences/{key}`               |   `200` | `PreferenceResponse`   |
| `DELETE /preferences/{key}`            |   `204` | No body                |
| `GET /status/me`                       |   `200` | `StatusResponse`       |
| `POST /internal/users/create`          |   `201` | `UserCreateResponse`   |
| `POST /internal/users/resolve`         |   `200` | `UserResolveResponse`  |
| `GET /internal/users/{user_id}/status` |   `200` | `UserStatusResponse`   |

---

# 15. Pydantic Contract

The implementation should introduce shared schemas equivalent to:

```python
class ResponseMeta(BaseModel):
    request_id: str
    correlation_id: str | None = None
    timestamp: datetime


class ApiResponse(BaseModel, Generic[T]):
    success: Literal[True] = True
    data: T
    meta: ResponseMeta


class ErrorDetail(BaseModel):
    code: str
    message: str


class ApiError(BaseModel):
    success: Literal[False] = False
    error: ErrorDetail
    meta: ResponseMeta
```

Validation errors may extend `details`:

```python
class ValidationErrorDetail(BaseModel):
    field: str
    code: str
    message: str
```

---

# 16. Client Contract

Clients should consume responses using:

```text
success
data
error.code
error.message
error.details
meta.request_id
meta.correlation_id
meta.timestamp
```

Client logic should primarily branch on:

```text
HTTP status
+
error.code
```

and not on:

```text
error.message
```

This keeps the API stable even when human-readable messages change.

---

# 17. Standardization Decision

Going forward, **019 User Service uses one response envelope across public and internal JSON APIs.**

Success:

```text
{
  success: true,
  data: ...,
  meta: ...
}
```

Error:

```text
{
  success: false,
  error: ...,
  meta: ...
}
```

The only exception is `204 No Content`, which intentionally has no response body.

This contract should be implemented **before the 018 ↔ 019 integration**, so 018 can consume a stable API rather than adapting to response formats that may later change.

