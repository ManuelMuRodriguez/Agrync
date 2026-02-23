import {
    MantineReactTable,
    useMantineReactTable,
    type MRT_ColumnDef,
    type MRT_TableOptions,
    type MRT_ColumnFilterFnsState,
    type MRT_ColumnFiltersState,
    type MRT_SortingState,
    type MRT_PaginationState,
    type MRT_Row,
} from 'mantine-react-table';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { DateTime } from 'luxon';
import { toast } from 'react-toastify';
import { modals } from '@mantine/modals';
import { ActionIcon, Tooltip, Button, Flex, Text } from '@mantine/core';
import { IconEdit, IconRefresh, IconTrash } from '@tabler/icons-react';
import { getVariables, updateVariable, deleteVariable, createVariable } from '../api/ModbusAPI';
import { MRT_Localization_ES } from 'mantine-react-table/locales/es';
import { endianOptions, ModbusVariableTable, opcTypes } from '../types';

export default function TablaVariablesModbus() {
    const { t } = useTranslation();
    const [validationErrors, setValidationErrors] = useState<Record<string, string | undefined>>({});
    const [globalFilter, setGlobalFilter] = useState('');
    const [sorting, setSorting] = useState<MRT_SortingState>([]);
    const [pagination, setPagination] = useState<MRT_PaginationState>({ pageIndex: 0, pageSize: 10 });
    const [columnFilters, setColumnFilters] = useState<MRT_ColumnFiltersState>([]);
    const [columnFilterFns, setColumnFilterFns] = useState<MRT_ColumnFilterFnsState>({});


    function cleanObject<T extends Record<string, any>>(obj: T): Partial<T> {
        const cleaned: Partial<T> = {};
        for (const key in obj) {
            const val = obj[key];
            if (val === '' || val === '---' || val === null) {
                cleaned[key] = undefined;
            } else {
                cleaned[key] = val;
            }
        }
        return cleaned;
    }


    function validateVariable(variable: ModbusVariableTable) {
        return {
            id_device_slave: !variable.id_device_slave || variable.id_device_slave.trim() === ''
                ? t('variablesTable.slaveRequired')
                : undefined,
            name: !variable.name ? t('variablesTable.nameRequired') : undefined,
            type: !variable.type ? t('variablesTable.typeRequired') : undefined,
            address:
                variable.address === null ||
                    variable.address === undefined ||
                    isNaN(Number(variable.address)) ||
                    Number(variable.address) <= 0
                    ? t('variablesTable.addressRequired')
                    : undefined,

            scaling:
                variable.scaling !== null && variable.scaling !== undefined && variable.scaling.toString() !== '' &&
                    Number(variable.scaling) <= 0
                    ? t('variablesTable.scalingRequired')
                    : undefined,

            decimals:
                variable.decimals !== null && variable.decimals !== undefined && variable.decimals.toString() !== '' &&
                    (isNaN(Number(variable.decimals)) || !Number.isInteger(Number(variable.decimals)) || Number(variable.decimals) < 0)
                    ? t('variablesTable.decimalsRequired')
                    : undefined,

            interval:
                variable.interval !== null && variable.interval !== undefined && variable.interval.toString() !== '' &&
                    (isNaN(Number(variable.interval)) || !Number.isInteger(Number(variable.interval)) || Number(variable.interval) <= 1)
                    ? t('variablesTable.intervalRequired')
                    : undefined,

            length:
                variable.length !== null && variable.length !== undefined && variable.length.toString() !== '' &&
                    (isNaN(Number(variable.length)) || !Number.isInteger(Number(variable.length)) || Number(variable.length) <= 0)
                    ? t('variablesTable.lengthRequired')
                    : undefined,

            min_value:
                variable.min_value !== null && variable.min_value !== undefined &&
                    isNaN(Number(variable.min_value))
                    ? t('variablesTable.minValueRequired')
                    : undefined,

            max_value:
                variable.max_value !== null && variable.max_value !== undefined &&
                    isNaN(Number(variable.max_value))
                    ? t('variablesTable.maxValueRequired')
                    : undefined,
        };
    }

    const { data: dataTableVariables, error, isError, isFetching, isLoading, refetch } = useQuery({
        queryKey: ['tableVariablesModbus', { columnFilters, columnFilterFns, globalFilter, pagination, sorting }],
        queryFn: () =>
            getVariables({ columnFilters, columnFilterFns, globalFilter, sorting, pagination }),
        retry: false,
        refetchOnWindowFocus: false,
    });

    //const normalizeValue = (val: any) => (val === null || val === undefined || val === '' ? '---' : val);

    const formattedDeviceSlaveOptions = dataTableVariables?.devicesSlavesAvailable.map(ds => ({
        label: `${ds.name_device}-${ds.name_slave}`,
        value: `${ds.id_db_device}-${ds.id_db_slave}`,
    })) ?? [];

    const formattedVariables = useMemo(() => {
        return dataTableVariables?.data.map(variable => {
            const createdAt = DateTime.fromISO(variable.createdAt, { zone: 'UTC' });
            const updatedAt = DateTime.fromISO(variable.updatedAt, { zone: 'UTC' });

            const id_device_slave = `${variable.id_db_device}-${variable.id_db_slave}`;

            return {
                ...variable,
                id_device_slave,
                //scaling: normalizeValue(variable.scaling),
                //writable: normalizeValue(variable.writable),
                //min_value: normalizeValue(variable.min_value),
                //max_value: normalizeValue(variable.max_value),
                //unit: normalizeValue(variable.unit),
                createdAt: createdAt.isValid ? createdAt.setZone('Europe/Madrid').toFormat('dd/MM/yyyy HH:mm:ss') : t('common.invalidDate'),
                updatedAt: updatedAt.isValid ? updatedAt.setZone('Europe/Madrid').toFormat('dd/MM/yyyy HH:mm:ss') : t('common.invalidDate'),
            };
        }) ?? [];
    }, [dataTableVariables]);

    const [tableData, setTableData] = useState<ModbusVariableTable[]>([]);

    useEffect(() => {
        setTableData(formattedVariables);
    }, [formattedVariables]);

    const columns = useMemo<MRT_ColumnDef<ModbusVariableTable>[]>(() => [
        {
            accessorKey: 'id_device_slave',
            header: t('variablesTable.deviceSlave'),
            editVariant: 'select',
            enableEditing: true,
            mantineEditSelectProps: ({ table }) => ({
                data: formattedDeviceSlaveOptions,
                error: validationErrors?.id_device_slave,
                required: true,
                onFocus: () => setValidationErrors((prev) => ({ ...prev, id_device_slave: undefined })),
                disabled: !table.getState().creatingRow,
            }),
            Cell: ({ row }) => `${row.original.name_device} - ${row.original.name_slave}`
        },
        {
            accessorKey: 'name',
            header: t('variablesTable.name'),
            enableGrouping: false,
            mantineEditTextInputProps: () => ({
                required: true,
                error: validationErrors?.name,
                onFocus: () => setValidationErrors((prev) => ({ ...prev, name: undefined })),
            }),
        },
        {
            accessorKey: 'type',
            header: t('variablesTable.type'),
            editVariant: 'select',
            mantineEditSelectProps: ({ table }) => ({
                data: opcTypes,
                required: true,
                error: validationErrors?.type,
                onFocus: () => setValidationErrors((prev) => ({ ...prev, type: undefined })),
                classNames: {
                    input: validationErrors?.type ? 'border-2' : 'border-2 border-gap',
                },
                disabled: !table.getState().creatingRow
            }),
        },
        {
            accessorKey: 'address',
            header: t('variablesTable.address'),
            enableGrouping: false,
            mantineEditTextInputProps: ({ table }) => ({
                type: 'number',
                required: true,
                error: validationErrors?.address,
                onFocus: () => setValidationErrors((prev) => ({ ...prev, address: undefined })),
                disabled: !table.getState().creatingRow,
            }),
        },
        {
            accessorKey: 'scaling',
            header: t('variablesTable.scaling'),
            enableGrouping: false,
            mantineEditTextInputProps: ({ table }) => ({
                type: 'number',
                error: validationErrors?.scaling,
                onFocus: () => setValidationErrors((prev) => ({ ...prev, scaling: undefined })),
                disabled: !table.getState().creatingRow
            }),
            Cell: ({ cell }) => {
                const value = cell.getValue();
                if (value === null || value === undefined || value === '') return '---';
                return <>{value}</>;
            }
        },
        {
            accessorKey: 'decimals',
            header: t('variablesTable.decimals'),
            enableGrouping: false,
            mantineEditTextInputProps: ({ table }) => ({
                type: 'number',
                error: validationErrors?.decimals,
                onFocus: () => setValidationErrors((prev) => ({ ...prev, decimals: undefined })),
                classNames: {
                    input: validationErrors?.decimals ? 'border-2' : 'border-2',
                },
                disabled: !table.getState().creatingRow
            }),
        },
        {
            accessorKey: 'endian',
            header: t('variablesTable.endian'),
            editVariant: 'select',
            enableGrouping: false,
            mantineEditSelectProps: ({ table }) => ({
                data: endianOptions,
                disabled: !table.getState().creatingRow
            }),
        },
        {
            accessorKey: 'interval',
            header: t('variablesTable.interval'),
            enableGrouping: false,
            mantineEditTextInputProps: () => ({
                type: 'number',
                error: validationErrors?.interval,
                onFocus: () => setValidationErrors((prev) => ({ ...prev, interval: undefined })),
                classNames: {
                    input: validationErrors?.interval ? 'border-2' : 'border-2 border-gap',
                },
            }),
        },
        {
            accessorKey: 'length',
            header: t('variablesTable.length'),
            enableGrouping: false,
            mantineEditTextInputProps: ({ table }) => ({
                type: 'number',
                error: validationErrors?.length,
                onFocus: () => setValidationErrors((prev) => ({ ...prev, length: undefined })),
                classNames: {
                    input: validationErrors?.length ? 'border-2' : 'border-2 border-gap',
                },
                disabled: !table.getState().creatingRow
            }),
        },
        {
            accessorKey: 'writable',
            header: t('variablesTable.writable'),
            editVariant: 'select',
            enableGrouping: false,
            Cell: ({ cell }) => cell.getValue() === true ? t('variablesTable.yes') : t('variablesTable.no'),
            mantineEditSelectProps: () => ({
                data: [
                    { label: t('variablesTable.yes'), value: "true" },
                    { label: t('variablesTable.no'), value: "false" },
                ],
            }),
        },
        {
            accessorKey: 'min_value',
            header: t('variablesTable.minValue'),
            enableGrouping: false,
            mantineEditTextInputProps: () => ({
                type: 'number',
                error: validationErrors?.min_value,
                onFocus: () => setValidationErrors((prev) => ({ ...prev, min_value: undefined })),
                classNames: {
                    input: validationErrors?.min_value ? 'border-2' : 'border-2 border-gap',
                },
            }),
            Cell: ({ cell }) => {
                const value = cell.getValue();
                if (value === null || value === undefined || value === '') return '---';
                return <>{value}</>; 
            }
        },
        {
            accessorKey: 'max_value',
            header: t('variablesTable.maxValue'),
            enableGrouping: false,
            mantineEditTextInputProps: () => ({
                type: 'number',
                error: validationErrors?.max_value,
                onFocus: () => setValidationErrors((prev) => ({ ...prev, max_value: undefined })),
                classNames: {
                    input: validationErrors?.max_value ? 'border-2' : 'border-2 border-gap',
                },
            }),
            Cell: ({ cell }) => {
                const value = cell.getValue();
                if (value === null || value === undefined || value === '') return '---';
                return <>{value}</>; 
            }
        },
        {
            accessorKey: 'unit',
            header: t('variablesTable.unit'),
            enableGrouping: false,
            Cell: ({ cell }) => {
                const value = cell.getValue();
                if (value === null || value === undefined || value === '') return '---';
                return <>{value}</>; 
            }
        },
        { accessorKey: 'createdAt', header: t('variablesTable.createdAt'), enableEditing: false, enableGrouping: false },
        { accessorKey: 'updatedAt', header: t('variablesTable.updatedAt'), enableEditing: false, enableGrouping: false },
    ], [validationErrors, formattedDeviceSlaveOptions, t]);

    useEffect(() => {
        if (columns.length === 0) return;
        const newFilterFns = Object.fromEntries(columns.map(col => [col.accessorKey!, 'contains']));
        const keysOld = Object.keys(columnFilterFns);
        const keysNew = Object.keys(newFilterFns);
        const areEqual = keysOld.length === keysNew.length && keysOld.every(key => columnFilterFns[key] === newFilterFns[key]);
        if (!areEqual) setColumnFilterFns(newFilterFns);
    }, [columns]);

    const queryClient = useQueryClient();

    const { mutateAsync: mutateUpdate } = useMutation({
        mutationFn: updateVariable,
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['tableVariablesModbus'] });
            setValidationErrors({});
            toast.success(data, { closeButton: false, className: 'bg-right-green text-white' });
        },
        onError: (error: any) => {
            toast.error(error?.message ?? t('variablesTable.unexpectedError'), { closeButton: false, className: 'bg-error text-white' });
        }
    });

    const { mutate: mutateDelete } = useMutation({
        mutationFn: deleteVariable,
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['tableVariablesModbus'] });
            toast.success(data, { closeButton: false, className: 'bg-right-green text-white' });
        },
        onError: (error: any) => {
            toast.error(error?.message ?? t('variablesTable.unexpectedError'), { closeButton: false, className: 'bg-error text-white' });
        },
    });

    const { mutateAsync: mutateCreate } = useMutation({
        mutationFn: createVariable,
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['tableVariablesModbus'] });
            setValidationErrors({});
            toast.success(data, { closeButton: false, className: 'bg-right-green text-white' });
        },
        onError: (error: any) => {
            toast.error(error?.message ?? t('variablesTable.unexpectedError'), { closeButton: false, className: 'bg-error text-white' });
        },
    });



    const handleSaveRow: MRT_TableOptions<ModbusVariableTable>['onEditingRowSave'] = async ({ values, table, row }) => {
        const newErrors = validateVariable(values);
        if (Object.values(newErrors).some(Boolean)) {
            setValidationErrors(newErrors);
            return;
        }

        setValidationErrors({});

        const [deviceId, slaveId] = values.id_device_slave.split('-');
        const updatedRow: ModbusVariableTable = {
            ...row.original,
            ...values,
            id_db_device: deviceId,
            id_db_slave: slaveId,
        };


        try {

            const cleanedPartial = cleanObject(updatedRow);

            const updatedRowCleaned: ModbusVariableTable = {
                ...updatedRow,
                ...cleanedPartial,
                interval: updatedRow.interval != null ? Number(updatedRow.interval) : null,
                writable: updatedRow.writable != null && (String(updatedRow.writable) === 'true' || updatedRow.writable === true),
                min_value: updatedRow.min_value != null ? Number(updatedRow.min_value) : null,
                max_value: updatedRow.max_value != null ? Number(updatedRow.max_value) : null,
                scaling: updatedRow.scaling != null ? Number(updatedRow.scaling) : null,
            };


            await mutateUpdate({
                formData: updatedRowCleaned,
                deviceId,
                slaveId,
                variableId: updatedRow.id,
            });

            //setTableData((prev) => {
            //    const newData = [...prev];
            //    newData[row.index] = updatedRowCleaned;
            //    return newData;
            //});

            setTableData((prev) => {
                return prev.map(item => item.id === updatedRowCleaned.id ? updatedRowCleaned : item);
            });

            table.setEditingRow(null);
        } catch (error) {
        }
    };

    const handleCreateRow: MRT_TableOptions<ModbusVariableTable>['onCreatingRowSave'] = async ({ values, exitCreatingMode }) => {
        const newErrors = validateVariable(values);
        if (Object.values(newErrors).some(Boolean)) {
            setValidationErrors(newErrors);
            return;
        }

        setValidationErrors({});

        const [id_db_device, id_db_slave] = values.id_device_slave.split('-');

        const newVariable = {
            ...values,
            id_db_device,
            id_db_slave,
        };

        try {

            const cleanedVariable = cleanObject(newVariable) as ModbusVariableTable;

            await mutateCreate({
                deviceId: id_db_device,
                slaveId: id_db_slave,
                formData: cleanedVariable,
            });

            exitCreatingMode();
        } catch (error) {
        }
    };

    const openDeleteConfirmModal = (row: MRT_Row<ModbusVariableTable>) =>
        modals.openConfirmModal({
            title: t('variablesTable.confirmDelete'),
            children: <Text>{t('variablesTable.confirmDeleteMsg', { name: row.original.name })}</Text>,
            labels: { confirm: t('variablesTable.delete'), cancel: t('variablesTable.cancel') },
            confirmProps: { style: { backgroundColor: '#FB6767', color: 'white' } },
            cancelProps: { style: { backgroundColor: '#D4D4D4', color: 'white' } },
            onConfirm: () =>
                mutateDelete({
                    deviceId: row.original.id_db_device,
                    slaveId: row.original.id_db_slave,
                    variableId: row.original.id,
                }),
        });

    const table = useMantineReactTable<ModbusVariableTable>({
        columns,
        data: tableData,
        enableEditing: true,
        enableGrouping: true,
        createDisplayMode: 'row',
        editDisplayMode: 'row',
        enableColumnFilterModes: true,
        enableColumnResizing: true,
        enableStickyHeader: true,
        mantineTableHeadCellProps: ({ column }) => ({
            style: {
                color: '#033F36',
                ...(column.id === 'mrt-row-actions' ? { minWidth: 120, whiteSpace: 'nowrap' } : {}),
            },
        }),
        mantineTableBodyCellProps: ({ column }) => ({
            style: {
                color: '#033F36',
                ...(column.id === 'mrt-row-actions' ? { minWidth: 120, whiteSpace: 'nowrap' } : {}),
            },
        }),
        manualFiltering: true,
        manualSorting: true,
        manualPagination: true,
        localization: MRT_Localization_ES,
        state: {
            columnFilterFns,
            columnFilters,
            globalFilter,
            isLoading,
            pagination,
            showProgressBars: isFetching,
            sorting,
        },
        onEditingRowCancel: () => setValidationErrors({}),
        onCreatingRowCancel: () => setValidationErrors({}),
        columnFilterModeOptions: ['contains', 'startsWith', 'endsWith'],
        initialState: { showColumnFilters: true },
        onEditingRowSave: handleSaveRow,
        onCreatingRowSave: handleCreateRow,
        onColumnFilterFnsChange: setColumnFilterFns,
        onColumnFiltersChange: setColumnFilters,
        onGlobalFilterChange: setGlobalFilter,
        onSortingChange: setSorting,
        onPaginationChange: setPagination,
        rowCount: dataTableVariables?.totalRowCount ?? 0,
        mantineTableContainerProps: { sx: { maxWidth: '100%', overflowX: 'auto' } },
        renderTopToolbarCustomActions: ({ table }) => (
            <Flex justify="space-between" align="center">
                <Button onClick={() => table.setCreatingRow(true)}>{t('variablesTable.createNew')}</Button>
                <Tooltip label={t('variablesTable.refresh')}>
                    <ActionIcon onClick={() => refetch()}><IconRefresh /></ActionIcon>
                </Tooltip>
            </Flex>
        ),
        renderRowActions: ({ row, table }) => (
            <Flex gap="md" style={{ overflowX: 'auto', whiteSpace: 'nowrap' }}>
                <Tooltip label={t('variablesTable.edit')}>
                    <ActionIcon variant="light" color="gray" onClick={() => table.setEditingRow(row)} className="text-button-edit bg-gap hover:text-white hover:bg-button-edit disabled:text-button-cancel-card">
                        <IconEdit />
                    </ActionIcon>
                </Tooltip>
                <Tooltip label={t('variablesTable.remove')}>
                    <ActionIcon color="red" onClick={() => openDeleteConfirmModal(row)} className="text-error bg-gap hover:text-white hover:bg-error disabled:text-button-cancel-card">
                        <IconTrash />
                    </ActionIcon>
                </Tooltip>
            </Flex>
        ),
    });

    useEffect(() => {
        if (isError && error) {
            toast.error(error.message || t('variablesTable.errorLoading'), {
                closeButton: false,
                className: 'bg-error text-white',
            });
        }
    }, [isError, error]);

    return <MantineReactTable table={table} />;
}
