# Introduction

## What is Agrync?

Agrync is a web-based platform that bridges the gap between industrial field devices and the people who need to monitor them. It collects sensor data from the shop floor, stores it, and presents it through a clean web interface — so operators and engineers can watch values in real time, review historical trends, and act on anomalies without writing a single line of code.

<!-- screenshot: landing dashboard showing several variable cards with live values -->
![Agrync overview](../images/dashboard-cards.png)
*The Agrync dashboard showing live sensor readings from multiple devices.*

## Key capabilities

| Capability | Description |
|---|---|
| **Modbus TCP/IP collection** | Reads registers from any Modbus-compatible PLC or sensor over TCP. |
| **OPC UA server** | Exposes collected data as an OPC UA server so other OT systems can subscribe. |
| **FIWARE forwarding** | Pushes telemetry to a FIWARE Orion Context Broker for long-term storage and analytics. |
| **Live dashboard** | Shows the most recent value of each variable, updated automatically. |
| **Historical charts** | Plots time-series data with optional hourly or daily aggregation via Highcharts. |
| **Role-based access** | Administrators control the system; Editors can write values; each user sees only their assigned devices. |
| **Bulk configuration** | Devices, slaves, and variables can be configured in bulk by uploading a JSON file. |

## System architecture

Agrync is composed of three main layers:

```mermaid
graph TD
        A["Browser<br/>(React + Vite)"]
        B["FastAPI backend"]
        C["MongoDB"]
        D["Modbus TCP/IP devices"]
        E["OPC UA clients"]
        F["FIWARE Orion"]

        A -->|HTTP / WebSocket| B
        B --> C
        B -->|Modbus task| D
        B -->|ServerOPC task| E
        B -->|OPCtoFIWARE task| F
```

The **backend** exposes a REST API and manages three long-running background tasks. The **frontend** communicates exclusively with the backend API — it never contacts field devices directly.
