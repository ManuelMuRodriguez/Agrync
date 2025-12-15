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
import { ModbusSlaveTable } from '../types';
import { useEffect, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createSlave, deleteSlave, getSlaves, updateSlave } from '../api/ModbusAPI';
import { MRT_Localization_ES } from 'mantine-react-table/locales/es';
import { DateTime } from 'luxon';
import { toast } from 'react-toastify';
import { modals } from '@mantine/modals';
import { ActionIcon, Tooltip, Button, Flex, Text } from '@mantine/core';
import { IconEdit, IconRefresh, IconTrash } from '@tabler/icons-react';

export default function TablaEsclavosModbus() {

  const [validationErrors, setValidationErrors] = useState<Record<string, string | undefined>>({});
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState<MRT_SortingState>([]);
  const [pagination, setPagination] = useState<MRT_PaginationState>({ pageIndex: 0, pageSize: 10 });
  const [columnFilters, setColumnFilters] = useState<MRT_ColumnFiltersState>([]);
  const [columnFilterFns, setColumnFilterFns] = useState<MRT_ColumnFilterFnsState>({});

  const validateSlaveId = (slave_id: number) =>
    /^[1-9]\d*$/.test(slave_id.toString());

  function validateSlave(slave: ModbusSlaveTable) {
    return {
      name: !slave.name ? 'The name is mandatory.' : undefined,
      slave_id: !validateSlaveId(slave.slave_id) ? 'It must be a positive integer.' : undefined,
      id_device: !slave.id_device ? 'You must select a device.' : undefined,
    };
  }

  const { data: dataTableSlave, error, isError, isFetching, isLoading, refetch } = useQuery({
    queryKey: ['tableSlavesModbus', { columnFilters, columnFilterFns, globalFilter, pagination, sorting }],
    queryFn: () =>
      getSlaves({ columnFilters, columnFilterFns, globalFilter, sorting, pagination }),
    retry: false,
    refetchOnWindowFocus: false,
  });


  const formattedDeviceOptions = dataTableSlave?.devicesAvailable.map(device => ({
    label: device.name,
    value: device.id.toString(),
  })) ?? [];

  const formattedSlaves = useMemo(() => {
    return dataTableSlave?.data.map((slave) => {
      const createdAt = DateTime.fromISO(slave.createdAt, { zone: 'UTC' });
      const updatedAt = DateTime.fromISO(slave.updatedAt, { zone: 'UTC' });

      return {
        ...slave,
        createdAt: createdAt.isValid ? createdAt.setZone('Europe/Madrid').toFormat('dd/MM/yyyy HH:mm:ss') : 'Fecha inválida',
        updatedAt: updatedAt.isValid ? updatedAt.setZone('Europe/Madrid').toFormat('dd/MM/yyyy HH:mm:ss') : 'Fecha inválida',
        id_device: slave.id_device.toString(),
      };
    }) ?? [];
  }, [dataTableSlave]);

  // Estado local sincronizado con datos formateados
  const [tableData, setTableData] = useState<ModbusSlaveTable[]>([]);

  useEffect(() => {
    setTableData(formattedSlaves);
  }, [formattedSlaves]);


  const columns = useMemo<MRT_ColumnDef<ModbusSlaveTable>[]>(() => [
    {
      accessorKey: 'id_device',
      header: 'Id device',
      size: 200,
      enableEditing: true,
      editVariant: 'select',
      mantineEditSelectProps: ({ table }) => ({
        data: formattedDeviceOptions,
        error: validationErrors?.id_device,
        required: true,
        onFocus: () => setValidationErrors((prev) => ({ ...prev, id_device: undefined })),
        disabled: !table.getState().creatingRow,
      }),
      Cell: ({ row }) => {
        const device = formattedDeviceOptions.find(d => d.value === row.original.id_device);
        return device?.label || row.original.name_device || '—';
      },
    },
    {
      accessorKey: 'name',
      header: 'Name',
      enableGrouping: false,
      mantineEditTextInputProps: () => ({
        required: true,
        error: validationErrors?.name,
        onFocus: () => setValidationErrors((prev) => ({ ...prev, name: undefined })),
      }),
    },
    {
      accessorKey: 'slave_id',
      header: 'ID Slave',
      enableGrouping: false,
      mantineEditTextInputProps: () => ({
        required: true,
        error: validationErrors?.slave_id,
        onFocus: () => setValidationErrors((prev) => ({ ...prev, slave_id: undefined })),
        classNames: {
          input: validationErrors?.slave_id ? 'border-2' : 'border-2',
        },
        type: 'number'
      }),
    },
    { accessorKey: 'createdAt', header: 'Date of creation', enableEditing: false, enableGrouping: false },
    { accessorKey: 'updatedAt', header: 'Last modification', enableEditing: false, enableGrouping: false },
  ], [validationErrors, formattedDeviceOptions]);

  useEffect(() => {
    if (columns.length === 0) return;

    const newFilterFns = Object.fromEntries(
      columns.map((col) => [col.accessorKey!, 'contains'])
    );

    const keysOld = Object.keys(columnFilterFns);
    const keysNew = Object.keys(newFilterFns);

    const areEqual =
      keysOld.length === keysNew.length &&
      keysOld.every((key) => columnFilterFns[key] === newFilterFns[key]);

    if (!areEqual) {
      setColumnFilterFns(newFilterFns);
    }
  }, [columns]);

  const queryClient = useQueryClient();

  const { mutateAsync: mutateUpdate } = useMutation({
    mutationFn: updateSlave,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tableVariablesModbus'] });
      queryClient.invalidateQueries({ queryKey: ['tableSlavesModbus'] });
      setValidationErrors({});
      toast.success(data, { closeButton: false, className: 'bg-right-green text-white' });
    },
    onError: (error: any) => {
      toast.error(error?.message ?? 'Unexpected error', { closeButton: false, className: 'bg-error text-white' });
    },
  });

  const { mutate: mutateDelete } = useMutation({
    mutationFn: deleteSlave,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tableVariablesModbus'] });
      queryClient.invalidateQueries({ queryKey: ['tableSlavesModbus'] });
      toast.success(data, { closeButton: false, className: 'bg-right-green text-white' });
    },
    onError: (error: any) => {
      toast.error(error?.message ?? 'Unexpected error', { closeButton: false, className: 'bg-error text-white' });
    },
  });

  const { mutateAsync: mutateCreate } = useMutation({
    mutationFn: createSlave,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tableVariablesModbus'] });
      queryClient.invalidateQueries({ queryKey: ['tableSlavesModbus'] });
      setValidationErrors({});
      toast.success(data, { closeButton: false, className: 'bg-right-green text-white' });
    },
    onError: (error: any) => {
      toast.error(error?.message ?? 'Unexpected error', { closeButton: false, className: 'bg-error text-white' });
    },
  });

  const handleSaveRow: MRT_TableOptions<ModbusSlaveTable>['onEditingRowSave'] = async ({ values, table, row }) => {
    const newErrors = validateSlave(values);
    if (Object.values(newErrors).some(Boolean)) {
      setValidationErrors(newErrors);
      return;
    }

    setValidationErrors({});
    const updatedRow = { ...row.original, ...values };

    try {
      await mutateUpdate({ formData: updatedRow, deviceId: updatedRow.id_device, slaveId: updatedRow.id });

      setTableData((prev) => {
        const newData = [...prev];
        newData[row.index] = updatedRow;
        return newData;
      });

      table.setEditingRow(null);
    } catch (error) {
    }
  };

  const handleCreateRow: MRT_TableOptions<ModbusSlaveTable>['onCreatingRowSave'] = async ({ values, exitCreatingMode }) => {
    const newErrors = validateSlave(values);
    if (Object.values(newErrors).some(Boolean)) {
      setValidationErrors(newErrors);
      return;
    }
    setValidationErrors({});

    try {

      await mutateCreate({ deviceId: values.id_device, formData: values });
      exitCreatingMode();

    } catch (error) {
    }
  };

  const openDeleteConfirmModal = (row: MRT_Row<ModbusSlaveTable>) =>
    modals.openConfirmModal({
      title: 'Confirmar eliminación',
      children: <Text>Are you sure you want to delete the slave {row.original.name}?</Text>,
      labels: { confirm: 'Delete', cancel: 'Cancel' },
      confirmProps: { style: { backgroundColor: '#FB6767', color: 'white' } },
      cancelProps: { style: { backgroundColor: '#D4D4D4', color: 'white' } },
      onConfirm: () => mutateDelete({ deviceId: row.original.id_device, slaveId: row.original.id }),
    });

  const table = useMantineReactTable<ModbusSlaveTable>({
    columns,
    data: tableData,
    enableGrouping: true,
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
    onEditingRowCancel: () => setValidationErrors({}),
    onCreatingRowCancel: () => setValidationErrors({}),
    columnFilterModeOptions: ['contains', 'startsWith', 'endsWith'],
    initialState: { showColumnFilters: true },
    manualFiltering: true,
    manualSorting: true,
    manualPagination: true,
    enableEditing: true,
    mantineTableContainerProps: { sx: { maxWidth: '100%', overflowX: 'auto' } },
    localization: MRT_Localization_ES,
    createDisplayMode: 'row',
    editDisplayMode: 'row',
    onEditingRowSave: handleSaveRow,
    onCreatingRowSave: handleCreateRow,
    renderTopToolbarCustomActions: ({ table }) => (
      <Flex justify="space-between" align="center">
        <Button onClick={() => table.setCreatingRow(true)}>Create New Slave</Button>
        <Tooltip label="Refrescar">
          <ActionIcon onClick={() => refetch()}><IconRefresh /></ActionIcon>
        </Tooltip>
      </Flex>
    ),
    renderRowActions: ({ row, table }) => (
      <Flex gap="md" style={{ overflowX: 'auto', whiteSpace: 'nowrap' }}>
        <Tooltip label='Editar'>
          <ActionIcon variant="light" color="gray" onClick={() => table.setEditingRow(row)} className="text-button-edit bg-gap hover:text-white hover:bg-button-edit disabled:text-button-cancel-card">
            <IconEdit />
          </ActionIcon>
        </Tooltip>
        <Tooltip label='Eliminar'>
          <ActionIcon color="red" onClick={() => openDeleteConfirmModal(row)} className="text-error bg-gap hover:text-white hover:bg-error disabled:text-button-cancel-card">
            <IconTrash />
          </ActionIcon>
        </Tooltip>
      </Flex>
    ),
    onColumnFilterFnsChange: setColumnFilterFns,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    rowCount: dataTableSlave?.totalRowCount ?? 0,
    state: {
      columnFilterFns,
      columnFilters,
      globalFilter,
      isLoading,
      pagination,
      showProgressBars: isFetching,
      sorting,
    },
  });

  useEffect(() => {
    if (isError && error) {
      toast.error(error.message || 'Error loading slaves', {
        closeButton: false,
        className: 'bg-error text-white',
      });
    }
  }, [isError, error]);

  return <MantineReactTable table={table} />;
}
