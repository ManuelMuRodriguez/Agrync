"""
Agrync Demo Task — Modbus TCP Poller (OPC-UA free)
====================================================
Standalone service that:
  1. Reads Modbus devices from MongoDB (populated when the reviewer imports
     demo_devices.json via the web UI).
  2. Polls the Modbus TCP simulator (or any real device) for register values.
  3. Sends those values to FIWARE Orion as normalized NGSIv2 entities.
  4. FIWARE Orion notifies the FastAPI backend via subscription, which stores
     LastVariable and HistoricalVariable documents in MongoDB.
  5. The frontend reads those documents and displays live charts.

This bypasses the OPC-UA layer entirely — no certificates, no OPC server needed.

Register decode convention (must match agrync_backend/tasks/Modbus.py):
  - Float32 / float64 / Int32 / UInt32: Big-endian word order
  - Int16 / UInt16: single holding register
"""

import asyncio
import math
import os
import struct
import time
import logging
from datetime import datetime, timezone

import requests
from motor.motor_asyncio import AsyncIOMotorClient
from pymodbus import ModbusException, FramerType
from pymodbus.client import AsyncModbusTcpClient

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [DEMO-TASK] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration (environment variables — all have sensible defaults)
# ---------------------------------------------------------------------------
MONGO_URI           = os.getenv("MONGO_URI",           "mongodb://mongodb:27017")
FIWARE_URL          = os.getenv("FIWARE_URL",           "http://orion:1026/v2/entities")
ORION_URL           = os.getenv("ORION_URL",            "http://orion:1026")
FIWARE_SERVICE      = os.getenv("FIWARE_SERVICE",       "demo")
FIWARE_SERVICE_PATH = os.getenv("FIWARE_SERVICE_PATH",  "/")
BACKEND_NOTIFY_URL  = os.getenv("BACKEND_NOTIFY_URL",   "http://backend:8000/fiware/subscription")
POLL_INTERVAL       = int(os.getenv("POLL_INTERVAL",    "5"))   # seconds between full polls
RECONNECT_SECONDS   = int(os.getenv("RECONNECTION_TIME","10"))   # wait before Modbus reconnect
DB_REFRESH_CYCLES   = int(os.getenv("DB_REFRESH_CYCLES","12"))   # re-read devices after N intervals

HDR      = {"Fiware-Service": FIWARE_SERVICE, "Fiware-ServicePath": FIWARE_SERVICE_PATH}
HDR_JSON = {**HDR, "Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# Register decoding (Big-endian word order, matches Agrync Modbus.py)
# ---------------------------------------------------------------------------

def _regs_to_float32_be(regs: list[int]) -> float:
    return struct.unpack(">f", struct.pack(">HH", regs[0], regs[1]))[0]

def _regs_to_float64_be(regs: list[int]) -> float:
    return struct.unpack(">d", struct.pack(">HHHH", *regs[:4]))[0]

def _regs_to_int32_be(regs: list[int]) -> int:
    return struct.unpack(">i", struct.pack(">HH", regs[0], regs[1]))[0]

def _regs_to_uint32_be(regs: list[int]) -> int:
    return struct.unpack(">I", struct.pack(">HH", regs[0], regs[1]))[0]

def _regs_to_int64_be(regs: list[int]) -> int:
    return struct.unpack(">q", struct.pack(">HHHH", *regs[:4]))[0]

def _regs_to_uint64_be(regs: list[int]) -> int:
    return struct.unpack(">Q", struct.pack(">HHHH", *regs[:4]))[0]


def decode_value(registers: list[int], var_type: str) -> float | int | None:
    """Convert Modbus holding registers to a Python scalar."""
    try:
        if var_type == "Float32":
            return _regs_to_float32_be(registers)
        if var_type == "Float64":
            return _regs_to_float64_be(registers)
        if var_type == "UInt16":
            return registers[0] & 0xFFFF
        if var_type == "Int16":
            v = registers[0]
            return v if v < 0x8000 else v - 0x10000
        if var_type == "Int32":
            return _regs_to_int32_be(registers)
        if var_type == "UInt32":
            return _regs_to_uint32_be(registers)
        if var_type == "Int64":
            return _regs_to_int64_be(registers)
        if var_type == "UInt64":
            return _regs_to_uint64_be(registers)
    except Exception as exc:
        logger.warning("Decode error (regs=%s type=%s): %s", registers, var_type, exc)
    return None


# ---------------------------------------------------------------------------
# FIWARE helpers (synchronous — called via run_in_executor)
# ---------------------------------------------------------------------------

def fiware_ensure_subscription() -> None:
    """Create the FIWARE → backend subscription (idempotent)."""
    try:
        r = requests.get(f"{ORION_URL}/v2/subscriptions", headers=HDR, timeout=5)
        if r.status_code == 200:
            for sub in r.json():
                if sub.get("notification", {}).get("http", {}).get("url") == BACKEND_NOTIFY_URL:
                    logger.info("FIWARE subscription already registered.")
                    return
        body = {
            "description": "Agrync demo — Modbus TCP direct to backend",
            "subject": {
                "entities": [{"idPattern": ".*"}],
                "condition": {"attrs": []},
            },
            "notification": {
                "http": {"url": BACKEND_NOTIFY_URL},
                "attrsFormat": "normalized",
            },
            "throttling": 0,
        }
        r = requests.post(f"{ORION_URL}/v2/subscriptions", headers=HDR_JSON, json=body, timeout=5)
        if r.status_code in (201, 204):
            logger.info("FIWARE subscription created (notifies → %s).", BACKEND_NOTIFY_URL)
        else:
            logger.error("Could not create FIWARE subscription: %s — %s", r.status_code, r.text)
    except Exception as exc:
        logger.error("FIWARE subscription setup failed: %s", exc)


def fiware_upsert_entity(entity_id: str, attributes: dict, timestamp_iso: str) -> None:
    """Create or update a FIWARE Orion entity with normalized NGSIv2 attributes."""
    if not attributes:
        return

    payload = {
        name: {
            "value": value,
            "type": "Number",
            "metadata": {
                "timestamp": {"type": "DateTime", "value": timestamp_iso}
            },
        }
        for name, value in attributes.items()
        if value is not None
    }

    if not payload:
        return

    try:
        r = requests.get(f"{FIWARE_URL}/{entity_id}", headers=HDR, timeout=5)
        if r.status_code == 404:
            create_body = {"id": entity_id, "type": "modbus", **payload}
            r2 = requests.post(FIWARE_URL, headers=HDR_JSON, json=create_body, timeout=5)
            logger.debug("FIWARE CREATE %s → %s", entity_id, r2.status_code)
        elif r.status_code == 200:
            r2 = requests.patch(
                f"{FIWARE_URL}/{entity_id}/attrs", headers=HDR_JSON, json=payload, timeout=5
            )
            logger.debug("FIWARE PATCH %s → %s", entity_id, r2.status_code)
        else:
            logger.warning("FIWARE GET %s returned unexpected %s", entity_id, r.status_code)
    except Exception as exc:
        logger.error("FIWARE upsert error for %s: %s", entity_id, exc)


# ---------------------------------------------------------------------------
# Modbus polling for one device
# ---------------------------------------------------------------------------

async def poll_slave(
    device_name: str,
    slave_doc: dict,
    client: AsyncModbusTcpClient,
    loop: asyncio.AbstractEventLoop,
) -> None:
    """Read all variables for a single slave and push to FIWARE."""
    slave_name = slave_doc["name"]
    slave_id   = slave_doc.get("slave_id", 1)
    variables  = slave_doc.get("variables") or []
    entity_id  = f"{device_name}-{slave_name}"
    timestamp  = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    attributes: dict[str, float | int] = {}

    for var in variables:
        name     = var["name"]
        address  = var.get("address", 0)
        length   = var.get("length") or 1
        var_type = var.get("type", "Float32")
        scaling  = var.get("scaling")
        decimals = var.get("decimals", 0)

        try:
            rr = await client.read_holding_registers(address, count=length, slave=slave_id)
        except ModbusException as exc:
            logger.warning("[%s] Modbus read %s@a%d: %s", entity_id, name, address, exc)
            continue

        if rr is None or rr.isError():
            logger.warning("[%s] Error response reading %s@a%d", entity_id, name, address)
            continue

        value = decode_value(rr.registers, var_type)
        if value is None:
            continue
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            continue

        if scaling is not None:
            value = value * scaling

        value = round(value, decimals)
        attributes[name] = value

    if attributes:
        await loop.run_in_executor(
            None, fiware_upsert_entity, entity_id, attributes, timestamp
        )
        logger.info("[%s] → %s", entity_id, attributes)


async def poll_device(device_doc: dict) -> None:
    """
    Maintain a persistent Modbus TCP connection to one device and poll all its
    slaves at POLL_INTERVAL seconds. Reconnects automatically on failure.
    """
    ip   = device_doc["ip"]
    name = device_doc["name"]
    loop = asyncio.get_running_loop()
    client = AsyncModbusTcpClient(ip, port=502, framer=FramerType.SOCKET, timeout=2)

    while True:
        try:
            await client.connect()
            if not client.connected:
                raise ConnectionError(f"TCP connect to {ip}:502 failed")

            logger.info("Modbus connected: %s (%s)", name, ip)

            while client.connected:
                start = time.monotonic()
                for slave in device_doc.get("slaves") or []:
                    await poll_slave(name, slave, client, loop)
                elapsed = time.monotonic() - start
                await asyncio.sleep(max(0.0, POLL_INTERVAL - elapsed))

        except (ConnectionError, ModbusException, OSError) as exc:
            logger.warning("Modbus device %s (%s) unreachable: %s — retry in %ds",
                           name, ip, exc, RECONNECT_SECONDS)
            client.close()
            await asyncio.sleep(RECONNECT_SECONDS)

        except asyncio.CancelledError:
            client.close()
            return


# ---------------------------------------------------------------------------
# Startup helpers
# ---------------------------------------------------------------------------

async def wait_for_http(url: str, label: str, timeout_s: int = 120) -> None:
    """Block until an HTTP endpoint responds (or timeout expires)."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code < 500:
                logger.info("%s is ready (%s).", label, url)
                return
        except Exception:
            pass
        logger.info("Waiting for %s …", label)
        await asyncio.sleep(5)
    logger.warning("%s did not become ready within %ds — continuing anyway.", label, timeout_s)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    logger.info("=" * 60)
    logger.info("Agrync Demo Task — Modbus TCP → FIWARE Orion (no OPC-UA)")
    logger.info("Poll interval : %d s", POLL_INTERVAL)
    logger.info("Reconnect wait: %d s", RECONNECT_SECONDS)
    logger.info("FIWARE Orion  : %s", ORION_URL)
    logger.info("Backend notify: %s", BACKEND_NOTIFY_URL)
    logger.info("=" * 60)

    # 1. Wait for dependencies
    await wait_for_http(f"{ORION_URL}/version",  "FIWARE Orion")
    await wait_for_http("http://backend:8000/docs", "Agrync backend")

    # 2. Register FIWARE → backend subscription (idempotent)
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, fiware_ensure_subscription)

    # 3. Connect to MongoDB and watch for device documents
    db = AsyncIOMotorClient(MONGO_URI).agrync

    device_tasks: dict[str, asyncio.Task] = {}
    cycle = 0

    logger.info(
        "Watching MongoDB for Modbus devices — import modbus_simulator/demo_devices.json "
        "via the web UI to start receiving data."
    )

    while True:
        cycle += 1
        try:
            devices = await db.ModbusDevice.find({}).to_list(None)
        except Exception as exc:
            logger.error("MongoDB read error: %s — retrying in 10 s", exc)
            await asyncio.sleep(10)
            continue

        current_ips = {d["ip"] for d in devices}

        # Cancel pollers for devices that no longer exist in the DB
        for ip in list(device_tasks.keys()):
            if ip not in current_ips:
                logger.info("Device %s removed from DB — stopping poller.", ip)
                device_tasks.pop(ip).cancel()

        # Start pollers for new (or recovered) devices
        for doc in devices:
            ip = doc["ip"]
            if ip not in device_tasks or device_tasks[ip].done():
                logger.info("Starting poller for %s (%s).", doc["name"], ip)
                device_tasks[ip] = asyncio.create_task(poll_device(doc))

        if not devices:
            logger.info("No devices found in DB yet — waiting for import …")

        # Re-read devices from DB every DB_REFRESH_CYCLES intervals
        await asyncio.sleep(POLL_INTERVAL * DB_REFRESH_CYCLES)


if __name__ == "__main__":
    asyncio.run(main())
