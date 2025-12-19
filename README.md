docker compose up --build
docker compose down
git add .
git commit -m "Initial commit"
git push -u origin main
docker build -f Dockerfile.backend -t agrync-backend:latest .
docker build -f Dockerfile.frontend -t agrync-frontend:latest .
# Agrync / Agroconnect V2

Agrync is a full-stack platform to collect, manage and visualize telemetry from industrial and IoT devices. It includes a FastAPI backend and a React + Vite frontend. The project is designed to bridge multiple industrial protocols and make sensor management simple for agroindustrial plants.

---

## Key features

- Modbus TCP/IP reader: collect telemetry from Modbus-enabled devices and PLCs.
- OPC UA server: optionally expose collected data via an OPC UA server for OT integration.
- FIWARE integration: forward telemetry to FIWARE or similar IoT platforms for storage and analytics.
- Sensor management center: add, edit, or remove sensors one-by-one via the web UI, or perform bulk configuration by uploading a JSON file.
- Docker Compose based deployment: the repository is configured so the entire stack can be launched with Docker Compose.

---

## Repository layout

- `agrync_backend/` — FastAPI backend
- `agrync_frontend/` — Vite + React + TypeScript frontend
- `docker-compose.yml` — Docker Compose configuration for development
- `Dockerfile.backend`, `Dockerfile.frontend` — Dockerfiles for building images

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
docker build -f Dockerfile.backend -t agrync-backend:latest .
```

Build frontend image:

```bash
docker build -f Dockerfile.frontend -t agrync-frontend:latest .
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

## Suggested improvements

- Add i18n (react-i18next) to the frontend for proper localization.
- Add unit and integration tests (pytest for backend; Jest/Vitest for frontend).
- Add GitHub Actions CI to lint, test and build on PRs.

---

## License

Add a `LICENSE` file (for example MIT) at the repository root.

---

## Next steps I can do for you

- Run a workspace search and translate any remaining Spanish UI strings in the frontend.
- Create a `.env.example` listing environment variables used by backend and frontend.
- Create a `CONTRIBUTING.md` and a basic GitHub Actions workflow for CI.

Tell me which of these you want me to do next and I will proceed.