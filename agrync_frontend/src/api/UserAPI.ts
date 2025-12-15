import { isAxiosError } from "axios";
import api from "../lib/axios";
import { ChangeEmailForm, ChangePasswordForm, onlyNamesDevicesSchema, SendDeviceNames, User, UserNameForm, UsersTableResponse, usersTableResponseSchema, UserTable } from "../types";
import { MRT_ColumnFilterFnsState, MRT_ColumnFiltersState, MRT_PaginationState, MRT_SortingState } from "mantine-react-table";


export async function changeFullName({ formData, userId }: { formData: UserNameForm, userId: User['id'] }) {
    try {
        const response = await api.patch(`/users/${userId}/name`, formData)
        return response.data.message
    } catch (error) {
        if (isAxiosError(error) && error.response) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
                const messages = detail.map((e) => e.message || e.msg || "Error").join(" | ");
                throw new Error(messages);
            } else if (typeof detail === "string") {
                throw new Error(detail);
            }
        }
        throw error;
    }
}



export async function changeEmail({ formData, userId }: { formData: ChangeEmailForm, userId: User['id'] }) {
    try {
        const response = await api.patch(`/users/${userId}/email`, formData)
        return response.data.message
    } catch (error) {
        if (isAxiosError(error) && error.response) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
                const messages = detail.map((e) => e.message || e.msg || "Error").join(" | ");
                throw new Error(messages);
            } else if (typeof detail === "string") {
                throw new Error(detail);
            }
        }
        throw error;
    }
}


export async function changePassword({ formData, userId }: { formData: ChangePasswordForm, userId: User['id'] }) {
    try {
        const response = await api.patch(`/users/${userId}/password`, formData)
        return response.data.message
    } catch (error) {
        if (isAxiosError(error) && error.response) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
                const messages = detail.map((e) => e.message || e.msg || "Error").join(" | ");
                throw new Error(messages);
            } else if (typeof detail === "string") {
                throw new Error(detail);
            }
        }
        throw error;
    }
}









interface Params {
    columnFilterFns: MRT_ColumnFilterFnsState;
    columnFilters: MRT_ColumnFiltersState;
    globalFilter: string;
    sorting: MRT_SortingState;
    pagination: MRT_PaginationState;
}

export async function getUsers(payload: Params): Promise<UsersTableResponse> {
    try {
        const { data } = await api.post<UsersTableResponse>('/users/list', payload);
        const response = usersTableResponseSchema.safeParse(data);
        if (response.success) {
            return response.data;
        } else {
            throw new Error('Respuesta inválida');
        }
    } catch (error) {
        if (isAxiosError(error) && error.response) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
                const messages = detail.map((e) => e.message || e.msg || "Error").join(" | ");
                throw new Error(messages);
            } else if (typeof detail === "string") {
                throw new Error(detail);
            }
        }
        throw error;
    }
}






export async function updateUser({ formData, userId }: { formData: UserTable, userId: User['id'] }) {
    try {
        const response = await api.put(`/users/${userId}`, formData)
        return response.data.message
    } catch (error) {
        if (isAxiosError(error) && error.response) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
                const messages = detail.map((e) => e.message || e.msg || "Error").join(" | ");
                throw new Error(messages);
            } else if (typeof detail === "string") {
                throw new Error(detail);
            }
        }
        throw error;
    }
}

export async function createUser({ formData }: { formData: UserTable }) {
    try {
        const response = await api.post(`/auth/register`, formData)
        return response.data.message
    } catch (error) {
        if (isAxiosError(error) && error.response) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
                const messages = detail.map((e) => e.message || e.msg || "Error").join(" | ");
                throw new Error(messages);
            } else if (typeof detail === "string") {
                throw new Error(detail);
            }
        }
        throw error;
    }
}


export async function deleteUser({ userId }: { userId: User['id'] }) {
    try {
        const response = await api.delete(`/users/${userId}`)
        return response.data.message
    } catch (error) {
        if (isAxiosError(error) && error.response) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
                const messages = detail.map((e) => e.message || e.msg || "Error").join(" | ");
                throw new Error(messages);
            } else if (typeof detail === "string") {
                throw new Error(detail);
            }
        }
        throw error;
    }
}
























export async function getUserDevices({ userId }: { userId: User['id'] }) {
    try {
        const { data } = await api.get(`/users/${userId}/devices`)
        const response = onlyNamesDevicesSchema.safeParse(data)
        if (response.success) {
            return response.data ?? []
        }

        return [];
    } catch (error) {
        if (isAxiosError(error) && error.response) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
                const messages = detail.map((e) => e.message || e.msg || "Error").join(" | ");
                throw new Error(messages);
            } else if (typeof detail === "string") {
                throw new Error(detail);
            }
        }
        throw error;
    }
}




export async function getAvailableDevices({ userId }: { userId: User['id'] }) {
    try {
        const { data } = await api.get(`/users/${userId}/devices/available`)
        const response = onlyNamesDevicesSchema.safeParse(data)
        if (response.success) {
            return response.data ?? []
        }

        return [];
    } catch (error) {
        if (isAxiosError(error) && error.response) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
                const messages = detail.map((e) => e.message || e.msg || "Error").join(" | ");
                throw new Error(messages);
            } else if (typeof detail === "string") {
                throw new Error(detail);
            }
        }
        throw error;
    }
}

export async function updateUserDevices({ formData, userId }: { formData: SendDeviceNames, userId: User['id'] }) {
    try {
        const response = await api.patch(`/users/${userId}/devices`, formData)
        return response.data.message
    } catch (error) {
        if (isAxiosError(error) && error.response) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
                const messages = detail.map((e) => e.message || e.msg || "Error").join(" | ");
                throw new Error(messages);
            } else if (typeof detail === "string") {
                throw new Error(detail);
            }
        }
        throw error;
    }
}