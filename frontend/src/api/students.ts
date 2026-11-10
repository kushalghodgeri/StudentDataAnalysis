import { apiClient } from "./client";
import { PaginatedResponse } from "@/types/api";
import { Student, StudentDetail, StudentQueryParams } from "@/types/student";
import { MetaFilters } from "@/types/analytics";

export async function fetchStudents(
  params: StudentQueryParams
): Promise<PaginatedResponse<Student>> {
  const response = await apiClient.get<PaginatedResponse<Student>>("/students", {
    params,
  });
  return response.data;
}

export async function fetchStudentDetail(id: number): Promise<StudentDetail> {
  const response = await apiClient.get<StudentDetail>(`/students/${id}`);
  return response.data;
}

export async function fetchMetaFilters(): Promise<MetaFilters> {
  const response = await apiClient.get<MetaFilters>("/meta/filters");
  return response.data;
}
