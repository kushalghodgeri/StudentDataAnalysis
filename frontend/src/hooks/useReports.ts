import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchReports, generateReport } from "@/api/reports";
import { ReportLog, ReportRequest, ReportResponse } from "@/types/report";

export function useGenerateReport() {
  const queryClient = useQueryClient();

  return useMutation<ReportResponse, Error, ReportRequest>({
    mutationFn: (payload) => generateReport(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports", "list"] });
    },
  });
}

export function useReports() {
  const query = useQuery<ReportLog[]>({
    queryKey: ["reports", "list"],
    queryFn: fetchReports,
    staleTime: 30 * 1000,
  });

  const generateMutation = useGenerateReport();

  return {
    ...query,
    reports: query.data,
    generateMutation,
  };
}
