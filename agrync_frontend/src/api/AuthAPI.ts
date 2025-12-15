import api from "../lib/axios";
import { CreatePasswordForm, userInfoSchema, UserLoginForm } from "../types";
import { isAxiosError } from "axios";


export async function validateUser(formData: CreatePasswordForm) {
    try {
        const response = await api.post("/auth/validate", formData)
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


export async function login(formData: UserLoginForm) {
    try {
        const body = new URLSearchParams();
        body.append('username', formData.username);
        body.append('password', formData.password);

        const { data } = await api.post("/auth/login", body, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            withCredentials: true

        });

        localStorage.setItem('ACCESS_TOKEN_AGRYNC', data.access_token)
        return data
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

export async function logout() {
    try {
        const response = await api.post("/auth/logout", {}, { withCredentials: true })
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



export async function getUserInfo() {
    try {
        const { data } = await api('/auth/info')
        const response = userInfoSchema.safeParse(data)
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