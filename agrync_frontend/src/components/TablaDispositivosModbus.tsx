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
import { ActionIcon, Tooltip, Button, Flex, Text } from '@mantine/core';
import { useEffect, useMemo, useState } from "react";
import { ModbusDeviceTable } from "../types";
import { createDevice, deleteDevice, getDevices, updateDevice } from '../api/ModbusAPI';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { DateTime } from 'luxon';
import { toast } from 'react-toastify';
import { modals } from '@mantine/modals';
import { MRT_Localization_ES } from 'mantine-react-table/locales/es';
import { IconEdit, IconRefresh, IconTrash } from '@tabler/icons-react';
import { useTranslation } from 'react-i18next';


export default function TablaDispositivosModbus() {

    const { t } = useTranslation();
    const [validationErrors, setValidationErrors] = useState<Record<string, string | undefined>>({});
    const [columnFilters, setColumnFilters] = useState<MRT_ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState<MRT_SortingState>([]);
  const [pagination, setPagination] = useState<MRT_PaginationState>({ pageIndex: 0, pageSize: 10 });

    const validateIp = (ip: string) =>
        !!ip && /^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$/.test(ip);
    
      // Validate full device
      function validateDevice(device: ModbusDeviceTable) {
        return {
          name: !device.name ? t('devicesTable.nameRequired') : undefined,
          ip: !validateIp(device.ip) ? t('devicesTable.invalidIp') : undefined
        };
      }

    const columns = useMemo<MRT_ColumnDef<ModbusDeviceTable>[]>(() => [
    {
      accessorKey: 'name',
      header: t('devicesTable.name'),
      mantineEditTextInputProps: () => ({
        required: true,
        error: validationErrors?.name,
        onFocus: () => setValidationErrors((prev) => ({ ...prev, name: undefined })),
        classNames: {
          input: validationErrors?.name ? 'border-2' : 'border-2',

        },
      }),
    },
    {
      accessorKey: 'ip',
      header: t('devicesTable.ipAddress'),
      mantineEditTextInputProps: () => ({
        required: true,
        error: validationErrors?.ip,
        onFocus: () => setValidationErrors((prev) => ({ ...prev, ip: undefined })),
        classNames: {
          input: validationErrors?.ip ? 'border-2' : 'border-2',
        },
      }),
    },
    { accessorKey: 'createdAt', header: t('devicesTable.createdAt'), enableEditing: false },
    { accessorKey: 'updatedAt', header: t('devicesTable.updatedAt'), enableEditing: false },
  ], [validationErrors]);


  const [columnFilterFns, setColumnFilterFns] = useState<MRT_ColumnFilterFnsState>(
  Object.fromEntries(columns.map((col) => [col.accessorKey!, 'contains']))
  );


  const { data: dataTableDevice, error, isError, isFetching, isLoading, refetch } = useQuery({
      queryKey: ['tableDevicesModbus', { columnFilters, columnFilterFns, globalFilter, pagination, sorting }],
      queryFn: () =>
        getDevices({
          columnFilters,
          columnFilterFns,
          globalFilter,
          sorting,
          pagination,
        }),
      retry: false,
      refetchOnWindowFocus: false,
    });


    const formattedDevices = useMemo(() => {
        return dataTableDevice?.data.map((device) => {
          const createdAt = DateTime.fromISO(device.createdAt, { zone: 'UTC' });
          const updatedAt = DateTime.fromISO(device.updatedAt, { zone: 'UTC' });
    
          return {
            ...device,
            createdAt: createdAt.isValid
              ? createdAt.setZone('Europe/Madrid').toFormat('dd/MM/yyyy HH:mm:ss')
              : 'Invalid date',
            updatedAt: updatedAt.isValid
              ? updatedAt.setZone('Europe/Madrid').toFormat('dd/MM/yyyy HH:mm:ss')
              : 'Invalid date',
          };
        }) ?? [];
      }, [dataTableDevice]);

      const queryClient = useQueryClient();
      
       
        const { mutateAsync: mutateUpdate } = useMutation({
          mutationFn: updateDevice,
          onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['tableVariablesModbus'] });
            queryClient.invalidateQueries({ queryKey: ['tableSlavesModbus'] });
            queryClient.invalidateQueries({ queryKey: ['tableDevicesModbus'] });
            setValidationErrors({});
            toast.success(data, {
              closeButton: false,
              className: 'bg-right-green text-white'
            })
          },
          onError: (error: any) => {
            queryClient.invalidateQueries({ queryKey: ['tableDevicesModbus'] });
            toast.error(error?.message ?? t('devicesTable.unexpectedError'), { closeButton: false, className: 'bg-error text-white' });
          },
        });
      
        const { mutate: mutateDelete } = useMutation({
          mutationFn: deleteDevice,
          onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['tableVariablesModbus'] });
            queryClient.invalidateQueries({ queryKey: ['tableSlavesModbus'] });
            queryClient.invalidateQueries({ queryKey: ['tableDevicesModbus'] });
            toast.success(data, {
              closeButton: false,
              className: 'bg-right-green text-white'
            })
          },
          onError: (error: any) => {
            toast.error(error?.message ?? t('devicesTable.unexpectedError'), { closeButton: false, className: 'bg-error text-white' });
          },
        });
      
        const { mutate: mutateCreate } = useMutation({
          mutationFn: createDevice,
          onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['tableVariablesModbus'] });
            queryClient.invalidateQueries({ queryKey: ['tableSlavesModbus'] });
            queryClient.invalidateQueries({ queryKey: ['tableDevicesModbus'] });
            setValidationErrors({});
            toast.success(data, {
              closeButton: false,
              className: 'bg-right-green text-white'
            })
          },
          onError: (error: any) => {
            toast.error(error?.message ?? t('devicesTable.unexpectedError'), { closeButton: false, className: 'bg-error text-white' });
          },
        });

        const handleSaveRow: MRT_TableOptions<ModbusDeviceTable>['onEditingRowSave'] = async ({
            values,
            table,
            row
          }) => {
            const newErrors = validateDevice(values);
            if (Object.values(newErrors).some(Boolean)) {
              setValidationErrors(newErrors);
              return;
            }
            setValidationErrors({});
            await mutateUpdate({ formData: values, deviceId: row.original.id });
            table.setEditingRow(null);
          };


          const handleCreateRow: MRT_TableOptions<ModbusDeviceTable>['onCreatingRowSave'] = async ({
              values,
              exitCreatingMode,
            }) => {
              const newErrors = validateDevice(values);
              if (Object.values(newErrors).some(Boolean)) {
                setValidationErrors(newErrors);
                return;
              }
              setValidationErrors({});
              mutateCreate({ formData: values });
              exitCreatingMode();
            };

          const openDeleteConfirmModal = (row: MRT_Row<ModbusDeviceTable>) =>
              modals.openConfirmModal({
              title: t('devicesTable.confirmDelete'),
              children: <Text>{t('devicesTable.confirmDeleteMsg', { name: row.original.name })}</Text>,
              labels: { confirm: t('devicesTable.delete'), cancel: t('devicesTable.cancel') },
                confirmProps: {
                  style: { backgroundColor: '#FB6767', color: 'white' },
                },
                cancelProps: {
                  style: { backgroundColor: '#D4D4D4', color: 'white' },
                },
                onConfirm: () => mutateDelete({ deviceId: row.original.id }),
              });


    const table = useMantineReactTable({
        columns,
        data: formattedDevices,
        enableColumnFilterModes: true,
        enableColumnResizing: true,
        enableStickyHeader: true,
        mantineTableHeadCellProps: ({ column }) => ({
      style: {
        color: '#033F36',
        ...(column.id === 'mrt-row-actions' ? { minWidth: 120,whiteSpace: 'nowrap' } : {}),
      },
    }),
    mantineTableBodyCellProps: ({ column }) => ({
      style: {
        color: '#033F36',
        ...(column.id === 'mrt-row-actions' ? { minWidth: 120,whiteSpace: 'nowrap' } : {}),
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
          <Flex justify="space-between" align="center" >
            <Button onClick={() => table.setCreatingRow(true)}>
              {t('devicesTable.createNew')}
            </Button>
            <Tooltip label={t('devicesTable.refresh')}>
              <ActionIcon onClick={() => refetch()}>
                <IconRefresh />
              </ActionIcon>
            </Tooltip>
          </Flex>
        ),
        renderRowActions: ({ row, table }) => {
    
          return (
            <Flex gap="md" style={{ overflowX: 'auto', whiteSpace: 'nowrap' }} >
              <Tooltip label= {t('devicesTable.edit')}>
                <ActionIcon
                  variant="light"
                  color="gray"
                  onClick={() =>  table.setEditingRow(row)}
                  className={`text-button-edit bg-gap hover:text-white hover:bg-button-edit disabled:text-button-cancel-card`}
                >
                  <IconEdit />
                </ActionIcon>
              </Tooltip>
    
              <Tooltip label= {t('devicesTable.delete')}>
                <ActionIcon
                  color="red"
                  onClick={() => openDeleteConfirmModal(row)}
                  className={`text-error bg-gap hover:text-white hover:bg-error disabled:text-button-cancel-card`}
                >
                  <IconTrash />
                </ActionIcon>
              </Tooltip>
            </Flex>
          );
        },
        //mantineToolbarAlertBannerProps: isError ? { color: 'red', children: 'Error cargando dispositivos' } : undefined,
        onColumnFilterFnsChange: setColumnFilterFns,
        onColumnFiltersChange: setColumnFilters,
        onGlobalFilterChange: setGlobalFilter,
        onSortingChange: setSorting,
        onPaginationChange: setPagination,
        rowCount: dataTableDevice?.totalRowCount ?? 0,
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
            toast.error(error.message || 'Error loading devices', {
              closeButton: false,
              className: 'bg-error text-white',
            });
          }
        }, [isError, error]);


    return <MantineReactTable table={table} />
  }