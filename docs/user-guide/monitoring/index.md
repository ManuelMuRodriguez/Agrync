# Monitoring

!!! info "Administrator only"
    Starting, stopping, and inspecting tasks requires the **Administrator** role.

## What are tasks?

Agrync runs three independent background processes called **tasks**. Each task is a long-running Python script that operates continuously once started.

| Task | Script | Purpose |
|---|---|---|
| **Modbus** | `tasks/Modbus.py` | Polls all configured Modbus devices on their defined intervals and stores the values in the database. |
| **ServerOPC** | `tasks/ServerOPC.py` | Starts an OPC UA server that exposes the latest variable values to any OPC UA client. |
| **OPCtoFIWARE** | `tasks/OPCtoFIWARE.py` | Subscribes to the OPC UA server and forwards updates to FIWARE Orion as context entity attributes. |

## Task states

Each task can be in one of three states:

| State | Meaning |
|---|:---|
| **Running** | The process is active and operating normally. |
| **Stopped** | The process is not running. |
| **Failed** | The process started but terminated with an error. Check the log for details. |

<!-- screenshot: the monitoring overview page showing the three task cards with their current states and start/stop buttons -->
![Monitoring overview](../../images/monitoring-overview.png)
*The monitoring page showing the three tasks with their current states.*

## Task dependencies

The **OPCtoFIWARE** task depends on the **ServerOPC** task because it subscribes to the OPC UA server. Both tasks are marked as **locked**: if either is running, the other is blocked from starting independently.

The **Modbus** task is independent and can run on its own.

Recommended start order:

```
1. Modbus     → starts collecting data into the database
2. ServerOPC  → exposes collected data via OPC UA
3. OPCtoFIWARE → forwards OPC UA data to FIWARE Orion
```

## Navigation

Go to **Administration → Monitoring** and select the task (Modbus, ServerOPC, or OPCtoFIWARE) from the left-hand submenu.
