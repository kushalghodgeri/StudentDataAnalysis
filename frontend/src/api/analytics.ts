import { apiClient } from "./client";
import {
  AttendanceAnalytics,
  DemographicsAnalytics,
  OverviewAnalytics,
  PerformanceAnalytics,
} from "@/types/analytics";

export interface AnalyticsFilterParams {
  semester?: number | null;
  department?: string | null;
}

export async function fetchOverview(
  params?: AnalyticsFilterParams
): Promise<OverviewAnalytics> {
  const queryParams: Record<string, unknown> = {};
  if (params?.semester) queryParams.semester = params.semester;
  if (params?.department) queryParams.department = params.department;

  const response = await apiClient.get<OverviewAnalytics>("/analytics/overview", {
    params: queryParams,
  });
  return response.data;
}

export async function fetchPerformance(
  params?: AnalyticsFilterParams
): Promise<PerformanceAnalytics> {
  const queryParams: Record<string, unknown> = {};
  if (params?.semester) queryParams.semester = params.semester;
  if (params?.department) queryParams.department = params.department;

  const response = await apiClient.get<PerformanceAnalytics>(
    "/analytics/performance",
    { params: queryParams }
  );
  return response.data;
}

export async function fetchAttendance(
  params?: AnalyticsFilterParams
): Promise<AttendanceAnalytics> {
  const queryParams: Record<string, unknown> = {};
  if (params?.semester) queryParams.semester = params.semester;
  if (params?.department) queryParams.department = params.department;

  const response = await apiClient.get<AttendanceAnalytics>(
    "/analytics/attendance",
    { params: queryParams }
  );
  return response.data;
}

export async function fetchDemographics(): Promise<DemographicsAnalytics> {
  const response = await apiClient.get<DemographicsAnalytics>(
    "/analytics/demographics"
  );
  return response.data;
}
