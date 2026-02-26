# Configuration

## Docker Compose services

Defined in `docker-compose.yml` at the repository root.

| Service | Image / Build | Internal port | Host port | Notes |
|---|---|---|---|---|
| `mongodb` | `mongo:latest` | `27017` | `27020` | Volume: `mongo_data:/data/db` |
| `backend` | `./agrync_backend` | `8000`, `4842` | `8000`, `4842` | Volume: `./agrync_backend` → `/Agrync/agrync_backend` |
| `frontend` | `./agrync_frontend` | `5173` | `5173` | Volume: source + named `node_modules` |
| `orion` | `telefonicaiot/fiware-orion:latest` | `1026` | `1026` | Uses `mongodb` as its store |

All services share the `agrync_network` bridge network.

---

## Backend environment variables

Create a `.env` file in `agrync_backend/routers/` (loaded by `routers/*.py` via `python-dotenv`).

### Authentication

| Variable | Example | Description |
|---|---|---|
| `ACCESS_TOKEN_SECRET_KEY` | `change-me-32chars` | JWT signing secret for access tokens |
| `REFRESH_TOKEN_SECRET_KEY` | `change-me-32chars` | JWT signing secret for refresh tokens |
| `ALGORITHM` | `HS256` | JWT signature algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token validity in minutes |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | `1440` | Refresh token validity in minutes (1 day) |
| `ADMIN_EMAIL` | `admin@example.com` | Email of the initial admin created on first startup |

---

## Task environment variables

Create a `.env` file in `agrync_backend/tasks/` (loaded by all task scripts via `python-dotenv`).

### OPC UA

| Variable | Example | Description |
|---|---|---|
| `OPCUA_IP_PORT` | `4842` | Port the OPC UA server listens on |
| `URL_ADMIN` | `opc.tcp://localhost:{OPCUA_IP_PORT}` | Admin client URL (`{OPCUA_IP_PORT}` is replaced at runtime) |
| `CERT` | `certificate/my_cert.der` | Path to server certificate (relative to `tasks/`) |
| `PRIVATE_KEY` | `certificate/private_key.pem` | Server private key |
| `CLIENT_CERT` | `certificate/client_cert.der` | Client certificate |
| `CLIENT_APP_URI` | `urn:agrync:client` | OPC UA application URI for the write-value client |
| `USERNAME_OPC_ADMIN` | `admin` | OPC UA username |
| `PASSWORD_OPC_ADMIN` | `password` | OPC UA password |
| `URI` | `urn:agrync:server` | OPC UA namespace URI |

### FIWARE

| Variable | Example | Description |
|---|---|---|
| `FIWARE_URL` | `http://orion:1026` | FIWARE Orion base URL |
| `BACKEND_URL` | `http://backend:8000/api/v1` | FastAPI backend URL (used by OPCtoFIWARE to register Orion subscription) |

### Tasks general

| Variable | Example | Description |
|---|---|---|
| `RECONNECTION_TIME` | `5` | Seconds between reconnection attempts |
| `LOG_CONFIG` | `logging.conf` | Path to Python logging configuration file |
| `LOG_MODBUS` | `ModbusLogger` | Logger name for the Modbus task |
| `LOG_OPC_FIWARE` | `OPCtoFIWARELogger` | Logger name for the OPCtoFIWARE task |

---

## Log rotation

Logs are configured via `tasks/logging.conf` using `ConcurrentRotatingFileHandler` (from `concurrent-log-handler`). Rotated log files are named with numeric suffixes (`Modbus.log.1`, `Modbus.log.2`, …).

---

## OPC UA certificates

Certificates are stored in `agrync_backend/tasks/certificate/`. To regenerate:

```bash
# Example using openssl — adjust subject fields as needed
openssl req -x509 -newkey rsa:2048 -keyout private_key.pem \
    -out my_cert.pem -days 365 -nodes
openssl x509 -outform der -in my_cert.pem -out my_cert.der
```

See `tasks/certificate/comandos.txt` for the exact commands used in this project.
