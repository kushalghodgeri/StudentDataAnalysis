import { useQuery } from "@tanstack/react-query";
import { fetchStudentDetail } from "@/api/students";
import { StudentDetail } from "@/types/student";

export function useStudentDetail(id: number) {
  return useQuery<StudentDetail>({
    queryKey: ["students", "detail", id],
    queryFn: () => fetchStudentDetail(id),
    enabled: !isNaN(id) && id > 0,
    staleTime: 60 * 1000,
  });
}
