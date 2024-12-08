import axios from "axios";

// Use injected environment variable if it exists otherwise dev default
export const API = axios.create({
    baseURL: process.env.CLIENT_API_BASE_URL || "http://localhost:8000",
    withCredentials: true,
});