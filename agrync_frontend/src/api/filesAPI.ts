import { isAxiosError } from "axios"
import api from "../lib/axios"


export async function getTemplate() {
    try {
        const response = await api.get("/modbus/download-template", { responseType: "blob" });
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


export async function uploadFileModbus(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await api.post("/modbus/upload", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });

        return response.data;
    } catch (error) {
        if (isAxiosError(error) && error.response) {
            const detail = error.response.data.detail;
            if (Array.isArray(detail)) {
                const messages = detail.map((e) => e.message || e.msg || "Error").join(" | ");
                throw new Error(messages);
            } else if (typeof detail === "string") {
                throw new Error(detail);
            }
            throw new Error("Error al subir el archivo");
        }
        throw error;
    }
}