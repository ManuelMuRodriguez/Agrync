# System Overview

Agrync is deployed as four Docker containers connected on a shared bridge network (`agrync_network`). The diagram below shows the containers and the data flows between them.

## Container map

```mermaid
graph TD
    subgraph Docker["Docker Compose – agrync_network"]
        FE["agrync_frontend\nReact/Vite\n:5173"]
        BE["agrync_backend\nFastAPI / Python\n:8000 (REST)\n:4842 (OPC UA)"]
        DB["mongodb\nMongoDB\n:27017 (internal)\n:27020 (host)"]
        OR["orion\nFIWARE Orion CB\n:1026"]
    end

    Browser["Browser"] -->|HTTP + WS| FE
    FE -->|REST /api/v1| BE
    BE -->|Beanie/Motor| DB
    OR -->|MongoDB wire| DB
    BE -->|"OPCtoFIWARE task\nNGSI v2 HTTP"| OR
```

## End-to-end data flow

```mermaid
sequenceDiagram
    participant Field as Modbus device
    participant MT as Modbus task
    participant DB as MongoDB
    participant OPC as ServerOPC task
    participant OF as OPCtoFIWARE task
    participant Orion as FIWARE Orion

    MT->>Field: Poll holding registers (TCP)
    Field-->>MT: Raw register values
    MT->>DB: Write LastVariable + HistoricalVariable
    OPC->>DB: Read LastVariable
    OPC-->>OPC: Expose via OPC UA server
    OF->>OPC: Subscribe (OPC UA)
    OPC-->>OF: Value change notification
    OF->>Orion: PATCH context entity attribute (NGSI v2)
```

## Ports summary

| Host port | Container | Purpose |
|---|---|---|
| `5173` | agrync_frontend | React dev server (Vite) |
| `8000` | agrync_backend | FastAPI REST API |
| `4842` | agrync_backend | OPC UA server (asyncua) |
| `27020` | mongodb | MongoDB (host access) |
| `1026` | orion | FIWARE Orion Context Broker |

## API root path

All REST routes are prefixed with `/api/v1` (set via `root_path` in the FastAPI app). Example:

```
POST http://localhost:8000/api/v1/auth/login
```
