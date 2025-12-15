import MonitorizacionTareas from "../components/MonitorizacionTareas";


export default function ServerOPCMonitorizacion() {

  return (
    <MonitorizacionTareas
      taskName="ServerOPC"
      cooldownKey="serverCooldownTimestamp"
      cooldownMs={2 * 60 * 1000}
    />
  );
}