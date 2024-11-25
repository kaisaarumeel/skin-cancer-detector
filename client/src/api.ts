import axios from "axios";

// Change this to use env variable later
export const API= axios.create({baseURL: "http://localhost:8000",
    withCredentials: true,

});