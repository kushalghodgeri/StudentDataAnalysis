import { useQuery } from "@tanstack/react-query";
import { fetchAttendance } from "@/api/analytics";
import { AttendanceAnalytics } from "@/types/analytics";

export function useAttendance(filters?: { semester: number | null; department: string | null }) {
  return useQuery<AttendanceAnalytics>({
    queryKey: ["analytics", "attendance", filters?.semester, filters?.department],
    queryFn: () =>
      fetchAttendance({
        semester: filters?.semester,
        department: filters?.department,
      }),
    staleTime: 60 * 1000,
  });
}
