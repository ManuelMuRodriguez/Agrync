# Authentication API

**Router prefix**: `/auth`  
**Tag**: `authentication`

---

## Conventions

All endpoints under `/auth` are **public** except where noted. The login endpoint uses `application/x-www-form-urlencoded` (OAuth2 Password flow).

---

## Endpoints

### POST `/auth/validate`

Activates a new user account and sets the initial password.

**Role required**: none (public)

**Request body** (`application/json`):

```json
{
    "email": "user@example.com",
    "password": "mysecret123",
    "password_confirmation": "mysecret123"
}
```

| Field | Type | Constraints |
|---|---|---|
| `email` | EmailStr | Must match an existing, inactive account. |
| `password` | string | Minimum 8 characters. |
| `password_confirmation` | string | Must equal `password`. |

**Responses**:

| Status | Description |
|---|---|
| `201` | `{"message": "Activation successful"}` |
| `400` | Passwords do not match / too short |
| `400` | User already activated |
| `403` | User does not exist |

---

### POST `/auth/login`

Authenticates a user and returns an access token. Also sets an `httpOnly` refresh token cookie.

**Role required**: none (public)

**Request body** (`application/x-www-form-urlencoded`):

| Field | Notes |
|---|---|
| `username` | User email address |
| `password` | Account password |

**Response `200`**:

```json
{
    "access_token": "<JWT>",
    "token_type": "bearer"
}
```

The response also sets:
```
Set-Cookie: refresh-Token=<JWT>; HttpOnly; Max-Age=<REFRESH_TOKEN_EXPIRE_MINUTES * 60>
```

| Status | Description |
|---|---|
| `200` | Token returned |
| `401` | Incorrect email or password / account not active |
| `400` | Email or password not provided |

---

### POST `/auth/refresh`

Exchanges the `refresh-Token` cookie for a new access token.

**Role required**: none (cookie-based)

**Response `201`**:

```json
{
    "access_token": "<JWT>",
    "token_type": "bearer"
}
```

| Status | Description |
|---|---|
| `201` | New access token returned |
| `401` | Refresh token missing or invalid |

---

### POST `/auth/register`

Creates a new (inactive) user account. The user must call `/auth/validate` to activate it.

**Role required**: `Administrator`

**Request body** (`application/json`):

```json
{
    "email": "newuser@example.com",
    "full_name": "María García",
    "role": "Editor"
}
```

| Status | Description |
|---|---|
| `201` | `{"message": "User created successfully"}` |
| `409` | Email already in use |
| `401` | Caller is not an administrator |

---

### GET `/auth/info`

Returns the identity of the currently authenticated user.

**Role required**: any authenticated user

**Response `200`** (`UserByToken`):

```json
{
    "id": "64a1f2...",
    "full_name": "María García",
    "role": "Editor"
}
```

---

### POST `/auth/logout`

Deletes the `refresh-Token` cookie, ending the session.

**Role required**: none

**Response `200`**:

```json
{"message": "Session closed successfully"}
```
