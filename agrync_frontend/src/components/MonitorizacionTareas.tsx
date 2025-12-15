import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { startTask, stopTask, getModbusTaskStatus } from "../api/TaskAPI";
import { Task } from "../types";
import { toast } from "react-toastify";
import { Switch } from "@headlessui/react";
import { PacmanLoader } from "react-spinners";

const stateMap = {
  running: "Running",
  stopped: "Stopped",
  failed: "Failed",
};


type MonitorizacionTareasProps = {
    taskName: string;
  cooldownKey: string;
  cooldownMs?: number;
};

export default function MonitorizacionTareas({ taskName, cooldownKey, cooldownMs = 2 * 60 * 1000 }: MonitorizacionTareasProps) {
  const queryClient = useQueryClient();
  const [logsHtml, setLogsHtml] = useState<string>("");
  const [isCooldown, setIsCooldown] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(cooldownKey);
    if (stored) {
      const timestamp = parseInt(stored);
      if (Date.now() - timestamp < cooldownMs) {
        setIsCooldown(true);
        const timeout = setTimeout(() => setIsCooldown(false), cooldownMs - (Date.now() - timestamp));
        return () => clearTimeout(timeout);
      } else {
        localStorage.removeItem(cooldownKey);
      }
    }
  }, []);

  const { data: statusData, isError, isLoading } = useQuery<Task>({
    queryKey: ["taskState", taskName],
    queryFn: () => getModbusTaskStatus(taskName),
    retry: false,
    refetchOnWindowFocus: false,
    refetchInterval: 60000
  });

  const estadoActual = statusData?.state === "running";
  const isLocked = statusData?.locked;

  const { mutate: start, isPending: isStarting } = useMutation({
    mutationFn: startTask,
    onError: (error) => {
      toast.error(error.message, {
        closeButton: false,
        className: "bg-error text-white",
      });
    },
    onSuccess: (data) => {
      localStorage.setItem(cooldownKey, Date.now().toString());
      setIsCooldown(true);
      setTimeout(() => setIsCooldown(false), cooldownMs);
      toast.success(data, {
        closeButton: false,
        className: "bg-right-green text-white",
      });
      queryClient.invalidateQueries({ queryKey: ["taskState", taskName] });
    },
  });

  const handleStart = () => start(taskName);

  const { mutate: stop, isPending: isStopping } = useMutation({
    mutationFn: stopTask,
    onError: (error) => {
      toast.error(error.message, {
        closeButton: false,
        className: "bg-error text-white",
      });
    },
    onSuccess: (data) => {
      toast.success(data, {
        closeButton: false,
        className: "bg-right-green text-white",
      });
      queryClient.invalidateQueries({ queryKey: ["taskState", taskName] });
    },
  });

  const handleStop = () => stop(taskName);

  useEffect(() => {
    if (!estadoActual) return;

    const token = localStorage.getItem("ACCESS_TOKEN_AGRYNC");
    if (!token) return;

    const ws = new WebSocket(`ws://localhost:8000/api/v1/tasks/ws/log/${taskName}`);

    ws.onopen = () => {
      ws.send(JSON.stringify({ token }));
    };

    ws.onmessage = (event) => {
      setLogsHtml(event.data);
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    ws.onclose = () => {
      console.log("WebSocket cerrado");
    };

    return () => ws.close();
  }, [estadoActual]);

  useEffect(() => {
    if (isError) {
      toast.error("Error loading service status", {
        closeButton: false,
        className: "bg-error text-white",
      });
    }
  }, [isError]);

  return (
    <div className="flex flex-row p-4">
      <div className="w-1/3 mt-12">
        <h2 className="text-button font-bold text-2xl mb-8 text-center">
         Service control: {taskName}
        </h2>

        <div className="flex flex-col space-y-8">
          <h3 className="text-button font-medium text-xl text-center">
            Service status:{" "}
            <span className="text-3xl font-bold ml-2">
              {statusData?.state ? stateMap[statusData.state] ?? statusData.state : "Desconocido"}
            </span>
          </h3>

          {!isLocked && (
            <Switch
              checked={estadoActual}
              onChange={(enabled) => {
                if (enabled) {
                  handleStart();
                } else {
                  handleStop();
                }
              }}
              disabled={isStopping || isStarting || isCooldown}
              className={`${estadoActual ? "bg-button" : "bg-button-cancel-hover"
                } relative inline-flex h-10 w-20 items-center rounded-full transition-colors duration-200 focus:outline-none mx-auto cursor-pointer`}
            >
              <span
                className={`${estadoActual ? "translate-x-10" : "translate-x-1"
                  } inline-block h-8 w-8 transform rounded-full bg-white transition-transform duration-200`}
              />
            </Switch>
          )}
        </div>

        {isCooldown && !isLocked && (
          <p className="text-button font-semibold my-2">
            *Please wait at least 2 minutes before pressing the button again.*
          </p>
        )}
      </div>

      {estadoActual && (
        <div className="w-2/3 ml-8 bg-black rounded-md overflow-auto text-white font-mono text-sm">
          <h3 className="mb-2 font-bold text-center text-2xl">Logs {taskName}</h3>
          <div className="ml-4" dangerouslySetInnerHTML={{ __html: logsHtml }} />
        </div>
      )}

      {isLoading && (
        <div className="fixed inset-0 z-50 bg-bg-modal bg-opacity-50 flex items-center justify-center">
          <PacmanLoader color="#0BCCAF" loading={true} size={50} />
        </div>
      )}
    </div>
  );
}