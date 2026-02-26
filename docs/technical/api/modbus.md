# Modbus API

**Router prefix**: `/modbus`  
**Tag**: `modbus`

All Modbus endpoints require the `Administrator` role.

---

## Bulk import

### POST `/modbus/upload`

Imports a JSON file containing devices, slaves, and variables. Creates new records and updates existing ones (upsert logic based on IP for devices, name for slaves/variables).

**Role required**: `Administrator`

**Request**: `multipart/form-data` with a single file field.

**Address offset**: the endpoint subtracts 1 from each variable address before storing it (Modbus protocol uses 0-based addressing internally).

**Upsert rules**:

- Existing device matched by IP — name must match, otherwise `422`.
- Existing slave matched by name — `slave_id` must match, otherwise `422`.
- Existing variable matched by name — `address` must match; mutable fields (`interval`, `writable`, `min_value`, `max_value`, `unit`) are updated.

**Response `200`**: `{"message": "Data processed successfully"}`

---

### GET `/modbus/download-template`

Returns the `modbus_template.json` example file for download.

**Response**: `FileResponse` (`application/json`)

---

## Device endpoints

### GET `/modbus/list`

Returns a flat list of all `ModbusDevice` documents (including embedded slaves and variables).

**Response `200`**: `list[ModbusDevice]`

---

### POST `/modbus/devices/list`

Returns a paginated, filtered, and sortable list of devices.

**Request body**: `FiltersPayload` (same structure as `/users/list`)

**Filterable fields**: `name` · `ip` · `createdAt` · `updatedAt`

**Response `200`** (`DevicesResponseList`): `{ data: [...], totalRowCount: N }`

---

### POST `/modbus/devices`

Creates a new Modbus device.

**Request body** (`DeviceInput`):

```json
{
    "name": "PumpRoom",
    "ip": "192.168.1.50"
}
```

| Status | Description |
|---|---|
| `201` | Device created |
| `422` | Name or IP already exists |

---

### PUT `/modbus/devices/{device_db_id}`

Updates name and/or IP of an existing device.

**Path parameter**: `device_db_id` — MongoDB ObjectId

| Status | Description |
|---|---|
| `200` | Updated or no changes detected |
| `404` | Device not found |
| `422` | Name or IP already used by another device |

---

### DELETE `/modbus/devices/{device_db_id}`

Deletes a device and all its slaves, variables, associated `GenericDevice`, `LastVariable`, and `HistoricalVariable` records.

| Status | Description |
|---|---|
| `200` | Deleted |
| `404` | Device not found |

---

## Slave endpoints

### POST `/modbus/slaves/list`

Returns a paginated list of slaves, optionally filtered by parent device.

**Request body**: `FiltersPayload` + optional `deviceSelect` field.

**Filterable fields**: `name` · `slave_id` · `createdAt` · `updatedAt`

**Response `200`** (`SlavesResponseList`): `{ data: [...], totalRowCount: N }`

---

### POST `/modbus/devices/{device_db_id}/slaves`

Creates a new slave within a device.

**Request body** (`SlaveInput`):

```json
{
    "name": "Pump1",
    "slave_id": 3
}
```

| Status | Description |
|---|---|
| `201` | Slave created |
| `404` | Parent device not found |
| `422` | `slave_id` already used / duplicate name |

---

### PUT `/modbus/devices/{device_db_id}/slaves/{slave_db_id}`

Updates slave name and/or `slave_id`.

| Status | Description |
|---|---|
| `200` | Updated |
| `404` | Device or slave not found |
| `422` | `slave_id` conflict |

---

### DELETE `/modbus/devices/{device_db_id}/slaves/{slave_db_id}`

Deletes a slave and all its variables, `GenericDevice`, `LastVariable`, and `HistoricalVariable` records.

| Status | Description |
|---|---|
| `200` | Deleted |
| `404` | Device or slave not found |

---

## Variable endpoints

### POST `/modbus/variables/list`

Returns a paginated list of variables, optionally filtered by parent device and slave.

**Request body**: `FiltersPayload` + optional `deviceSelect` / `deviceSlaveSelect` fields.

**Filterable fields**: `name` · `type` · `address` · `interval` · `unit`

**Response `200`** (`VariablesResponseList`): `{ data: [...], totalRowCount: N }`

---

### POST `/modbus/devices/{device_db_id}/slaves/{slave_db_id}/variables`

Creates a new variable within a slave.

**Request body** (`VariableInput`) — see [JSON Template Reference](../user-guide/reference/json-template.md) for all fields.

!!! note "Address offset"
    The address you provide in the UI is 1-based. The endpoint stores `address - 1` internally.

| Status | Description |
|---|---|
| `201` | Variable created |
| `404` | Device or slave not found |
| `422` | Address conflict / duplicate name |

---

### PUT `/modbus/devices/{device_db_id}/slaves/{slave_db_id}/variables/{variable_db_id}`

Updates mutable variable fields (`interval`, `writable`, `min_value`, `max_value`, `unit`).

`name`, `type`, and `address` are immutable after creation.

| Status | Description |
|---|---|
| `200` | Updated |
| `404` | Device, slave, or variable not found |

---

### DELETE `/modbus/devices/{device_db_id}/slaves/{slave_db_id}/variables/{variable_db_id}`

Deletes a variable and its `LastVariable` and `HistoricalVariable` records.

| Status | Description |
|---|---|
| `200` | Deleted |
| `404` | Device, slave, or variable not found |
