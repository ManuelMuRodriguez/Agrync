
<p align="center">
  <img src="agrync_frontend/public/agrync.png" alt="Agrync Logo" width="200"/>
  # Agrync : A Modular Integration Layer for Industrial IoT interoperability in Agro-industrial Environments

</p>



[![CI](https://github.com/ManuelMuRodriguez/Agrync/actions/workflows/ci.yml/badge.svg)](https://github.com/ManuelMuRodriguez/Agrync/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.13-3776ab?logo=python&logoColor=white)
![Node](https://img.shields.io/badge/Node.js-22-339933?logo=node.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61dafb?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178c6?logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ed?logo=docker&logoColor=white)

<p align="center">
  <a href="https://agrync.readthedocs.io/">📚 Documentation</a> &nbsp;·&nbsp;
  <a href="https://agrync.readthedocs.io/en/latest/user-guide/introduction/">Introduction</a> &nbsp;·&nbsp;
  <a href="https://agrync.readthedocs.io/en/latest/user-guide/installation/">Installation</a> &nbsp;·&nbsp;
  <a href="https://agrync.readthedocs.io/en/latest/user-guide/first-steps/">First steps</a> &nbsp;·&nbsp;
  <a href="https://agrync.readthedocs.io/en/latest/technical/">Technical docs</a> &nbsp;·&nbsp;
  <a href="https://agrync.readthedocs.io/en/latest/technical/architecture/">Architecture</a>
</p>

---

Agroindustrial facilities typically operate hundreds of sensors and PLCs from different manufacturers, each speaking its own protocol — Modbus, OPC-UA, or proprietary variants — creating isolated data silos that are expensive to integrate, hard to maintain, and impossible to monitor from a single interface. Bridging this IT/OT gap has traditionally required specialist engineering teams and customized middleware that few small or mid-size agro-processing plants can afford. Agrync is a full-stack platform — FastAPI backend and React + Vite frontend — built to eliminate that barrier: it provides a unified, open-source layer that speaks the industrial protocols already present on the plant floor, normalises the data, and exposes it through a modern web interface, so operators can configure, monitor and manage every sensor in the facility without writing a single line of integration code.

---

**M. Muñoz\*** · J.J. León · M. Torres · A. Becerra-Terón · J.A. Sánchez  
*University of Almería, Spain* · \*Corresponding author: mmr411@ual.es

---

## Documentation

Full documentation — installation, configuration, usage guides and API reference — is available at:

**[https://agrync.readthedocs.io/](https://agrync.readthedocs.io/)**

---

## Key features

- Modbus TCP/IP reader: collect telemetry from Modbus-enabled devices and PLCs.
- OPC UA server: optionally expose collected data via an OPC UA server for OT integration.
- FIWARE integration: forward telemetry to FIWARE or similar IoT platforms for storage and analytics.
- Sensor management center: add, edit, or remove sensors one-by-one via the web UI, or perform bulk configuration by uploading a JSON file.
- Docker Compose based deployment: the repository is configured so the entire stack can be launched with Docker Compose.

---

## Repository layout

- `agrync_backend/` — FastAPI backend (includes `Dockerfile`)
- `agrync_frontend/` — Vite + React + TypeScript frontend (includes `Dockerfile`)
- `docker-compose.yml` — Docker Compose configuration for development
- `.github/workflows/ci.yml` — GitHub Actions CI pipeline

---

## Prerequisites

- Docker & Docker Compose (recommended)
- Node.js >= 18 (for frontend development)
- Python 3.11+ (for backend development)
- Git

---

## Launching the full stack (recommended)

The recommended way to run the entire system (backend + database + frontend) is using Docker Compose from the repository root:

```bash
docker compose up --build
```

After the services start:

| Service | URL | Notes |
|---|---|---|
| Frontend | http://localhost:5173 | React + Vite UI |
| Backend REST API | http://localhost:8000/api/v1 | FastAPI |
| Swagger / OpenAPI | http://localhost:8000/api/v1/docs | Interactive API docs |
| OPC UA Server | opc.tcp://localhost:4842 | Exposed by the backend container |
| FIWARE Orion | http://localhost:1026 | NGSI v2 Context Broker |
| MongoDB | localhost:27020 | Internal port 27017 |

To stop and remove containers:

```bash
docker compose down
```

---

## Backend — local development

1. Create and activate a virtual environment:

```bash
cd agrync_backend
python -m venv .venv
source .venv/bin/activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Environment variables

All environment variables must be provided before starting the backend. Full configuration reference is available at **[https://agrync.readthedocs.io/en/latest/technical/configuration/](https://agrync.readthedocs.io/en/latest/technical/configuration/)**.

Create a `.env` file in `agrync_backend/` (or export the variables directly):

```text
# ── MongoDB ────────────────────────────────────────────────
MONGO_URI=mongodb://localhost:27017

# ── Authentication (JWT) ───────────────────────────────────
ACCESS_TOKEN_SECRET_KEY=change-me-access
REFRESH_TOKEN_SECRET_KEY=change-me-refresh
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=1440
ADMIN_EMAIL=admin@example.com

# ── OPC UA Server ──────────────────────────────────────────
OPCUA_IP_PORT=4842
URL=opc.tcp://localhost:{OPCUA_IP_PORT}
URL_ADMIN=opc.tcp://localhost:{OPCUA_IP_PORT}
URI=urn:agrync:server
USERNAME_OPC=operator
PASSWORD_OPC=change-me
USERNAME_OPC_ADMIN=admin
PASSWORD_OPC_ADMIN=change-me
CERT=certificate/my_cert.der
PRIVATE_KEY=certificate/private_key.pem
CLIENT_CERT=certificate/client_cert.der
CLIENT_APP_URI=urn:agrync:client

# ── Modbus task ────────────────────────────────────────────
RECONNECTION_TIME=5

# ── FIWARE Orion ───────────────────────────────────────────
FIWARE_URL=http://orion:1026
FIWARE_SERVICE=agrync
FIWARE_SERVICE_PATH=/

# ── Telegram alerts (optional) ─────────────────────────────
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
ALERT_INTERVAL=60

# ── Logging ────────────────────────────────────────────────
LOG_CONFIG=logging.conf
LOG_MODBUS=ModbusLogger
LOG_OPC=OPCLogger
LOG_OPC_FIWARE=OPCtoFIWARELogger
```

4. Run the backend in development:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

5. API docs (Swagger/OpenAPI):

Open http://localhost:8000/api/v1/docs

---

## Frontend — local development

1. Install dependencies and run the dev server:

```bash
cd agrync_frontend
npm install
npm run dev
# or use pnpm/yarn
```

2. Dev server URL: http://localhost:5173

3. If the frontend needs a specific API URL, check `agrync_frontend/src/api` or environment configuration and set the appropriate base URL.

---

## Docker images (optional)

Build backend image:

```bash
docker build agrync_backend -t agrync-backend:latest
```

Build frontend image:

```bash
docker build agrync_frontend -t agrync-frontend:latest
```

---

## Background tasks

The core integration logic runs as three independent background processes managed from the Administration panel. See the "Docs" column for detailed documentation on each task.

| Task | Description | Docs |
|---|---|---|
| **Modbus** | Polls all configured Modbus TCP/IP devices at their configured intervals, decodes register values (Int16/32/64, Float32/64, endianness, scaling) and persists them in MongoDB (`LastVariable` + `HistoricalVariable`). Also subscribes to the OPC UA server to relay write-back commands to writable registers. | [→ docs](https://agrync.readthedocs.io/en/latest/technical/background-tasks/modbus/) |
| **ServerOPC** | Starts an OPC UA server (port 4842) secured with X.509 certificates (`Basic256Sha256 + SignAndEncrypt`). Exposes every Modbus variable as an OPC UA node and keeps their values in sync from the database. | [→ docs](https://agrync.readthedocs.io/en/latest/technical/background-tasks/server-opc/) |
| **OPCtoFIWARE** | Connects as an OPC UA client to ServerOPC, subscribes to all nodes, and forwards value changes to a FIWARE Orion Context Broker via NGSI v2 PATCH requests. Registers a webhook on Orion so that platform-side updates flow back to the database. Supports optional Telegram alerts on out-of-range values. | [→ docs](https://agrync.readthedocs.io/en/latest/technical/background-tasks/opc-to-fiware/) |

Tasks are started and stopped from the web UI (*Administration → Monitoring*) or via the REST API (`POST /api/v1/tasks/{name}/start`). ServerOPC and OPCtoFIWARE are locked tasks (they start and stop together as a pair).

---

## Configuration notes

- The backend uses Beanie + Motor to interact with MongoDB. Use a supported MongoDB server.
- Tasks and connectors (Modbus/OPC) are managed under `tasks/` and `routers/`. Review their configs before enabling production connectors.
- The project includes example JSON configuration files for bulk device/sensor import in `agrync_frontend/public` and `agrync_backend/static`.

---

## Troubleshooting

- If TypeScript or JSX errors appear in the frontend, run `npm install` in `agrync_frontend` to install dependencies and type packages.
- If the backend cannot connect to MongoDB, check `MONGODB_URI`, network access and that MongoDB is running.

---

## Running the tests

Full testing documentation is available at **[https://agrync.readthedocs.io/en/latest/technical/testing/](https://agrync.readthedocs.io/en/latest/technical/testing/)**.

### Backend (pytest)

The backend test suite uses an in-memory MongoDB mock — no running database or Docker is required.

```bash
cd agrync_backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-test.txt
pytest -v
```

To run a single file:

```bash
pytest tests/test_auth.py -v
```

Expected result: **99 passed, 1 xfailed**.

### Frontend — unit tests (Vitest)

```bash
cd agrync_frontend
npm install
npm run test -- --run
```

With coverage report:

```bash
npm run test -- --coverage
```

Expected result: **49 passed**.

### Frontend — end-to-end tests (Playwright)

E2E tests require the full stack to be running first:

```bash
# From the repository root
docker compose up -d

# Then, in a separate terminal
cd agrync_frontend
npx playwright test --config playwright.config.cjs
```

To run a single spec:

```bash
npx playwright test e2e/login.spec.cjs --config playwright.config.cjs
```

Expected result: **11 passed**. An HTML report can be opened with:

```bash
npx playwright show-report
```

---

## Screenshots

**Dashboard — real-time sensor values**

<p align="center">
  <img src="docs/images/dashboard-cards.png" alt="Dashboard with real-time sensor cards" width="800"/>
</p>

**Modbus device management**

<p align="center">
  <img src="docs/images/modbus-devices-table.png" alt="Modbus devices configuration table" width="800"/>
</p>

**Task monitoring — Modbus running**

<p align="center">
  <img src="docs/images/monitoring-modbus-running.png" alt="Monitoring panel showing the Modbus task running" width="800"/>
</p>

---

## License

See [LICENSE](LICENSE).