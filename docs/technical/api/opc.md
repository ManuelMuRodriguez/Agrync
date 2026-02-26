# OPC UA API

**Router prefix**: `/opc`  
**Tag**: `opc`

---

## Endpoints

### POST `/opc/write-value/{user_id}`

Writes a value to an OPC UA variable node via the running `ServerOPC` task.

**Role required**: `Administrator` or `Editor`

!!! warning "Prerequisites"
    Both the task identified by `deviceType` and the `ServerOPC` task must be in the `running` state. The request will fail with `400` otherwise.

**Path parameter**: `user_id` — MongoDB ObjectId of the requesting user.

**Request body** (`VariableWriteInput`):

```json
{
    "nameGenericDevice": "Device1-Slave1",
    "nameVariable": "OutletTemp",
    "value": 42.5,
    "deviceType": "Modbus"
}
```

| Field | Type | Description |
|---|---|---|
| `nameGenericDevice` | string | Full device-slave name (`<Device>-<Slave>`). Must be in the user's device list. |
| `nameVariable` | string | Variable name as configured in the Modbus hierarchy. |
| `value` | number | Value to write. |
| `deviceType` | NameTask | Task type: `Modbus` · `ServerOPC` · `OPCtoFIWARE`. |

**Access control**:

- An `Editor` can only write to devices assigned to their own `user_id`.
- An `Administrator` can write to any device regardless of `user_id`.

**Responses**:

| Status | Description |
|---|---|
| `200` | Value written successfully |
| `400` | Variable is read-only (`writable = false`) |
| `400` | Modbus or OPC task is not running |
| `403` | User not allowed to modify this device |
| `404` | Device, variable, or task not found |

## OPC UA connection details

The backend connects to the OPC UA server as a privileged client using certificate-based security (`SecurityPolicyBasic256Sha256`, `SignAndEncrypt`). The connection parameters are loaded from `tasks/.env`:

| Variable | Description |
|---|---|
| `OPCUA_IP_PORT` | OPC UA server address (e.g. `opc.tcp://localhost:4842`) |
| `URL_ADMIN` | Full admin endpoint URL (includes `{OPCUA_IP_PORT}` placeholder) |
| `CERT` | Path to server certificate (`.der`) |
| `PRIVATE_KEY` | Path to client private key |
| `CLIENT_CERT` | Path to client certificate |
| `CLIENT_APP_URI` | OPC UA application URI for the client |
| `USERNAME_OPC_ADMIN` | OPC UA admin username |
| `PASSWORD_OPC_ADMIN` | OPC UA admin password |
| `URI` | OPC UA namespace URI |
