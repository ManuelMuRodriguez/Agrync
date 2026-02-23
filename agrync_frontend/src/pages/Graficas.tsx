

import { useForm } from "react-hook-form";
import { useState, useEffect, Fragment } from "react";
import { DateTimePicker } from '@mantine/dates';
import { Dialog, Transition, DialogPanel } from '@headlessui/react';
import dayjs from 'dayjs';
import 'dayjs/locale/es';
import { useGenericDevicesNames } from "../hooks/useGenericDevicesNames";
import { GoDash } from "react-icons/go";
import { IoRadio } from "react-icons/io5";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import { FormGraficas, GenericDevicesNames, HistoricalData } from "../types";
import { useMutation } from "@tanstack/react-query";
import { toast } from "react-toastify";
import { getHistoricalData } from "../api/GenericDevicesApi";
import { useAuth } from "../hooks/useAuth";
import highchartsAccessibility from "highcharts/modules/accessibility";
import highchartsExporting from 'highcharts/modules/exporting';
import { DateTime } from 'luxon';
import { PacmanLoader } from "react-spinners";
import { useTranslation } from "react-i18next";

if (typeof highchartsAccessibility === 'function') {
    highchartsAccessibility(Highcharts);
}

if (typeof highchartsExporting === 'function') {
    highchartsExporting(Highcharts);
}

dayjs.locale('es');

export default function Graficas() {
    const { t } = useTranslation();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [devices, setDevices] = useState<GenericDevicesNames>([]);
    const [initialSelectedVariables, setInitialSelectedVariables] = useState<string[]>([]);
    const [modalSelectedVariables, setModalSelectedVariables] = useState<string[]>([]);
    const [tempStartDate, setTempStartDate] = useState<Date | null>(null);
    const [tempEndDate, setTempEndDate] = useState<Date | null>(null);
    const [chartData, setChartData] = useState<HistoricalData>([]);

    const optionsAgregation = [
        { name: t('charts.noAggregation'), value: 'sin' },
        { name: t('charts.byHours'), value: 'horas' },
        { name: t('charts.byDays'), value: 'dias' }
    ];

    const initialValues: FormGraficas = {
        variables_names: [],
        start_date: null,
        end_date: null,
        aggregation: "sin"
    };

    const { register, handleSubmit, watch, setValue } = useForm({
        mode: "onTouched",
        reValidateMode: "onChange",
        shouldFocusError: true,
        defaultValues: initialValues
    });

    // Retrieve saved form values
    const selectedCheckboxes = watch("variables_names") as string[] || [];
    const fechaInicio = watch("start_date");
    const fechaFin = watch("end_date");
    const aggregation = watch("aggregation");

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



    const { mutate, isPending } = useMutation({
        mutationFn: getHistoricalData,
        onError: (error) => {
            toast.error(error.message, {
                closeButton: false,
                className: 'bg-error text-white'
            })
        },
        onSuccess: (data: HistoricalData) => {
            setChartData(data);
            toast.success(t('charts.dataLoaded'), {
                closeButton: false,
                className: 'bg-right-green text-white'
            })
        }

    })



    const onSubmit = (formData: FormGraficas) => {

        const userId = dataUser?.id;

        if (userId) {

            mutate({
                formData,
                userId: userId
            });

        }
    };





    // Run query only when all conditions are met
    useEffect(() => {
        if (fechaInicio && fechaFin && selectedCheckboxes.length > 0) {
            handleSubmit(onSubmit)();
        }
    }, [fechaInicio, fechaFin, selectedCheckboxes, aggregation]);

    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 1);





    return (
        <div className="w-auto flex flex-col space-y-12 min-w-lg ml-5">
            <form
                onSubmit={handleSubmit(onSubmit)}
                className="flex flex-col space-y-12"
                noValidate
            >
                {/* Fecha de Inicio con DatetimePicker de Mantine */}
                <div className="w-2/3">
                    <label htmlFor="fecha_inicio" className="block text-button text-2xl font-bold">{t('charts.dateRange')}</label>
                    <div className="flex flex-row items-center gap-2">
                        <div className="flex-1 min-w-72">
                            {/* @ts-expect-error: Suppress onChange type mismatch – value is handled manually */}
                            <DateTimePicker
                                
                                withSeconds={true}
                                dropdownType="modal"
                                id="start_date"
                                locale="es"
                                placeholder={t('charts.startDate')}
                                {...register("start_date")}
                                //onChange={(date) => setValue("start_date", date)}
                                onChange={(date) => {
                                    setTempStartDate(date); // Temporarily store the date while the user is picking
                                }}
                                classNames={{
                                    day: 'data[selected]:hover:bg-button-hover data-[selected]:bg-button data-[selected]:text-white ',
                                    input: `flex-1 p-3 border-2 rounded-lg focus:border-button text-2xl font-inter placeholder:text-gap font-medium ${fechaInicio ? 'border-button' : 'border-gap'}`,
                                    wrapper: 'rounded-lg',

                                    calendarHeaderControl: 'text-white bg-button hover:bg-button-hover'
                                    
                                }}
                                submitButtonProps={{
                                    bg: "text-button disabled:bg-button-hover",
                                    color: "text-white"

                                }}
                                size={'lg'}
                                maxDate={fechaFin || maxDate}
                                timeInputProps={{
                                    classNames: {
                                        input: 'selection:bg-button border-2 focus:ring-0 focus:border-button',
                                    },
                                }}
                                popoverProps={{
                                    classNames: {
                                        dropdown: 'shadow-lg rounded-lg border border-gray-200'
                                    },
                                    onClose: () => {
                                        if (tempStartDate) {
                                            setValue("start_date", tempStartDate);
                                        }
                                    }
                                }}
                            />
                        </div>

                        <GoDash className="flex-shrink-0 text-button" />
                        {/* Fecha de Fin con DatetimePicker de Mantine */}
                        <div className="flex-1 min-w-72">
                            {/* @ts-expect-error: Suppress onChange type mismatch – value is handled manually */}
                            <DateTimePicker
                                dropdownType="modal"
                                withSeconds
                                id="end_date"
                                locale="es"
                                placeholder={t('charts.endDate')}
                                {...register("end_date")}
                                //onChange={(date) => setValue("end_date", date)} 
                                onChange={(date) => {
                                    setTempEndDate(date); // Temporarily store the date while the user is picking
                                }}
                                classNames={{
                                    day: ' data-[selected]:bg-button data-[selected]:text-white data[selected]:hover:bg-button-hover',
                                    input: `flex-1 p-3 border-2 rounded-lg text-2xl font-inter placeholder:text-gap font-medium ${fechaFin ? 'border-button' : 'border-gap'}`,
                                    wrapper: 'rounded-lg',
                                    calendarHeaderControl: 'text-white bg-button hover:bg-button-hover'

                                }}
                                size={'lg'}
                                timeInputProps={{
                                    classNames: {
                                        input: 'selection:bg-button focus:ring-0 border-2 focus:border-button',
                                    },
                                }}
                                popoverProps={{
                                    classNames: {
                                        dropdown: 'shadow-lg rounded-lg border border-gray-200'
                                    },
                                    onClose: () => {
                                        if (tempEndDate) {
                                            setValue("end_date", tempEndDate);
                                        }
                                    }
                                }}
                                disabled={!fechaInicio} // End date field is disabled until a start date is selected
                                minDate={fechaInicio || undefined} 
                                maxDate={maxDate}
                            />

                        </div>
                    </div>
                </div>

                {/* Select de Agregación */}
                <div className="w-1/4">
                    <label htmlFor="agregation" className="block text-button text-2xl font-bold">{t('charts.aggregation')}</label>
                    <select
                        id="agregation"
                        className="block w-full min-w-60 rounded-md border-gap focus:border-button focus:ring-button font-medium text-2xl"
                        defaultValue={optionsAgregation[0].value}
                        {...register("aggregation")}
                    >
                        {optionsAgregation.map((optionAgregation) => {
                            return (
                                <option className='font-medium'
                                    value={optionAgregation.value}
                                    key={optionAgregation.name}>{optionAgregation.name}</option>
                            )
                        })}
                    </select>
                </div>

                {/* Botón para abrir el Modal */}
                <button
                    type="button"
                    onClick={handleModalOpen}
                    className="flex items-center gap-2 justify-center bg-button hover:bg-button-hover w-full p-3 rounded-lg text-white font-medium text-2xl cursor-pointer"
                >
                    <IoRadio /> {t('charts.selectVariables')}
                </button>

                {/* Modal con Headless UI */}
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
                                            <p className="text-button text-center text-xl font-bold">{t('charts.noDevices')}</p>
                                        ) : (
                                            devices.map((device, index) => (
                                                <div key={index} className="space-y-4 last:mb-0 mb-8">
                                                    <div>
                                                        <p className="text-xl font-bold text-button">{device.name}</p>
                                                        <hr className="border-black my-2" />
                                                    </div>

                                                    {device.variables_names.length === 0 || isError ? (
                                                        <p className="text-center text-button font-bold">{t('charts.noVariables')}</p>
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

                                        {/* Botón Guardar */}
                                        <button
                                            type="button"
                                            onClick={() => {
                                                register("variables_names")
                                                setValue("variables_names", modalSelectedVariables);
                                                setInitialSelectedVariables(modalSelectedVariables);
                                                setIsModalOpen(false);
                                            }}
                                            className="w-full p-3 bg-button hover:bg-button-hover text-white rounded-lg mt-6 font-bold text-xl"
                                        >
                                            {t('charts.save')}
                                        </button>
                                    </DialogPanel>
                                </Transition>
                            </div>
                        </div>
                    </Dialog>
                </Transition>
            </form>

            {chartData.length === 0 ? (
                <p className="text-3xl font-bold text-center text-button">{t('charts.noData')}</p>
            ) : (
                <div className="w-full min-w-0 border-2 border-button rounded-lg p-4 bg-white shadow-md">
                    <HighchartsReact
                        highcharts={Highcharts}
                        options={{
                            credits: {
                                enabled: false
                            },
                            lang: {
                                viewFullscreen: "View in full screen",
                                downloadPNG: "Download PNG",
                                downloadJPEG: "Download JPEG",
                                downloadSVG: "Download SVG",
                                downloadPDF: "Download PDF",
                                printChart: "Print Chart"
                            },
                            chart: {
                                style: {
                                    fontFamily: 'Inter, sans-serif',
                                    color: '#056153'
                                },
                                zoomType: 'x'
                            },
                            exporting: {
                                buttons: {
                                    contextButton: {
                                        menuItems: ['downloadPNG', 'downloadJPEG', 'downloadSVG', 'downloadPDF', 'separator', 'printChart', 'viewFullscreen']
                                    }
                                }
                            },
                            title: {
                                text: t('charts.chartTitle'),
                                style: {
                                    color: '#056153',
                                },
                            },
                            xAxis: {

                                labels: {
                                    style: {
                                        color: '#056153',
                                    },
                                    rotation: -25,
                                },
                                type: 'datetime',
                                ordinal: false,
                                style: {
                                    color: '#056153',
                                }
                            },
                            yAxis: {
                                title: {
                                    text: t('charts.yAxisTitle'),
                                    style: {
                                        color: '#056153',
                                    }
                                },
                            },
                            tooltip: {
                                shared: true, crosshairs: true,
                                borderWidth: 1,
                                dateTimeLabelFormats: {

                                    year: '%d/%m/%Y %H:%M:%S',
                                    month: '%d/%m/%Y %H:%M:%S',
                                    week: '%d/%m/%Y %H:%M:%S',
                                    day: '%d/%m/%Y %H:%M:%S',
                                    hour: '%d/%m/%Y %H:%M',
                                    minute: '%d/%m/%Y %H:%M',
                                    second: '%d/%m/%Y %H:%M:%S',
                                    millisecond: '%d/%m/%Y %H:%M:%S',
                                },
                                style: {
                                    fontFamily: 'Inter, sans-serif'
                                }
                            },
                            series: chartData.map((variable) => ({
                                type: 'line',
                                name: variable.name,
                                data: variable.series.map((point) => [
                                    DateTime.fromISO(point.timestamp, { zone: 'UTC' }).setZone('Europe/Madrid').toMillis(),
                                    point.value
                                ]

                                ),
                            })),
                        }}
                    />
                </div>
            )}

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