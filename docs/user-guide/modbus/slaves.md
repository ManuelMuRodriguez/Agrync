# Slaves

A **slave** (also called a Modbus unit or node) is a logical entity within a device identified by a numeric **Slave ID**. Each device can have multiple slaves.

## Viewing slaves

Click on a device row to select it. The slaves table below automatically filters to show only the slaves that belong to the selected device.

## Adding a slave

1. Select the parent device by clicking its row.
2. Click **Add slave** above the slaves table.
3. Fill in the form:

| Field | Required | Rules |
|---|:---:|---|
| **Name** | ✅ | Letters, digits, `_`, `.`, `-`. Must be unique within the device. |
| **Slave ID** | ✅ | Integer greater than `0`. Must be unique within the device. |

4. Click **Save**.

## Editing a slave

Click the **Edit** icon on any slave row. You can change the name and the slave ID. Click **Save** to apply.

!!! warning "Changing slave ID"
    Changing the Slave ID affects how the Modbus task queries the device. Make sure the new ID matches the physical device configuration.

## Deleting a slave

Click the **Delete** icon on the slave row and confirm. All variables belonging to this slave are also deleted.

!!! danger
    Historical data for all variables in this slave is also permanently removed.
