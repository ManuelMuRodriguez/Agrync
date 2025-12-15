import { useState, useEffect, Fragment } from "react";
import { RiArrowDropDownLine } from "react-icons/ri"
import { RiArrowDropUpLine } from "react-icons/ri";
import VariableCard from '../components/VariableCard';
import { useForm } from 'react-hook-form';
import { FormDashboard, GenericDevices, GenericDevicesNames, LastData } from '../types';
import { IoRadio } from 'react-icons/io5';
import { Dialog, Transition, DialogPanel } from '@headlessui/react';
import { useAuth } from "../hooks/useAuth";
import { useGenericDevicesNames } from "../hooks/useGenericDevicesNames";
import { useMutation } from "@tanstack/react-query";
import { toast } from "react-toastify";
import { getDashboardBody, getLastData } from "../api/GenericDevicesApi";
import { PacmanLoader } from "react-spinners";





export default function Dashboard() {
  const [devices, setDevices] = useState<GenericDevicesNames>([]);
  const [dataGenericDevices, setDataGenericDevices] = useState<GenericDevices>([]);
  const [initialSelectedVariables, setInitialSelectedVariables] = useState<string[]>([]);
  const [modalSelectedVariables, setModalSelectedVariables] = useState<string[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [openStates, setOpenStates] = useState<Record<string, boolean>>({});
  const [lastData, setlastData] = useState<Record<string, { value: number | null; timestamp: string | null }>>({});
  const [lastParams, setLastParams] = useState<{ formData: FormDashboard; userId: string } | null>(null);

  const initialValues: FormDashboard = {
    variables_names: []
  }

  const { register, handleSubmit, watch, setValue } = useForm({
    mode: "onTouched",
    reValidateMode: "onChange",
    shouldFocusError: true,
    defaultValues: initialValues
  });

  const selectedCheckboxes = watch("variables_names") as string[] || [];

  const { data: dataDevices, isError, isLoading } = useGenericDevicesNames();
  const { data: dataUser } = useAuth();

  useEffect(() => {
    if (dataDevices) {
      setDevices(dataDevices);
    }
  }, [dataDevices]);

  const handleModalOpen = () => {
    setInitialSelectedVariables(selectedCheckboxes);
    setModalSelectedVariables(selectedCheckboxes);
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setModalSelectedVariables(initialSelectedVariables);
    setIsModalOpen(false);
  };




  const replaceLastDash = (str: string) => {
    const lastDash = str.lastIndexOf("-");
    if (lastDash === -1) return str;
    return str.substring(0, lastDash) + "|" + str.substring(lastDash + 1);
  }

  const { mutate: cardValues } = useMutation({
    mutationFn: getLastData,
    onSuccess: (data: LastData) => {
      const mapped: Record<string, { value: number | null; timestamp: string | null }> = {};
      data.forEach(item => {
        const normalizedKey = replaceLastDash(item.name);
        mapped[normalizedKey] = { value: item.value, timestamp: item.timestamp };
      });
      setlastData(mapped);
    },
    onError: (err) => {
      console.error("Error obtaining real-time values", err);
    }
  });







  const { mutate: mutateBody, isPending } = useMutation({
    mutationFn: getDashboardBody,
    onError: (error) => {
      toast.error(error.message, {
        closeButton: false,
        className: "bg-error text-white"
      });
    },
    onSuccess: (dataGenericDevices: GenericDevices) => {
      setDataGenericDevices(dataGenericDevices);
      toast.success("Data successfully uploaded", {
        closeButton: false,
        className: "bg-right-green text-white"
      });

    }
  });

  const onSubmit = (formData: FormDashboard) => {
    const userId = dataUser?.id;
    if (userId) {

      const params = { formData, userId };
      setLastParams(params);

      if (formData.variables_names.length === 0) {
        setDataGenericDevices([]);
        setlastData({});
        setLastParams(null);
        return;
      }


      mutateBody({ formData, userId });
      cardValues({ formData, userId })
    }
  };

  const toggleDevice = (deviceName: string) => {
    setOpenStates((prev) => ({
      ...prev,
      [deviceName]: !prev[deviceName]
    }));
  };




  //const initialCallMade = useRef(false);

  //useEffect(() => {
  //  if (!lastParams || initialCallMade.current) return;

  //  cardValues(lastParams);
  //  initialCallMade.current = true;
  //}, [lastParams]);

  useEffect(() => {
    if (!lastParams) return;

    const interval = setInterval(() => {
      cardValues(lastParams);
    }, 30000);

    return () => clearInterval(interval);
  }, [lastParams]);




  return (
    <div className="ml-5 space-y-5 min-w-80">
      <form className="flex flex-col space-y-12" noValidate>
        <button
          type="button"
          onClick={handleModalOpen}
          className="flex items-center gap-2 justify-center bg-button hover:bg-button-hover w-full p-3 rounded-lg text-white font-medium text-2xl cursor-pointer"
        >
          <IoRadio /> Select Variables
        </button>

        {/* Modal */}
        <Transition appear show={isModalOpen} as={Fragment}>
          <Dialog as="div" className="relative z-10" onClose={handleModalClose}>
            <Transition
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0"
              enterTo="opacity-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
              show={isModalOpen}
            >
              <div className="fixed inset-0 bg-bg-modal" />
            </Transition>

            <div className="fixed inset-0 overflow-y-auto">
              <div className="flex min-h-full items-center justify-center p-4 pt-12 text-center">
                <Transition
                  as={Fragment}
                  enter="ease-out duration-300"
                  enterFrom="opacity-0 scale-95"
                  enterTo="opacity-100 scale-100"
                  leave="ease-in duration-200"
                  leaveFrom="opacity-100 scale-100"
                  leaveTo="opacity-0 scale-95"
                  show={isModalOpen}
                >
                  <DialogPanel className="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all w-10/12">
                    {devices.length === 0 ? (
                      <p className="text-button text-center text-xl font-bold">
                        No devices found
                      </p>
                    ) : (
                      devices.map((device, index) => (
                        <div key={index} className="space-y-4 last:mb-0 mb-8">
                          <div>
                            <p className="text-xl font-bold text-button">{device.name}</p>
                            <hr className="border-black my-2" />
                          </div>

                          {device.variables_names.length === 0 || isError ? (
                            <p className="text-center text-button font-bold">No variables available</p>
                          ) : (
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-2">
                              {device.variables_names.map((variable, idx) => {
                                const fullName = `${device.name}|${variable}`;
                                return (
                                  <div key={idx} className="flex items-center space-x-2">
                                    <input
                                      type="checkbox"
                                      id={`checkbox-${fullName}`}
                                      value={fullName}
                                      checked={modalSelectedVariables.includes(fullName)}
                                      onChange={(e) => {
                                        setModalSelectedVariables((prev) =>
                                          e.target.checked
                                            ? [...prev, fullName]
                                            : prev.filter((v) => v !== fullName)
                                        );
                                      }}
                                      className="checked:bg-button checked:border-button focus:ring-0 checked:ring-0"
                                    />
                                    <label htmlFor={`checkbox-${fullName}`} className="text-button text-lg font-bold">
                                      {variable}
                                    </label>
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      ))
                    )}

                    <button
                      type="button"
                      onClick={() => {
                        register("variables_names")
                        setValue("variables_names", modalSelectedVariables);
                        setInitialSelectedVariables(modalSelectedVariables);
                        handleSubmit(onSubmit)();
                        setIsModalOpen(false);
                      }}
                      className="w-full p-3 bg-button hover:bg-button-hover text-white rounded-lg mt-6 font-bold text-xl"
                    >
                      Save
                    </button>
                  </DialogPanel>
                </Transition>
              </div>
            </div>
          </Dialog>
        </Transition>
      </form>

      {/* Paneles de Dispositivos */}

      {dataGenericDevices.length === 0 && (
        <p className="text-center text-3xl text-button font-bold mt-48">
          No variables have been selected yet. To select them, press the button above.
        </p>
      )}

      {dataGenericDevices.map((device) => (
        <div key={device.name} className="shadow-md rounded-lg border border-button-cancel-card mb-6">
          <div
            onClick={() => toggleDevice(device.name)}
            className="bg-bg-section-outline p-4 rounded-t-lg border-b border-button-cancel-card cursor-pointer flex items-center justify-between w-full"
          >
            <h2 className="font-bold text-2xl text-button">
              {device.name} ({device.type})
            </h2>
            {openStates[device.name] ? (
              <RiArrowDropUpLine className="text-button" size={40} />
            ) : (
              <RiArrowDropDownLine className="text-button" size={40} />
            )}
          </div>

          {openStates[device.name] && dataUser?.id && (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 my-4 mx-4">
              {device.variables?.map((variable) => {
                const variableKey = `${device.name}|${variable.name}`;
                const lastValue = lastData[variableKey] ?? { value: null, timestamp: null };
                return (
                  <VariableCard
                    key={variable.name}
                    variable={variable}
                    last_value={lastValue}
                    deviceName={device.name}
                    deviceType={device.type}
                    userId={dataUser?.id}
                    role={dataUser?.role}
                  />
                );
              })}
            </div>
          )}
        </div>
      ))}


      {(isLoading || isPending) && (
        <div className="fixed inset-0 z-50 bg-bg-modal bg-opacity-50 flex items-center justify-center">
          <PacmanLoader
            color="#0BCCAF"
            loading={true}
            size={50}
          />
        </div>
      )}
    </div>
  );
}