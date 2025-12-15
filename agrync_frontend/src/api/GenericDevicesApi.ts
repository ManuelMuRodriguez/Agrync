import { isAxiosError } from "axios"
import api from "../lib/axios"
import { FormDashboard, FormGraficas, GenericDevicesNames, genericDevicesNamesSchema, genericDevicesSchema, historicalDataSchema, lastDataSchema, User } from "../types"

export async function getUserGenericDevices(userId: User['id']) {
  try {
    const { data } = await api(`/generic/${userId}`)
    const response = genericDevicesNamesSchema.safeParse(data)
    if (response.success) {
      return response.data
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




const transformToGenericDevicesNames = (selected: string[]): GenericDevicesNames => {
  const grouped: Record<string, string[]> = {};

  selected.forEach((item) => {
    const [device, variable] = item.split("|");
    if (!grouped[device]) grouped[device] = [];
    grouped[device].push(variable);
  });

  return Object.entries(grouped).map(([name, variables_names]) => ({
    name,
    variables_names,
  }));
};



const toUtcISOString = (date: Date | null) => {

  if (!date) throw new Error("Fecha no válida");

  return new Date(date).toISOString();

}

export async function getHistoricalData({ formData, userId }: { formData: FormGraficas, userId: User['id'] }) {
  try {
    const body: GenericDevicesNames = transformToGenericDevicesNames(formData.variables_names);

    const { data } = await api.post(`/generic/historical-values/${userId}`,
      body,
      {
        params: {
          start_date: toUtcISOString(formData.start_date),
          end_date: toUtcISOString(formData.end_date),
          aggregation: formData.aggregation,
        },
      }
    );

    const response = historicalDataSchema.safeParse(data)
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







export async function getDashboardBody({ formData, userId }: { formData: FormDashboard, userId: User['id'] }) {
  try {


    const body: GenericDevicesNames = transformToGenericDevicesNames(formData.variables_names);

    const { data } = await api.post(`/generic/filter-variables/${userId}`, body);

    const response = genericDevicesSchema.safeParse(data)
    if (response.success) {
      return response.data
    } else {
      throw new Error("Error de validación")
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





export async function getLastData({ formData, userId }: { formData: FormDashboard, userId: User['id'] }) {

  try {

    const body: GenericDevicesNames = transformToGenericDevicesNames(formData.variables_names);

    const { data } = await api.post(`/generic/last-values/${userId}`, body
    );

    const response = lastDataSchema.safeParse(data)
    if (response.success) {
      return response.data
    } else {
      throw new Error("Error de validación")
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


