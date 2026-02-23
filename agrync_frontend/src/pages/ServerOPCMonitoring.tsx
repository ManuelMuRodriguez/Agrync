import MonitorizacionTareas from "../components/TaskMonitoring";


export default function ServerOPCMonitorizacion() {

  return (
    <MonitorizacionTareas
      taskName="ServerOPC"
      cooldownKey="serverCooldownTimestamp"
      cooldownMs={2 * 60 * 1000}
    />
  );
}