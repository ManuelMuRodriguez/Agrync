# Agrync: IoT Industrial Telemetry Collection and Management Platform

## Executive Summary

Agrync is a full-stack platform designed for the collection, management and visualisation of telemetry data from industrial and IoT devices. The system implements a modern approach to integrating multiple industrial protocols (Modbus TCP/IP, OPC UA) and facilitates interoperability with standard IoT platforms such as FIWARE, enabling centralised storage, analysis and visualisation of data in agroindustrial facilities.

---

## 1. Introduction and Context

### 1.1 Problem Statement
Traditional agroindustrial plants require the integration of multiple devices and sensors that use different communication protocols. These devices generate large volumes of telemetry data that must be captured, stored and analysed to optimise production processes. Existing solutions tend to be:

- **Fragmented**: require multiple decoupled systems for each protocol
- **Complex**: demand manual configuration and specialised technical experts
- **Costly**: involve significant infrastructure investments
- **Poorly scalable**: make it difficult to add new sensors or devices

### 1.2 Proposed Solution
Agrync addresses these challenges through a unified platform that:

- Integrates multiple industrial protocols in a single system
- Provides an intuitive web interface for sensor management
- Supports both manual configuration and bulk import via JSON files
- Facilitates interoperability with IoT standards (FIWARE)
- Uses Docker containers for simplified deployment

---

## 2. System Architecture

### 2.1 General Structure

```
Agrync
├── Backend (FastAPI + Python)
│   ├── REST API for device management
│   ├── Modbus TCP/IP connectors
│   ├── OPC UA server
│   ├── FIWARE integration
│   ├── User management and authentication
│   └── MongoDB database
│
└── Frontend (React + TypeScript + Vite)
    ├── Web user interface
    ├── Task management and monitoring
    ├── Variable visualisation
    ├── Device configuration
    └── User authentication
```

### 2.2 Main Components

#### **Backend (agrync_backend/)**

**Core technologies:**
- Framework: FastAPI (Python 3.11+)
- Database: MongoDB (via Beanie + Motor)
- Modbus industrial protocol: TCP/IP reading
- OPC UA server: exposure of collected data
- IoT integration: FIWARE client for data forwarding

**Directory structure:**

| Directory | Purpose |
|-----------|---------|
| `routers/` | REST endpoints organised by domain (auth, fiware, modbus, opc, task, user, generic) |
| `models/` | Data schemas (Pydantic) and ORM models (Beanie) |
| `tasks/` | Asynchronous services: Modbus readers, OPC server, FIWARE integration |
| `utils/` | Shared utilities (date management, passwords, tokens) |
| `static/` | Static files (JSON templates, downloads) |

**Main endpoints:**
- `POST /api/v1/auth/login` — User authentication
- `GET/POST /api/v1/devices` — Device management
- `POST /api/v1/tasks/modbus` — Modbus task configuration
- `POST /api/v1/tasks/opc` — OPC server configuration
- `POST /api/v1/fiware/push` — Data push to FIWARE

#### **Frontend (agrync_frontend/)**

**Core technologies:**
- Framework: React 19+
- Language: TypeScript
- Build tool: Vite
- Styles: Modern CSS

**Page structure:**
- Authentication (login/registration)
- Main dashboard
- Modbus device management
- Variable configuration
- Task monitoring
- User administration
- Configuration centre

**Application layers:**

| Layer | Responsibility |
|-------|---------------|
| `pages/` | Full-page components |
| `components/` | Reusable components (tables, forms, cards) |
| `api/` | HTTP clients (Axios) for each domain |
| `hooks/` | Custom hooks (authentication, generic data) |
| `lib/` | Shared utilities and configuration |
| `types/` | TypeScript definitions of shared types |

---

## 3. Key Technical Features

### 3.1 Modbus TCP/IP Connectivity

**How it works:**
1. The user configures a Modbus slave by specifying:
   - Device IP address
   - TCP port (typically 502)
   - Slave ID
2. The system runs an asynchronous task that periodically:
   - Connects to the device
   - Reads specified registers (coils, input registers, holding registers)
   - Stores values in MongoDB
   - Reports connection errors

**Protocol:**
- Modbus TCP/IP (RFC 1006)
- Reading of multiple data types: coils, discrete inputs, input registers, holding registers
- Support for multiple simultaneous slaves

### 3.2 OPC UA Server

**Functionality:**
- Exposes variables read from Modbus as OPC UA nodes
- Allows OPC UA clients (SCADA systems, monitoring tools) to connect
- Real-time value synchronisation

**Configuration:**
- Configurable port
- Optional authentication
- Security certificates in `tasks/certificate/`

### 3.3 FIWARE Integration

**Purpose:**
- Forward telemetry data to FIWARE platforms
- Facilitate storage in time-series databases
- Integration with standard IoT ecosystems

**Flow:**
1. Data collected from Modbus → MongoDB
2. FIWARE task → reads from MongoDB
3. Transformation to FIWARE format
4. HTTP POST to FIWARE server

### 3.4 Sensor and Variable Management

**Manual configuration:**
- Web interface for creating/editing sensors one by one
- Assignment of names, units and validation ranges

**Bulk import:**
- Upload of JSON files with a predefined structure
- Template available at `agrync_backend/static/downloads/modbus_template.json`
- Automatic schema validation

**JSON template example:**
```json
{
  "sensores": [
    {
      "nombre": "Temperatura Invernadero A",
      "dispositivo_modbus_id": "192.168.1.100",
      "puerto": 502,
      "esclavo": 1,
      "registro": 100,
      "tipo": "temperatura",
      "unidad": "°C",
      "factor_escala": 0.1
    }
  ]
}
```

---

## 4. Installation and Launch Procedures

### 4.1 Option 1: Full Deployment with Docker Compose (Recommended)

**Prerequisites:**
- Docker Engine 20.10+
- Docker Compose 1.29+
- Minimum 2 GB RAM available
- Ports 8000 (backend), 5173 (frontend) and 27017 (MongoDB) free

**Steps:**

```bash
# 1. Clone repository
git clone https://github.com/ManuelMuRodriguez/Agrync.git
cd Agrync

# 2. Configure environment variables (optional)
cat > .env << EOF
MONGODB_URI=mongodb://mongo:27017/agrync
SECRET_KEY=your-secret-key-here
FIWARE_URL=http://fiware:4041
FIWARE_SERVICE=agrync
FIWARE_SERVICEPATH=/agrync
EOF

# 3. Start services
docker compose up --build

# 4. Verify status
# Backend API: http://localhost:8000/api/v1/docs
# Frontend: http://localhost:5173
# MongoDB: localhost:27017
```

**Started services:**
- `agrync-backend` — FastAPI on port 8000
- `agrync-frontend` — React app on port 5173
- `mongo` — MongoDB database on port 27017
- `fiware` (optional) — FIWARE platform

**Stop services:**
```bash
docker compose down
```

### 4.2 Option 2: Local Development (Backend)

**Requirements:**
- Python 3.11+
- pip or poetry
- MongoDB running (local or remote)

**Steps:**

```bash
# 1. Navigate to backend
cd agrync_backend

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or on Windows:
# .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
export MONGODB_URI=mongodb://localhost:27017/agrync
export SECRET_KEY=dev-secret-key

# 5. Run server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 6. Access API documentation
# Swagger UI: http://localhost:8000/api/v1/docs
# ReDoc: http://localhost:8000/api/v1/redoc
```

**Execution notes:**
- `--reload`: Restarts automatically on code changes
- Hot-reload enabled for rapid development

### 4.3 Option 3: Local Development (Frontend)

**Requirements:**
- Node.js 18+
- npm, yarn or pnpm

**Steps:**

```bash
# 1. Navigate to frontend
cd agrync_frontend

# 2. Install dependencies
npm install
# or: yarn install, pnpm install

# 3. Configure API base (if needed)
# Edit src/api/axios.ts with the backend URL
# e.g.: http://localhost:8000/api/v1

# 4. Start development server
npm run dev

# 5. Access application
# http://localhost:5173
```

**Development features:**
- Hot Module Replacement (HMR) — changes reflected instantly
- TypeScript strict mode — type validation at development time
- ESLint configuration — code quality analysis

### 4.4 Building Individual Docker Images

**Backend:**
```bash
docker build -f Dockerfile.backend -t agrync-backend:latest .
docker run -p 8000:8000 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017/agrync \
  agrync-backend:latest
```

**Frontend:**
```bash
docker build -f Dockerfile.frontend -t agrync-frontend:latest .
docker run -p 5173:5173 agrync-frontend:latest
```

---

## 5. Data Flow and Operation

### 5.1 Configuration Flow

```
User (Web UI)
    ↓
[React Frontend]
    ↓ POST /api/v1/devices
[FastAPI Backend]
    ↓
[Pydantic Validation]
    ↓
[MongoDB]
    ↓ Confirmation
[Frontend] ← Device configured
```

### 5.2 Data Collection Flow

```
[Asynchronous Modbus Task]
    ↓ TCP/IP Connection
[Modbus Device]
    ↓ Register reading
[Modbus Task] ← Values read
    ↓ Transformation and validation
[MongoDB] ← Reading storage
    ↓
[OPC UA Server] ← Value synchronisation
    ↓
[OPC UA Clients] ← Variables available
```

### 5.3 FIWARE Integration Flow

```
[MongoDB] ← Historical data
    ↓
[FIWARE Task]
    ↓ Transformation to FIWARE format
[FIWARE API]
    ↓
[FIWARE time-series database]
    ↓
[Dashboards and analysis]
```

### 5.4 Authentication Flow

```
User enters credentials
    ↓
[Frontend] → POST /api/v1/auth/login
    ↓
[Backend] → Validation in MongoDB
    ↓ JWT token generated
[Frontend] ← Token stored in localStorage
    ↓
[Subsequent requests] include Authorization: Bearer <token>
```

---

## 6. Main Data Models

### 6.1 User Schema

```python
class User(BaseModel):
    email: str  # Unique identifier
    password_hash: str  # Stored with salt
    full_name: str
    role: Literal["admin", "operator", "viewer"]
    active: bool
    created_at: datetime
    updated_at: datetime
```

### 6.2 Modbus Device Schema

```python
class ModbusDevice(BaseModel):
    name: str
    ip_address: str
    port: int = 502
    slave_id: int
    read_interval: int  # seconds
    variables: List[Variable]
    active: bool
    created_at: datetime
```

### 6.3 Variable Schema

```python
class Variable(BaseModel):
    name: str
    register: int
    register_type: Literal["coil", "discrete_input", "input_register", "holding_register"]
    unit: str
    scale_factor: float = 1.0
    minimum: float
    maximum: float
    description: str
    active: bool
```

### 6.4 Telemetry Reading Schema

```python
class TelemetryReading(BaseModel):
    device_id: ObjectId
    variable_id: str
    value: float
    timestamp: datetime
    status: Literal["ok", "error", "out_of_range"]
    error_message: Optional[str]
```

---

## 7. Configuration and Environment Variables

### 7.1 Required Backend Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/agrync` |
| `SECRET_KEY` | Key for signing JWT tokens | `super-secret-key-123` |
| `FIWARE_URL` | FIWARE server URL | `http://localhost:4041` |
| `FIWARE_SERVICE` | FIWARE service | `agrync` |
| `FIWARE_SERVICEPATH` | FIWARE service path | `/agrync` |
| `OPC_PORT` | OPC UA server port | `4840` |
| `LOG_LEVEL` | Logging level | `INFO` |

### 7.2 Required Frontend Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000/api/v1` |

### 7.3 `.env.example` File

```text
# Backend
MONGODB_URI=mongodb://mongo:27017/agrync
SECRET_KEY=your-secret-key-change-in-production
FIWARE_URL=http://fiware:4041
FIWARE_SERVICE=agrync
FIWARE_SERVICEPATH=/agrync
OPC_PORT=4840
LOG_LEVEL=INFO

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Docker
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password
```

---

## 8. Security Considerations

### 8.1 Authentication and Authorisation

- **JWT Tokens**: Short-lived tokens for stateless authentication
- **Roles**: RBAC (Role-Based Access Control) with predefined roles
- **Hashing**: Passwords stored with modern cryptographic algorithms

### 8.2 Secure Connections

- **HTTPS**: Recommended for production (configure reverse proxy)
- **OPC UA Certificates**: Supported in `tasks/certificate/`
- **MongoDB Authentication**: Configurable credentials

### 8.3 Data Validation

- **Pydantic Validation**: Typed schemas in the backend
- **TypeScript Validation**: Type system in the frontend
- **Request limits**: Rate limiting recommended

---

## 9. Limitations and Future Improvements

### 9.1 Current Limitations

1. **MongoDB without authentication by default in development**: The development environment does not enforce MongoDB credentials; additional configuration is required before production.
2. **Single-node MongoDB**: No replica set or sharding is configured; availability and read scalability depend on a single instance.
3. **Single concurrent Modbus task**: The locking mechanism prevents more than one Modbus background task from running simultaneously, limiting multi-device parallelism.
4. **No API rate limiting**: The REST API does not implement request throttling, which may expose the system to abuse in open network environments.
5. **Basic logging without centralised aggregation**: Although `logging.conf` is in place, there is no centralised log collection (e.g. Loki, ELK Stack), making it harder to correlate events across services.
6. **No runtime observability**: There is no Prometheus, Grafana or equivalent integration for performance metrics or alerting.

### 9.2 Proposed Improvements

#### Short term (immediate)

1. **API rate limiting**
   - Add `slowapi` middleware or an nginx upstream rule to throttle requests per client.

2. **MongoDB authentication in all environments**
   - Enable `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` by default, even in development.

3. **Structured/JSON logging**
   - Migrate to `structlog` or equivalent JSON-formatted output to facilitate parsing and forwarding to external systems.

#### Medium term

4. **Monitoring and observability**
   - Prometheus exporters for task metrics (reads/min, latency, error rate).
   - Grafana dashboards for real-time visualisation.
   - Centralised log aggregation with Loki or ELK Stack.

5. **Message queue for asynchronous tasks**
   - Replace direct in-process task scheduling with RabbitMQ or Celery to decouple task execution and improve resilience.

6. **Redis caching**
   - Cache frequently queried telemetry data to reduce MongoDB read pressure.

#### Long term

7. **MongoDB high availability**
   - Configure replica sets for fault tolerance and horizontal read scalability.

8. **Additional protocol support**
   - MQTT broker integration for lightweight IoT devices.
   - CoAP support for constrained environments.

9. **Mobile application**
    - React Native app for on-site monitoring and push alerts.

10. **Machine Learning integration**
    - Anomaly detection and predictive maintenance models trained on stored telemetry.

---

## 10. Full Usage Example

### Use case: Monitoring a greenhouse with Modbus sensors

**Step 1: Deploy the system**
```bash
docker compose up --build
# Wait 30–60 seconds for services to start
```

**Step 2: Access the application**
```
Frontend: http://localhost:5173
API Docs: http://localhost:8000/api/v1/docs
```

**Step 3: Create a user and log in**
- Go to the registration screen
- Create an account with email and password
- Log in

**Step 4: Configure a Modbus device**
- Go to "Devices" → "Add device"
- Specify: IP (e.g. 192.168.1.100), Port (502), Slave (1)
- Save

**Step 5: Add variables**
- Go to "Variables" → "Add variable"
- Specify: Name, Modbus Register, Type, Unit
- Example: "Temperature", Register 100, type "input_register", unit "°C"
- Save

**Step 6: Start data reading**
- Go to "Tasks" → "Modbus"
- Create a task for the configured device
- Set read interval (e.g. 10 seconds)
- Activate task

**Step 7: Monitor data**
- Dashboard will show current variable values
- Historical graphs available
- Alerts if values leave the configured range

**Step 8 (Optional): FIWARE integration**
- Go to "Settings" → "FIWARE"
- Specify the FIWARE server URL
- Activate automatic data push
- Data will synchronise automatically

---

## 11. Conclusion

Agrync provides a comprehensive and scalable solution for telemetry collection and management in agroindustrial facilities. Its modular architecture, intuitive interface and support for multiple protocols make it suitable for both small installations and larger-scale plants. The use of modern technologies (FastAPI, React, Docker) guarantees maintainability, scalability and ease of deployment.

---

## Recommended Bibliography for the Scientific Article

1. **Industrial Protocols:**
   - Modbus Organization. "MODBUS Application Protocol Specification V1.1b3"
   - OPC Foundation. "OPC UA Specification" (IEC 62541)

2. **IoT and FIWARE:**
   - Gómez, J., et al. (2020). "FIWARE: An Open Ecosystem for IoT". ArXiv preprint.
   - ETSI GS CIM 009 V1.1.1: "Context Information Management (CIM)"

3. **Web Technologies:**
   - Tiangolo, S. (2021). "FastAPI: Modern Python Web Framework"
   - React Documentation. "Declarative, Efficient, and Flexible JavaScript Library"

4. **IoT in Agriculture:**
   - Sharma, A., et al. (2021). "IoT-based Smart Agriculture: A Comprehensive Survey"
   - Lobell, D. B., et al. (2015). "The use of satellite data for crop yield gap analysis"

---

**Document prepared:** 16 December 2025
**Version:** 1.0
