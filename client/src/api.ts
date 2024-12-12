import axios from "axios";

// Use injected environment variable if it exists otherwise development default
// Stupid hacky fix but the alternatives are unnecessarily complex
//let baseURL = import.meta.env.VITE_BACKEND_SKINSCAN || "http://localhost:666";
let baseURL = "http://164.92.176.222:8000"

export const API = axios.create({
    baseURL: baseURL,
    withCredentials: true,
});
