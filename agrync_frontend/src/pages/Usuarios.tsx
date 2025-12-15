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
import { IconRefresh, IconEdit, IconTrash } from '@tabler/icons-react';
import { useEffect, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getUsers, updateUser, deleteUser, createUser } from '../api/UserAPI';
import { modals } from '@mantine/modals';
import { toast } from 'react-toastify';
import { roleOptions, UserTable } from '../types';
import { DateTime } from 'luxon';
import { MRT_Localization_ES } from 'mantine-react-table/locales/es';
import { useAuth } from '../hooks/useAuth';
import { IoRadio } from "react-icons/io5";
import ModificarDispositivosUsuario from '../components/ModificarDispositivosUsuario';


export default function Usuarios() {

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserTable | null>(null);

  const openDeviceModal = (row: MRT_Row<UserTable>) => {
    setSelectedUser(row.original);
    setIsModalOpen(true);
  };

  const [validationErrors, setValidationErrors] = useState<Record<string, string | undefined>>({});

  const { data: dataAuth } = useAuth()

  const validateEmail = (email: string) =>
    !!email && /[^@]+@[^@]+\.[a-zA-Z]{2,6}/.test(email);

  function validateUser(user: UserTable) {
    return {
      email: !validateEmail(user.email) ? 'Invalid email format' : undefined,
      full_name: !user.full_name ? 'Full name required' : undefined,
      role: !user.role ? 'Required role' : undefined,
    };
  }

  const columns = useMemo<MRT_ColumnDef<UserTable>[]>(() => [
    {
      accessorKey: 'email',
      header: 'Email',
      mantineEditTextInputProps: () => ({
        type: 'email',
        required: true,
        error: validationErrors?.email,
        onFocus: () => setValidationErrors((prev) => ({ ...prev, email: undefined })),
        classNames: {
          input: validationErrors?.email ? 'border-2' : 'border-2',

        },
      }),
    },
    {
      accessorKey: 'full_name',
      header: 'Name',
      mantineEditTextInputProps: () => ({
        required: true,
        error: validationErrors?.full_name,
        onFocus: () => setValidationErrors((prev) => ({ ...prev, full_name: undefined })),
        classNames: {
          input: validationErrors?.full_name ? 'border-2' : 'border-2',
        },
      }),
    },
    {
      accessorKey: 'role',
      header: 'Role',
      editVariant: 'select',
      mantineEditSelectProps: () => ({
        data: roleOptions,
        required: true,
        error: validationErrors?.role,
        onFocus: () => setValidationErrors((prev) => ({ ...prev, role: undefined })),
        classNames: {
          input: validationErrors?.role ? 'border-2' : 'border-2 border-gap',
        },
      }),
    },
    {
      accessorKey: 'active',
      header: 'active',
      size: 120,
      Cell: ({ cell }) => (cell.getValue<boolean>() ? 'Sí' : 'No'),
      enableEditing: false,
    },
    { accessorKey: 'createdAt', header: 'Date of creation', enableEditing: false },
    { accessorKey: 'updatedAt', header: 'Last modified', enableEditing: false },
  ], [validationErrors]);

  const [columnFilters, setColumnFilters] = useState<MRT_ColumnFiltersState>([]);
  const [columnFilterFns, setColumnFilterFns] = useState<MRT_ColumnFilterFnsState>(
    Object.fromEntries(columns.map((col) => [col.accessorKey!, 'contains']))
  );
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState<MRT_SortingState>([]);
  const [pagination, setPagination] = useState<MRT_PaginationState>({ pageIndex: 0, pageSize: 10 });

  const { data: dataTableUser, error, isError, isFetching, isLoading, refetch } = useQuery({
    queryKey: ['tableUsers', { columnFilters, columnFilterFns, globalFilter, pagination, sorting }],
    queryFn: () =>
      getUsers({
        columnFilters,
        columnFilterFns,
        globalFilter,
        sorting,
        pagination,
      }),
    retry: false,
    refetchOnWindowFocus: false,
  });

  const formattedUsers = useMemo(() => {
    return dataTableUser?.data.map((user) => {
      const createdAt = DateTime.fromISO(user.createdAt, { zone: 'UTC' });
      const updatedAt = DateTime.fromISO(user.updatedAt, { zone: 'UTC' });

      return {
        ...user,
        createdAt: createdAt.isValid
          ? createdAt.setZone('Europe/Madrid').toFormat('dd/MM/yyyy HH:mm:ss')
          : 'Invalid date',
        updatedAt: updatedAt.isValid
          ? updatedAt.setZone('Europe/Madrid').toFormat('dd/MM/yyyy HH:mm:ss')
          : 'Invalid date',
      };
    }) ?? [];
  }, [dataTableUser]);

  const queryClient = useQueryClient();

  const { mutateAsync: mutateUpdate } = useMutation({
    mutationFn: updateUser,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tableUsers'] });
      setValidationErrors({});
      toast.success(data, {
        closeButton: false,
        className: 'bg-right-green text-white'
      })
    },
    onError: (error: any) => {
      queryClient.invalidateQueries({ queryKey: ['tableUsers'] });
      toast.error(error?.message ?? 'Unexpected error', { closeButton: false, className: 'bg-error text-white' });
    },
  });

  const { mutate: mutateDelete } = useMutation({
    mutationFn: deleteUser,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tableUsers'] });
      toast.success(data, {
        closeButton: false,
        className: 'bg-right-green text-white'
      })
    },
    onError: (error: any) => {
      toast.error(error?.message ?? 'Unexpected error', { closeButton: false, className: 'bg-error text-white' });
    },
  });

  const { mutate: mutateCreate } = useMutation({
    mutationFn: createUser,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tableUsers'] });
      setValidationErrors({});
      toast.success(data, {
        closeButton: false,
        className: 'bg-right-green text-white'
      })
    },
    onError: (error: any) => {
      toast.error(error?.message ?? 'Error inesperado', { closeButton: false, className: 'bg-error text-white' });
    },
  });

  const handleSaveRow: MRT_TableOptions<UserTable>['onEditingRowSave'] = async ({
    values,
    table,
    row
  }) => {
    const newErrors = validateUser(values);
    if (Object.values(newErrors).some(Boolean)) {
      setValidationErrors(newErrors);
      return;
    }
    setValidationErrors({});
    await mutateUpdate({ formData: values, userId: row.original.id });
    table.setEditingRow(null);
  };

  const handleCreateRow: MRT_TableOptions<UserTable>['onCreatingRowSave'] = async ({
    values,
    exitCreatingMode,
  }) => {
    const newErrors = validateUser(values);
    if (Object.values(newErrors).some(Boolean)) {
      setValidationErrors(newErrors);
      return;
    }
    setValidationErrors({});
    mutateCreate({ formData: values });
    exitCreatingMode();
  };

  const openDeleteConfirmModal = (row: MRT_Row<UserTable>) =>
    modals.openConfirmModal({
      title: 'Confirm deletion',
      children: <Text>Are you sure you want to delete {row.original.full_name}?</Text>,
      labels: { confirm: 'Delete', cancel: 'Cancel' },
      confirmProps: {
        style: { backgroundColor: '#FB6767', color: 'white' },
      },
      cancelProps: {
        style: { backgroundColor: '#D4D4D4', color: 'white' },
      },
      onConfirm: () => mutateDelete({ userId: row.original.id }),
    });


  const table = useMantineReactTable({
    columns,
    data: formattedUsers,
    enableColumnFilterModes: true,
    enableColumnResizing: true,
    enableStickyHeader: true,
    mantineTableHeadCellProps: ({ column }) => ({
      style: {
        color: '#033F36',
        ...(column.id === 'mrt-row-actions' ? { minWidth: 160,whiteSpace: 'nowrap' } : {}),
      },
    }),
    mantineTableBodyCellProps: ({ column }) => ({
      style: {
        color: '#033F36',
        ...(column.id === 'mrt-row-actions' ? { minWidth: 160,whiteSpace: 'nowrap' } : {}),
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
          Create New User
        </Button>
        <Tooltip label="Refrescar">
          <ActionIcon onClick={() => refetch()}>
            <IconRefresh />
          </ActionIcon>
        </Tooltip>
      </Flex>
    ),
    renderRowActions: ({ row, table }) => {
      const isSelf = dataAuth?.id === row.original.id;
      const isAdmin = row.original.role === 'Administrador';

      const disableActions = isSelf || isAdmin;

      const disableDeviceEdit = !isSelf && isAdmin;

      return (
        <Flex gap="md" style={{ overflowX: 'auto', whiteSpace: 'nowrap' }} >
          <Tooltip label={disableActions ? 'No editable' : 'Edit'}>
            <ActionIcon
              variant="light"
              color="gray"
              onClick={() => !disableActions && table.setEditingRow(row)}
              disabled={disableActions}
              className={`text-button-edit bg-gap hover:text-white hover:bg-button-edit disabled:text-button-cancel-card`}
            >
              <IconEdit />
            </ActionIcon>
          </Tooltip>

          <Tooltip label={disableActions ? 'No eliminable' : 'Delete'}>
            <ActionIcon
              color="red"
              onClick={() => !disableActions && openDeleteConfirmModal(row)}
              disabled={disableActions}
              className={`text-error bg-gap hover:text-white hover:bg-error disabled:text-button-cancel-card`}
            >
              <IconTrash />
            </ActionIcon>
          </Tooltip>

          <Tooltip label={disableDeviceEdit ? 'No editable' : "Edit devices"}>
            <ActionIcon
              variant="light"
              onClick={() => !disableDeviceEdit && openDeviceModal(row)}
              disabled={disableDeviceEdit}
              className={`text-button bg-gap hover:text-white hover:bg-button disabled:text-button-cancel-card`}
            >
              <IoRadio size={18} />
            </ActionIcon>
          </Tooltip>
        </Flex>
      );
    },
    //mantineToolbarAlertBannerProps: isError ? { color: 'red', children: 'Error cargando usuarios' } : undefined,
    onColumnFilterFnsChange: setColumnFilterFns,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    rowCount: dataTableUser?.totalRowCount ?? 0,
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
      toast.error(error.message || 'Error loading users', {
        closeButton: false,
        className: 'bg-error text-white',
      });
    }
  }, [isError, error]);

  return (
    <>


      <MantineReactTable table={table} />


      {selectedUser && (
        <ModificarDispositivosUsuario
          isModalOpen={isModalOpen}
          setIsModalOpen={setIsModalOpen}
          userId={selectedUser.id}
        />
      )}


    </>
  )


}
