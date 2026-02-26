# JSON Template Reference

This page documents the complete structure of the Modbus bulk-import JSON file. For step-by-step import instructions see [Bulk Import](../modbus/bulk-import.md).

---

## Obtaining the template

Go to **Administration → Modbus → Bulk Import** and click **Download Template**. The file `modbus_template.json` contains working example entries for every combination of optional fields.

---

## Top-level structure

The file must be a JSON **array** containing one or more **device objects**.

```json
[ <device>, <device>, … ]
```

---

## Device object

```json
{
    "name": "Dispositivo_1",      // string, required. Unique device name.
    "ip":   "192.168.1.10",       // string, required. IPv4 address of the Modbus TCP gateway.
    "slaves": [ <slave>, … ]      // array, required. At least one slave.
}
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| `name` | string | Yes | No spaces; unique across all devices. |
| `ip` | string | Yes | Valid IPv4 address (e.g. `192.168.1.10`). |
| `slaves` | array | Yes | At least one slave object. |

---

## Slave object

```json
{
    "name":     "Slave_1",   // string, required. Unique within the parent device.
    "slave_id": 1,           // integer, required. Modbus unit ID (1–247).
    "variables": [ <variable>, … ]
}
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| `name` | string | Yes | No spaces; unique within the parent device. |
| `slave_id` | integer | Yes | 1 – 247. |
| `variables` | array | Yes | At least one variable object. |

---

## Variable object

A variable must always include `name` and `address`. All other fields are optional and default to the values shown.

```json
{
    "name":      "VariableName",  // required
    "address":   201,             // required
    "type":      "Float32",       // optional – default: "Float32"
    "scaling":   null,            // optional – default: null (no scaling)
    "decimals":  0,               // optional – default: 0
    "endian":    "Big",           // optional – default: "Big"
    "interval":  5,               // optional – default: 5 (seconds)
    "length":    null,            // optional – default: null
    "writable":  false,           // optional – default: false
    "min_value": null,            // optional – default: null
    "max_value": null,            // optional – default: null
    "unit":      null             // optional – default: null
}
```

### Variable field reference

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | — | Variable name. No spaces. Unique within its slave. |
| `address` | integer | — | Modbus holding register starting address. |
| `type` | string | `"Float32"` | Data type. See [Data types](#data-types). |
| `scaling` | number \| null | `null` | Multiply raw value by this factor before storing. `null` disables scaling. |
| `decimals` | integer | `0` | Number of decimal places to store (0–6). |
| `endian` | string | `"Big"` | Byte order: `"Big"` or `"Little"`. |
| `interval` | integer | `5` | Polling interval in seconds (≥ 1). |
| `length` | integer \| null | `null` | Number of registers to read. Required only for `String` type; ignored otherwise. |
| `writable` | boolean | `false` | Whether the variable can be written from the Dashboard. |
| `min_value` | number \| null | `null` | Minimum valid value. Readings below this are flagged. |
| `max_value` | number \| null | `null` | Maximum valid value. Readings above this are flagged. |
| `unit` | string \| null | `null` | Engineering unit label displayed in the UI (e.g. `"°C"`, `"bar"`). |

### Data types

| value | Registers | Description |
|---|---|---|
| `Float32` | 2 | 32-bit IEEE 754 floating-point number. Default. |
| `Int16` | 1 | 16-bit signed integer. |
| `UInt16` | 1 | 16-bit unsigned integer. |
| `Int32` | 2 | 32-bit signed integer. |
| `UInt32` | 2 | 32-bit unsigned integer. |
| `String` | variable | ASCII string. Set `length` to the number of registers. |

---

## Minimal valid example

This is the smallest possible valid file — one device, one slave, one variable:

```json
[
    {
        "name": "BoilerRoom",
        "ip": "192.168.1.10",
        "slaves": [
            {
                "name": "Boiler1",
                "slave_id": 1,
                "variables": [
                    {
                        "name": "OutletTemp",
                        "type": "Float32",
                        "address": 100
                    }
                ]
            }
        ]
    }
]
```

---

## Full annotated example

This is the structure shipped with the template. It demonstrates three variable patterns: minimal fields, all defaults explicit, and all optional fields set.

```json
[
    {
        "name": "Dispositivo_1",
        "ip": "192.168.X.X",
        "slaves": [
            {
                "name": "Slave_1",
                "slave_id": 1,
                "variables": [
                    {
                        "name":    "Variable_minimos_atributos",
                        "type":    "Float32",
                        "address": 201
                        // Only required fields. Defaults apply for everything else.
                    },
                    {
                        "name":      "Variable_por_defecto",
                        "type":      "Float32",
                        "address":   301,
                        "scaling":   null,
                        "decimals":  0,
                        "endian":    "Big",
                        "interval":  5,
                        "length":    null,
                        "writable":  false,
                        "min_value": null,
                        "max_value": null,
                        "unit":      null
                        // All fields explicit, set to their default values.
                    },
                    {
                        "name":      "Variable_maximos_atributos",
                        "type":      "Float32",
                        "address":   401,
                        "scaling":   0.1,
                        "decimals":  2,
                        "endian":    "Little",
                        "interval":  6,
                        "length":    2,
                        "writable":  true,
                        "min_value": 10.5,
                        "max_value": 20.8,
                        "unit":      "ºC"
                        // All optional fields populated.
                    }
                ]
            }
        ]
    }
]
```

!!! note "Comments are not valid JSON"
    The `// ...` comments above are for illustration only. Remove them before uploading — JSON does not support inline comments.

---

## Common validation errors

| Error message | Cause | Fix |
|---|---|---|
| `name must not contain spaces` | Variable, slave, or device `name` has a space. | Replace spaces with underscores. |
| `ip is not a valid IPv4 address` | `ip` value is malformed. | Check for typos in the IP address. |
| `slave_id out of range` | `slave_id` is less than 1 or greater than 247. | Use a value between 1 and 247. |
| `address is required` | A variable object is missing the `address` field. | Add `"address": <integer>`. |
| `type is not a valid data type` | Unknown string in the `type` field. | Use one of the values in the [Data types](#data-types) table. |
| `length is required for String type` | A `String` variable has no `length`. | Add `"length": <register count>`. |
| `Duplicate device name` | Two devices share the same `name`. | Rename one of them. |
| `Duplicate slave name` | Two siblings share the same `name`. | Rename one of them. |
