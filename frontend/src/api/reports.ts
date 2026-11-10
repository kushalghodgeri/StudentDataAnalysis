import { apiClient } from "./client";
import { ReportLog, ReportRequest, ReportResponse } from "@/types/report";

export async function generateReport(
  payload: ReportRequest
): Promise<ReportResponse> {
  const response = await apiClient.post<ReportResponse>(
    "/reports/generate",
    payload
  );
  return response.data;
}

export async function fetchReports(): Promise<ReportLog[]> {
  const response = await apiClient.get<ReportLog[]>("/reports");
  return response.data;
}

export function getDownloadUrl(reportId: string, filename: string): string {
  const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
  return `${baseUrl}/reports/${reportId}/download/${filename}`;
}

export function getChartUrl(filename: string): string {
  const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
  return `${baseUrl}/charts/${filename}`;
}

export const buildReportDownloadUrl = getDownloadUrl;
export const buildChartUrl = getChartUrl;
