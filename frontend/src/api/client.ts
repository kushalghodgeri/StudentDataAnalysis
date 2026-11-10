import axios, { AxiosError } from "axios";
import { ApiError } from "@/types/api";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    let message = "An unexpected error occurred. Please try again.";

    if (error.response?.data?.error?.message) {
      message = error.response.data.error.message;
    } else if (error.message) {
      message = error.message;
    }

    // Attach user-friendly extracted message
    const customError = new Error(message) as Error & {
      code?: string;
      status?: number;
      details?: unknown;
    };
    customError.code = error.response?.data?.error?.code || "UNKNOWN_ERROR";
    customError.status = error.response?.status;
    customError.details = error.response?.data?.error?.details;

    return Promise.reject(customError);
  }
);
