# Agrync / Agroconnect V2

[![CI](https://github.com/ManuelMuRodriguez/Agrync/actions/workflows/ci.yml/badge.svg)](https://github.com/ManuelMuRodriguez/Agrync/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.13-3776ab?logo=python&logoColor=white)
![Node](https://img.shields.io/badge/Node.js-22-339933?logo=node.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61dafb?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178c6?logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ed?logo=docker&logoColor=white)

Agroindustrial facilities typically operate hundreds of sensors and PLCs from different manufacturers, each speaking its own protocol — Modbus, OPC-UA, or proprietary variants — creating isolated data silos that are expensive to integrate, hard to maintain, and impossible to monitor from a single interface. Bridging this IT/OT gap has traditionally required specialist engineering teams and bespoke middleware that few small or mid-size agro-processing plants can afford. Agrync is a full-stack platform — FastAPI backend and React + Vite frontend — built to eliminate that barrier: it provides a unified, open-source layer that speaks the industrial protocols already present on the plant floor, normalises the data, and exposes it through a modern web interface, so operators can configure, monitor and manage every sensor in the facility without writing a single line of integration code.

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

- Backend API: http://localhost:8000 (FastAPI app is mounted under `/api/v1`)
- Frontend: http://localhost:5173

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

Provide a MongoDB connection and other secrets as environment variables. Example `.env`:

```text
MONGODB_URI=mongodb://localhost:27017/agrync
SECRET_KEY=some-secret-key
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

## Configuration notes

- The backend uses Beanie + Motor to interact with MongoDB. Use a supported MongoDB server.
- Tasks and connectors (Modbus/OPC) are managed under `tasks/` and `routers/`. Review their configs before enabling production connectors.
- The project includes example JSON configuration files for bulk device/sensor import in `agrync_frontend/public` and `agrync_backend/static`.

---

## Troubleshooting

- If TypeScript or JSX errors appear in the frontend, run `npm install` in `agrync_frontend` to install dependencies and type packages.
- If the backend cannot connect to MongoDB, check `MONGODB_URI`, network access and that MongoDB is running.

---

## License

See [LICENSE](LICENSE).