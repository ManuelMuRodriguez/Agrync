import axios from "axios"


const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    headers: {
        'Content-Type': 'application/json',
    }
    
})

api.interceptors.request.use(config => {
    const token = localStorage.getItem("ACCESS_TOKEN_AGRYNC")
    if(token){
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})


api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
        if(error.response.data.detail == "Access Token inválido" || error.response.data.detail == "Not authenticated" || error.response.data.detail == "Access Token no encontrado" || error.response.data.detail == "Usuario no encontrado para ese Access Token") {
            originalRequest._retry = true;
            try {
                const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/refresh`,{}, { withCredentials: true });
                const newAccessToken = response.data.access_token;
                if (newAccessToken) {
                    localStorage.setItem('ACCESS_TOKEN_AGRYNC', newAccessToken);
                    originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                    return axios(originalRequest); 
                } else {
                    throw new Error("No se recibió el nuevo Access Token");
                }
            } catch (refreshError) {
                localStorage.removeItem('ACCESS_TOKEN_AGRYNC');
                //window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        } else {
            return Promise.reject(error);
        }
    }
    return Promise.reject(error);
  }
);



export default api