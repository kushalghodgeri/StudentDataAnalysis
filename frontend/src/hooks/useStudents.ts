import { useQuery } from "@tanstack/react-query";
import { fetchStudents } from "@/api/students";
import { PaginatedResponse } from "@/types/api";
import { Student, StudentQueryParams } from "@/types/student";

export function useStudents(params: StudentQueryParams) {
  return useQuery<PaginatedResponse<Student>>({
    queryKey: [
      "students",
      params.page,
      params.page_size,
      params.department,
      params.search,
      params.sort_by,
      params.order,
    ],
    queryFn: () => fetchStudents(params),
    staleTime: 30 * 1000,
  });
}
