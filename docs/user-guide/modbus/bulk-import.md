# Bulk Import

Instead of adding devices, slaves, and variables one by one, you can upload a single JSON file that describes the entire hierarchy at once. This is the recommended method for the initial setup of a plant.

## Download the template

Click **Download template** on the Modbus configuration page to get a ready-to-fill JSON example. The template shows the correct structure with sample values for every field.

## File structure

The file must be a JSON array of devices. Each device contains an array of slaves, and each slave contains an array of variables.

```json
[
  {
    "name": "PLC_Line1",
    "ip": "192.168.1.10",
    "slaves": [
      {
        "name": "Pump_A",
        "slave_id": 1,
        "variables": [
          {
            "name": "Flow_Rate",
            "type": "Float32",
            "address": 101,
            "interval": 5,
            "endian": "Big",
            "writable": false,
            "scaling": null,
            "decimals": 2,
            "unit": "m3/h",
            "min_value": 0,
            "max_value": 100
          }
        ]
      }
    ]
  }
]
```

### Device fields

| Field | Type | Required | Notes |
|---|---|:---:|---|
| `name` | string | ✅ | Unique across the system. No hyphens. |
| `ip` | string | ✅ | Valid IPv4 address. |
| `slaves` | array | — | Can be omitted to create an empty device. |

### Slave fields

| Field | Type | Required | Notes |
|---|---|:---:|---|
| `name` | string | ✅ | Unique within the device. No hyphens. |
| `slave_id` | integer | ✅ | Must be > 0. Unique within the device. |
| `variables` | array | — | Can be omitted to create an empty slave. |

### Variable fields

| Field | Type | Required | Default | Notes |
|---|---|:---:|---|---|
| `name` | string | ✅ | — | Unique within the slave. **No hyphens.** |
| `type` | string | ✅ | — | One of: `Int16`, `UInt16`, `Int32`, `UInt32`, `Float32`, `Int64`, `UInt64`, `Float64` |
| `address` | integer | ✅ | — | Register address, must be > 0. |
| `interval` | integer | — | `5` | Polling interval in seconds, must be > 1. |
| `endian` | string | — | `"Big"` | `"Big"` or `"Little"`. |
| `writable` | boolean | — | `false` | Whether the variable can be written from the dashboard. |
| `scaling` | number\|null | — | `null` | Multiplier for the raw value. Must be > 0 if set. |
| `decimals` | integer | — | `0` | Display decimal places, ≥ 0. |
| `unit` | string\|null | — | `null` | Physical unit label. |
| `min_value` | number\|null | — | `null` | Must be provided together with `max_value`. |
| `max_value` | number\|null | — | `null` | Must be provided together with `min_value`. |

## Upload the file

1. Click **Upload configuration** on the Modbus configuration page.
2. Select your JSON file.
3. Click **Upload**.

The system validates the file and processes each device, slave, and variable:

- **New items** are created.
- **Existing items** (matched by name) are updated if any of their editable fields have changed.
- **Items not present** in the file are left untouched — the upload is non-destructive.

## Validation errors

If the file contains errors, the upload is rejected and an error message is shown. Common causes:

| Error | Fix |
|---|---|
| Invalid JSON syntax | Validate the file with a JSON linter before uploading. |
| Duplicate device name | Each device name must be unique across the whole system. |
| Invalid IP address | Use standard IPv4 notation (`x.x.x.x`). |
| Variable name contains a hyphen | Replace hyphens with underscores. |
| `address` ≤ 0 | Register addresses must start at 1. |
| `interval` ≤ 1 | Minimum polling interval is 2 seconds. |
| Only one of `min_value`/`max_value` set | Provide both or neither. |
| `min_value` > `max_value` | The lower bound cannot exceed the upper bound. |
