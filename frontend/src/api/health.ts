import { apiClient } from "./client";

export interface HealthResponse {
  status: string;
  db_connected: boolean;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>("/health");
  return response.data;
}
