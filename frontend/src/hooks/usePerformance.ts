import { useQuery } from "@tanstack/react-query";
import { fetchPerformance } from "@/api/analytics";
import { PerformanceAnalytics } from "@/types/analytics";

export function usePerformance(filters?: { semester: number | null; department: string | null }) {
  return useQuery<PerformanceAnalytics>({
    queryKey: ["analytics", "performance", filters?.semester, filters?.department],
    queryFn: () =>
      fetchPerformance({
        semester: filters?.semester,
        department: filters?.department,
      }),
    staleTime: 60 * 1000,
  });
}
