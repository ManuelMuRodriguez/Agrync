import { isAxiosError } from "axios";
import api from "../lib/axios";
import { MRT_ColumnFilterFnsState, MRT_ColumnFiltersState, MRT_PaginationState, MRT_SortingState } from "mantine-react-table";
import { ModbusDeviceTable, ModbusDeviceTableResponse, modbusDeviceTableResponseSchema, ModbusSlaveTable, ModbusSlaveTableResponse, modbusSlaveTableResponseSchema, ModbusVariableTable, ModbusVariableTableResponse, modbusVariableTableResponseSchema } from "../types";


interface Params {
  columnFilterFns: MRT_ColumnFilterFnsState;
  columnFilters: MRT_ColumnFiltersState;
  globalFilter: string;
  sorting: MRT_SortingState;
  pagination: MRT_PaginationState;
}

export async function getDevices(payload: Params): Promise<ModbusDeviceTableResponse> {
  try {
    const { data } = await api.post<ModbusDeviceTableResponse>('/modbus/devices/list', payload);
    const response = modbusDeviceTableResponseSchema.safeParse(data);
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

export async function createDevice({ formData }: { formData: ModbusDeviceTable }) {
  try {
    const response = await api.post(`/modbus/devices`, formData)
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

export async function deleteDevice({ deviceId }: { deviceId: ModbusDeviceTable['id'] }) {
  try {
    const response = await api.delete(`/modbus/devices/${deviceId}`)
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


export async function updateDevice({ formData, deviceId }: { formData: ModbusDeviceTable, deviceId: ModbusDeviceTable['id'] }) {
  try {
    const response = await api.put(`/modbus/devices/${deviceId}`, formData)
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






export async function getSlaves(payload: Params): Promise<ModbusSlaveTableResponse> {
  try {

    const { data } = await api.post<ModbusSlaveTableResponse>('/modbus/slaves/list', payload);
    const response = modbusSlaveTableResponseSchema.safeParse(data);
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


export async function createSlave({ deviceId, formData }: { deviceId: ModbusDeviceTable['id'], formData: ModbusSlaveTable }) {
  try {
    const response = await api.post(`/modbus/devices/${deviceId}/slaves`, formData)
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

export async function deleteSlave({ deviceId, slaveId }: { deviceId: ModbusDeviceTable['id'], slaveId: ModbusSlaveTable['id'] }) {
  try {
    const response = await api.delete(`/modbus/devices/${deviceId}/slaves/${slaveId}`)
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


export async function updateSlave({ formData, deviceId, slaveId }: { formData: ModbusSlaveTable, deviceId: ModbusDeviceTable['id'], slaveId: ModbusSlaveTable['id'] }) {
  try {
    const response = await api.put(`/modbus/devices/${deviceId}/slaves/${slaveId}`, formData)
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











export async function getVariables(payload: Params): Promise<ModbusVariableTableResponse> {
  try {
    const { data } = await api.post<ModbusVariableTableResponse>('/modbus/variables/list', payload);
    const response = modbusVariableTableResponseSchema.safeParse(data);
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




export async function createVariable({ deviceId, slaveId, formData }: { deviceId: ModbusDeviceTable['id'], slaveId: ModbusSlaveTable['id'], formData: ModbusVariableTable }) {
  try {
    const response = await api.post(`/modbus/devices/${deviceId}/slaves/${slaveId}/variables`, formData)
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

export async function deleteVariable({ deviceId, slaveId, variableId }: { deviceId: ModbusDeviceTable['id'], slaveId: ModbusSlaveTable['id'], variableId: ModbusVariableTable['id'] }) {
  try {
    const response = await api.delete(`/modbus/devices/${deviceId}/slaves/${slaveId}/variables/${variableId}`)
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


export async function updateVariable({ formData, deviceId, slaveId, variableId }: { formData: ModbusVariableTable, deviceId: ModbusDeviceTable['id'], slaveId: ModbusSlaveTable['id'], variableId: ModbusVariableTable['id'] }) {
  try {
    console.log('updateVariable llamada con:', { formData, deviceId, slaveId, variableId });
    const response = await api.put(`/modbus/devices/${deviceId}/slaves/${slaveId}/variables/${variableId}`, formData)
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