# Modbus Configuration

!!! info "Administrator only"
    All Modbus configuration actions require the **Administrator** role.

## Data hierarchy

Modbus configuration follows a three-level hierarchy:

```
Device  (identified by IP address)
└── Slave  (identified by Modbus slave ID)
    └── Variable  (a single register or register group)
```

| Level | Identifies | Example |
|---|---|---|
| **Device** | A physical Modbus TCP/IP gateway or PLC | `PLC_Line1` at `192.168.1.10` |
| **Slave** | A logical unit within the device | `Pump_A` with slave ID `1` |
| **Variable** | A measured or controllable value | `Flow_Rate` at address `101` |

## Naming rules

All names (devices, slaves, and variables) follow the same rules:

- Only letters (`a–z`, `A–Z`), digits (`0–9`), underscores (`_`), dots (`.`), and hyphens (`-`) are allowed. **Hyphens are not allowed in variable names.**
- Leading and trailing spaces are stripped automatically.
- Internal spaces are replaced with underscores.

## Navigation

Go to **Administration → Devices → Modbus** to reach the Modbus configuration area. You will see three tables stacked vertically:

1. **Devices** — the top-level list.
2. **Slaves** — filtered to the currently selected device.
3. **Variables** — filtered to the currently selected slave.

## Configuration methods

There are two ways to configure Modbus:

- **Manual** — add, edit, or delete items one by one using the tables. Best for small changes.
- **Bulk import** — upload a JSON file describing the full hierarchy. Best for initial setup or large changes. See [Bulk Import](bulk-import.md).
