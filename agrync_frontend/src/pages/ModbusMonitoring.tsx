import MonitorizacionTareas from "../components/TaskMonitoring";



export default function ModbusMonitorizacion() {

  return (
    <MonitorizacionTareas
      taskName="Modbus"
      cooldownKey="modbusCooldownTimestamp"
      cooldownMs={2 * 60 * 1000}
    />
  );
}