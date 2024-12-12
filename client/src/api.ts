import axios from "axios";

// Use injected environment variable if it exists otherwise development default
// Stupid hacky fix but the alternatives are unnecessarily complex
let baseURL = "http://localhost:8000";
// Check if the Node process exists (it does during build stage)
if (typeof process !== "undefined") {
    // TypeScript demands this check :)))
    if (process.env.CLIENT_API_BASE_URL) {
        baseURL = process.env.CLIENT_API_BASE_URL;
    }
}

export const API = axios.create({
    baseURL: baseURL,
    withCredentials: true,
});