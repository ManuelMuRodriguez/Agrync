# Technical Manual

This manual documents the internal architecture, REST API, data models, background tasks, security design, configuration, and testing strategy of the **Agrync** platform.

It is intended for developers who deploy, integrate with, or contribute to Agrync.

---

## Technology stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11 · FastAPI · Beanie ODM · Motor (async MongoDB driver) |
| **Database** | MongoDB |
| **Background tasks** | Python subprocesses managed by `psutil` |
| **OPC UA** | `asyncua` (server + client) |
| **FIWARE** | Orion Context Broker v3 (`telefonicaiot/fiware-orion`) |
| **Frontend** | React 18 · TypeScript · Vite · TanStack Query · i18next |
| **Container runtime** | Docker Compose |
| **Authentication** | OAuth2 Password flow · JWT (access + refresh tokens) · `python-jose` |
| **Password hashing** | `passlib` (bcrypt) |

---

## Quick navigation

<div class="grid cards" markdown>

-   :material-layers-outline: **Architecture**

    System overview, container map, backend and frontend structure.

    [:octicons-arrow-right-24: Architecture](architecture/index.md)

-   :material-api: **API Reference**

    All REST endpoints with methods, paths, roles, payloads, and responses.

    [:octicons-arrow-right-24: API Reference](api/authentication.md)

-   :material-database: **Data Models**

    Beanie/Pydantic documents and their fields, validators, and relationships.

    [:octicons-arrow-right-24: Data Models](data-models/user-roles.md)

-   :material-cog-sync: **Background Tasks**

    Polling loop, OPC UA server, and FIWARE bridge internals.

    [:octicons-arrow-right-24: Background Tasks](background-tasks/modbus.md)

-   :material-shield-lock: **Auth & Security**

    JWT flow, token lifecycle, role enforcement, and password policy.

    [:octicons-arrow-right-24: Auth & Security](auth-security.md)

-   :material-wrench: **Configuration**

    All environment variables and Docker Compose service map.

    [:octicons-arrow-right-24: Configuration](configuration.md)

</div>
