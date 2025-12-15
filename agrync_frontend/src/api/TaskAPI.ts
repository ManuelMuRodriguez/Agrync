import { isAxiosError } from "axios";
import api from "../lib/axios";
import { taskSchema } from "../types";



export async function getModbusTaskStatus(taskName: string) {
  try {
    const { data } = await api.get(`/tasks/${taskName}/state`);
    const response = taskSchema.safeParse(data);
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



export async function stopTask(taskName: string) {
  try {
    const response = await api.post(`/tasks/${taskName}/stop`)
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


export async function startTask(taskName: string) {
  try {
    const response = await api.post(`/tasks/${taskName}/start`)
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

