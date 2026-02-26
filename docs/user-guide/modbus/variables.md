# Variables

A **variable** maps to one or more consecutive Modbus registers within a slave. It is the smallest unit of configuration and the entity that produces data values.

## Viewing variables

Click on a slave row to select it. The variables table at the bottom filters to show the variables of that slave.

## Adding a variable

1. Select a device row, then select a slave row.
2. Click **Add variable** above the variables table.
3. Fill in the form:

| Field | Required | Default | Description |
|---|:---:|---|---|
| **Name** | ✅ | — | Unique within the slave. No hyphens allowed. |
| **Type** | ✅ | — | Data type of the register(s). See table below. |
| **Address** | ✅ | — | Starting register address (integer > 0). |
| **Interval** | ✅ | `5` | Polling interval in seconds (must be > 1). |
| **Endian** | ✅ | `Big` | Byte order: `Big` or `Little`. |
| **Writable** | — | `false` | Whether the variable can be written from the dashboard. |
| **Scaling** | — | `null` | Multiplier applied to the raw value (must be > 0 if set). |
| **Decimals** | — | `0` | Number of decimal places to display (≥ 0). |
| **Unit** | — | `null` | Physical unit label (e.g. `°C`, `bar`, `rpm`). |
| **Min value** | — | `null` | Lower bound for value range (must be set together with max). |
| **Max value** | — | `null` | Upper bound for value range (must be set together with min). |

4. Click **Save**.

### Data types

| Type | Registers used | Description |
|---|:---:|---|
| `Int16` | 1 | Signed 16-bit integer |
| `UInt16` | 1 | Unsigned 16-bit integer |
| `Int32` | 2 | Signed 32-bit integer |
| `UInt32` | 2 | Unsigned 32-bit integer |
| `Float32` | 2 | 32-bit floating point (IEEE 754) |
| `Int64` | 4 | Signed 64-bit integer |
| `UInt64` | 4 | Unsigned 64-bit integer |
| `Float64` | 4 | 64-bit floating point (IEEE 754) |

The number of registers is inferred automatically from the type unless you override it with the **Length** field (advanced use only).

### Value range

Setting **Min value** and **Max value** allows the system to flag out-of-range readings. Both fields must be provided together — setting only one is not allowed.

## Editing a variable

Click the **Edit** icon on a variable row. You can modify the following fields: name, interval, writable flag, min/max values, and unit. The type, address, endian, scaling, decimals, and length cannot be changed after creation.

## Deleting a variable

Click the **Delete** icon and confirm. The variable and all its historical data are permanently removed.
