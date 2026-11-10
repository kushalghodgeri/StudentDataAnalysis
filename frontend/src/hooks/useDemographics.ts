import { useQuery } from "@tanstack/react-query";
import { fetchDemographics } from "@/api/analytics";
import { DemographicsAnalytics } from "@/types/analytics";

export function useDemographics() {
  return useQuery<DemographicsAnalytics>({
    queryKey: ["analytics", "demographics"],
    queryFn: fetchDemographics,
    staleTime: 60 * 1000,
  });
}
