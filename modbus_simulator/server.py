"""
Modbus TCP Demo Simulator — Agrync
===================================
Simulates a greenhouse IoT installation with two Modbus slaves on the same
TCP server (one IP, two slave IDs):

  Slave 1 (id=1)  — Environmental sensors  — Float32, Big Endian word order
  Slave 2 (id=2)  — Actuators / control     — UInt16

The sensor values oscillate realistically following a simulated day/night cycle
that completes one full cycle every 24 minutes (60x real speed), so reviewers
can observe meaningful data variation quickly.

Run standalone:
    python server.py
"""

import asyncio
import struct
import math
import time
import random
import logging

from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import (
    ModbusSlaveContext,
    ModbusServerContext,
    ModbusSequentialDataBlock,
)
from pymodbus.device import ModbusDeviceIdentification

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SIMULATOR] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Register map — Slave 1: environmental sensors (Float32, Big Endian)
# Each Float32 occupies 2 consecutive holding registers.
# NOTE: the Agrync backend subtracts 1 from addresses on import
# (converts 1-indexed user input to 0-indexed Modbus protocol).
# Addresses here must match what is stored in MongoDB (JSON address - 1).
# JSON: 100,102,104,106,108,110 → DB / protocol: 99,101,103,105,107,109
SLAVE1_ID = 1
S1 = {
    "Interior_Temp":      99,    # °C    range: ~18–28
    "Relative_Humidity":  101,   # %     range: ~55–80
    "CO2_Concentration":  103,   # ppm   range: ~400–900
    "Global_Radiation":   105,   # W/m²  range:   0–800
    "Soil_Temp_5cm":      107,   # °C    range: ~16–24
    "Soil_Temp_30cm":     109,   # °C    range: ~14–20
}

# ---------------------------------------------------------------------------
# Register map — Slave 2: actuators (UInt16)
# Each UInt16 occupies 1 holding register.
# JSON: 1,2,3,4 → DB / protocol: 0,1,2,3
# ---------------------------------------------------------------------------
SLAVE2_ID = 2
S2 = {
    "Zenith_Ventilation":   0,   # %     0–100  (writable)
    "Lateral_Ventilation":  1,   # %     0–100
    "Thermal_Screen":       2,   # bool  0 or 1 (writable)
    "Active_Irrigation":    3,   # bool  0 or 1
}

REGISTER_COUNT = 256  # covers all addresses up to 255


# ---------------------------------------------------------------------------
# Encoding helpers
# ---------------------------------------------------------------------------

def float32_big_to_regs(value: float) -> list[int]:
    """
    Encode a float32 value as two 16-bit holding registers in
    Big Endian word order (high word first).
    This matches 'endian: Big' in the Agrync device configuration.
    """
    packed = struct.pack(">f", float(value))
    high = struct.unpack(">H", packed[0:2])[0]
    low  = struct.unpack(">H", packed[2:4])[0]
    return [high, low]


# ---------------------------------------------------------------------------
# Simulation logic
# ---------------------------------------------------------------------------

def simulated_values() -> dict:
    """
    Generate realistic time-varying greenhouse sensor values.

    The day/night cycle runs at 60x real speed:
    one full day (sunrise → sunset → sunrise) every 24 minutes.
    This lets reviewers observe meaningful changes without waiting hours.
    """
    t = time.time()
    # 24 real minutes = 1 simulated day
    day_seconds = 24 * 60
    cycle = (t % day_seconds) / day_seconds   # 0.0 → 1.0

    # Sun intensity:  0 at midnight, peaks at solar noon (cycle=0.5)
    sun = max(0.0, math.sin(math.pi * cycle))

    def noise(amplitude: float) -> float:
        return random.uniform(-amplitude, amplitude)

    # Environmental sensors — physically correlated with sun intensity
    temp       = round(20.0  + 8.0  * sun + noise(0.3), 2)
    humidity   = round(75.0  - 15.0 * sun + noise(1.0), 2)
    co2        = round(550.0 + 300.0 * (1.0 - sun) + noise(10.0), 2)   # higher at night
    radiation  = round(max(0.0, 800.0 * sun + noise(5.0) * sun), 2)
    soil_5     = round(17.0  + 6.0  * sun + noise(0.2), 2)
    soil_30    = round(15.0  + 4.0  * sun + noise(0.1), 2)

    # Actuators respond automatically to environmental conditions
    vent_cen   = int(min(100, max(0, (temp - 22.0) * 15 + noise(2))))
    vent_lat   = int(min(100, max(0, (temp - 25.0) * 10 + noise(1))))
    screen     = 1 if radiation < 100.0 else 0   # screen active at night / overcast
    irrigation = 1 if 0.30 < cycle < 0.42 else 0  # mid-morning irrigation window

    return {
        "slave1": {
            "Interior_Temp":     temp,
            "Relative_Humidity": humidity,
            "CO2_Concentration": co2,
            "Global_Radiation":  radiation,
            "Soil_Temp_5cm":     soil_5,
            "Soil_Temp_30cm":    soil_30,
        },
        "slave2": {
            "Zenith_Ventilation":  vent_cen,
            "Lateral_Ventilation": vent_lat,
            "Thermal_Screen":      screen,
            "Active_Irrigation":   irrigation,
        },
    }


# ---------------------------------------------------------------------------
# Datastore setup and update
# ---------------------------------------------------------------------------

def build_context() -> ModbusServerContext:
    """Create the Modbus server context with two slave datastores."""
    # ModbusSequentialDataBlock(address, [initial_values]) — address 0 means
    # the block starts at register 0, covering addresses 0..REGISTER_COUNT-1.
    slave1 = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, [0] * REGISTER_COUNT),
    )
    slave2 = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, [0] * REGISTER_COUNT),
    )
    return ModbusServerContext(
        slaves={SLAVE1_ID: slave1, SLAVE2_ID: slave2},
        single=False,
    )


def update_context(context: ModbusServerContext) -> None:
    """Write the current simulated values into the Modbus holding registers."""
    vals = simulated_values()

    # --- Slave 1: Float32 Big Endian ---
    s1 = context[SLAVE1_ID]
    for name, addr in S1.items():
        s1.setValues(3, addr, float32_big_to_regs(vals["slave1"][name]))

    # --- Slave 2: UInt16 ---
    s2 = context[SLAVE2_ID]
    for name, addr in S2.items():
        s2.setValues(3, addr, [int(vals["slave2"][name]) & 0xFFFF])

    v1 = vals["slave1"]
    v2 = vals["slave2"]
    logger.info(
        "Slave1 | Temp: %5.1f°C  HR: %4.1f%%  CO2: %5.0f ppm  Rad: %5.0f W/m²  "
        "Soil5: %4.1f°C  Soil30: %4.1f°C",
        v1["Interior_Temp"], v1["Relative_Humidity"],
        v1["CO2_Concentration"],  v1["Global_Radiation"],
        v1["Soil_Temp_5cm"], v1["Soil_Temp_30cm"],
    )
    logger.info(
        "Slave2 | Zenith: %3d%%  Lateral: %3d%%  Screen: %d  Irrigation: %d",
        v2["Zenith_Ventilation"], v2["Lateral_Ventilation"],
        v2["Thermal_Screen"],    v2["Active_Irrigation"],
    )


async def update_loop(context: ModbusServerContext, interval: float = 5.0) -> None:
    """Refresh simulated register values every `interval` seconds."""
    while True:
        update_context(context)
        await asyncio.sleep(interval)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    context = build_context()
    update_context(context)  # seed initial values before first client poll

    identity = ModbusDeviceIdentification()
    identity.VendorName  = "Agrync"
    identity.ProductCode = "GH-SIM-1"
    identity.ProductName = "Greenhouse Modbus TCP Simulator"
    identity.ModelName   = "Demo v1.0"
    identity.MajorMinorRevision = "1.0"

    logger.info("=" * 60)
    logger.info("Agrync — Greenhouse Modbus TCP Simulator")
    logger.info("Listening on 0.0.0.0:502")
    logger.info("  Slave 1 (id=1) — Float32 Big Endian — environmental sensors")
    logger.info("  Slave 2 (id=2) — UInt16             — actuators / control")
    logger.info("Day/night cycle: 24 minutes (60x real speed)")
    logger.info("=" * 60)

    # Schedule the value-update loop to run concurrently with the server
    asyncio.ensure_future(update_loop(context))

    await StartAsyncTcpServer(
        context=context,
        identity=identity,
        address=("0.0.0.0", 502),
    )


if __name__ == "__main__":
    asyncio.run(main())
