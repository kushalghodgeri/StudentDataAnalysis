import { useQuery } from "@tanstack/react-query";
import { fetchMetaFilters } from "@/api/students";
import { MetaFilters } from "@/types/analytics";

export function useMetaFilters() {
  return useQuery<MetaFilters>({
    queryKey: ["meta", "filters"],
    queryFn: fetchMetaFilters,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}
