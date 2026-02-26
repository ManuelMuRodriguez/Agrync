# ServerOPC Task

The **ServerOPC** task starts an OPC UA server inside the backend container. It exposes the latest variable values collected by the Modbus task to any OPC UA client, including the OPCtoFIWARE task.

This task is **locked**: only one locked task can run at a time. If **OPCtoFIWARE** is already running, you must stop it before starting ServerOPC.

---

## Starting the ServerOPC task

1. Go to **Administration → Monitoring → ServerOPC**.
2. Verify the current state is **Stopped**.
3. Click **Start**.

<!-- screenshot: ServerOPC task page with state "Stopped" and the Start button -->
![ServerOPC task – stopped](../../images/monitoring-server-opc-stopped.png)
*ServerOPC task ready to start.*

If the task starts successfully, the state changes to **Running** and the log panel begins streaming.

<!-- screenshot: ServerOPC task running with log panel active -->
![ServerOPC task – running](../../images/monitoring-server-opc-running.png)
*ServerOPC task running, log panel active.*

!!! note "OPCtoFIWARE must be stopped first"
    If the OPCtoFIWARE task is currently running, an error is shown and the ServerOPC task will not start. Stop OPCtoFIWARE first, then start ServerOPC.

---

## Stopping the ServerOPC task

1. Go to **Administration → Monitoring → ServerOPC**.
2. Click **Stop**.
3. The state changes to **Stopped**.

!!! warning
    Stopping ServerOPC also breaks the OPCtoFIWARE task if it is running, because OPCtoFIWARE subscribes to the OPC UA server. Stop OPCtoFIWARE before stopping ServerOPC to achieve a clean shutdown.

Recommended shutdown order:

```
1. Stop OPCtoFIWARE
2. Stop ServerOPC
3. Stop Modbus (optional)
```

---

## Task state: Failed

If ServerOPC transitions to **Failed**:

1. Check the live log for error messages.
2. Common causes:
    - The configured OPC UA port (default `4840`) is already in use.
    - The server certificate has expired or is missing.
    - A network firewall is blocking the OPC UA port.
3. Resolve the issue and click **Start** to retry.

---

## Live log

The log panel streams output in real time via a WebSocket connection when the task is running.

<!-- screenshot: ServerOPC log panel with timestamped lines -->
![ServerOPC live log](../../images/monitoring-server-opc-log.png)
*Live log for the ServerOPC task.*

The underlying log file is stored at `tasks/logServer/ServerOPC.log` inside the backend container.
