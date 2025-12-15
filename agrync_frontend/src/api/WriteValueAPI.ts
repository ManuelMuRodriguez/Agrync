import { isAxiosError } from "axios"
import api from "../lib/axios"
import { SendValueOPC, User } from "../types";


export async function writeValue({ formData, userId }: { formData: SendValueOPC, userId: User['id'] }) {
  try {
    const body: SendValueOPC = formData;

    const response = await api.post(`/opc/write-value/${userId}`,
      body
    );

    return response.data

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