import { useQuery } from "@tanstack/react-query";
import { fetchOverview } from "@/api/analytics";
import { OverviewAnalytics } from "@/types/analytics";

export function useOverview(filters?: { semester: number | null; department: string | null }) {
  return useQuery<OverviewAnalytics>({
    queryKey: ["analytics", "overview", filters?.semester, filters?.department],
    queryFn: () =>
      fetchOverview({
        semester: filters?.semester,
        department: filters?.department,
      }),
    staleTime: 60 * 1000,
  });
}
