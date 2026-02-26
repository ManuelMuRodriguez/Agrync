# Users API

**Router prefix**: `/users`  
**Tag**: `users`

---

## Endpoints

### POST `/users/list`

Returns a paginated, filtered, and sortable list of all users.

**Role required**: `Administrator`

**Request body** (`FiltersPayload`):

```json
{
    "columnFilters": [{"id": "role", "value": "Editor"}],
    "columnFilterFns": {"role": "contains"},
    "sorting": [{"id": "full_name", "desc": false}],
    "globalFilter": "",
    "pagination": {"pageIndex": 0, "pageSize": 10}
}
```

**Response `200`** (`UsersResponseList`):

```json
{
    "data": [
        {
            "id": "64a1f2...",
            "email": "user@example.com",
            "full_name": "María García",
            "role": "Editor",
            "active": true,
            "devices": ["Device1-Slave1"],
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-15T10:30:00Z"
        }
    ],
    "totalRowCount": 1
}
```

**Filter modes** (`columnFilterFns`): `contains` · `startsWith` · `endsWith`

**Filterable fields**: `email` · `full_name` · `role` · `active` · `createdAt` · `updatedAt`

---

### PUT `/users/{user_id}`

Updates email, full name, and role for a user.

**Role required**: `Administrator`

**Path parameter**: `user_id` — MongoDB ObjectId

**Request body**:

```json
{
    "email": "updated@example.com",
    "full_name": "Updated Name",
    "role": "Administrador"
}
```

| Status | Description |
|---|---|
| `200` | User updated |
| `404` | User not found |
| `401` | Cannot modify another admin |
| `422` | Email already in use |

---

### GET `/users/{user_id}/name`

Returns the full name of the authenticated user. Users can only query their own name.

**Role required**: any authenticated user (own account only)

**Response `200`**: plain string with the full name.

---

### PATCH `/users/{user_id}/name`

Updates the full name of the authenticated user.

**Role required**: any authenticated user (own account only)

**Request body**:

```json
{"full_name": "New Name"}
```

| Status | Description |
|---|---|
| `200` | Name updated |
| `401` | Attempt to modify another user's name |

---

### PATCH `/users/{user_id}/password`

Changes the password of the authenticated user.

**Role required**: any authenticated user (own account only)

**Request body**:

```json
{
    "password": "current_password",
    "new_password": "new_secure_pass",
    "new_password_confirmation": "new_secure_pass"
}
```

| Status | Description |
|---|---|
| `200` | Password changed |
| `400` | New passwords do not match |
| `400` | New password same as current |
| `401` | Current password incorrect |

---

### PATCH `/users/{user_id}/email`

Changes the email address of the authenticated user.

**Role required**: any authenticated user (own account only)

**Request body**:

```json
{
    "email": "current@example.com",
    "new_email": "new@example.com",
    "new_email_confirmation": "new@example.com"
}
```

| Status | Description |
|---|---|
| `200` | Email changed |
| `400` | New emails do not match |
| `401` | Current email incorrect |
| `401` | New email same as current |
| `422` | Email already taken by another account |

---

### DELETE `/users/{user_id}`

Deletes a user and their device assignments.

**Role required**: `Administrator`

!!! warning
    Cannot delete your own account or another administrator.

| Status | Description |
|---|---|
| `200` | User deleted |
| `404` | User not found |
| `401` | Self-delete or admin-delete attempted |

---

### GET `/users/{user_id}/devices`

Returns the list of device names assigned to a user.

**Role required**: `Administrator`

**Response `200`**: `["Device1-Slave1", "Device2-Slave3"]`

---

### GET `/users/{user_id}/devices/available`

Returns device names **not yet assigned** to the user.

**Role required**: `Administrator`

**Response `200`**: `["Device3-Slave1"]`

---

### PATCH `/users/{user_id}/devices`

Replaces the full device assignment list for a user.

**Role required**: `Administrator`

**Request body**:

```json
{"names": ["Device1-Slave1", "Device2-Slave3"]}
```

| Status | Description |
|---|---|
| `200` | Devices updated |
| `400` | One or more device names do not exist |
| `401` | Cannot modify another admin's devices |
