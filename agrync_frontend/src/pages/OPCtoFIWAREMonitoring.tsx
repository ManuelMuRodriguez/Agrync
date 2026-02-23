import MonitorizacionTareas from "../components/TaskMonitoring";



export default function OPCtoFIWAREMonitorizacion() {

      return (
          <MonitorizacionTareas
            taskName="OPCtoFIWARE"
            cooldownKey="fiwareCooldownTimestamp"
            cooldownMs={2 * 60 * 1000}
          />
        );
  }