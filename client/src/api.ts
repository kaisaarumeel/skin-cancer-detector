import axios from "axios";

let baseURL = import.meta.env.VITE_BACKEND_SKINSCAN || "http://localhost:8000";

export const API = axios.create({
    baseURL: baseURL,
    withCredentials: true,
});
