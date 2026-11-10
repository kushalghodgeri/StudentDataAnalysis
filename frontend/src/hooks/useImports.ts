import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchImportLogs, uploadDataset } from "@/api/imports";
import { ImportLog, ImportResponse } from "@/types/import";

export function useImportLogs(limit: number = 50) {
  return useQuery<ImportLog[]>({
    queryKey: ["imports", "logs", limit],
    queryFn: () => fetchImportLogs(limit),
    staleTime: 30 * 1000,
  });
}

export function useUploadDataset() {
  const queryClient = useQueryClient();

  return useMutation<
    ImportResponse,
    Error,
    File
  >({
    mutationFn: (file) => uploadDataset(file),
    onSuccess: () => {
      // Invalidate relevant queries after an import
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
      queryClient.invalidateQueries({ queryKey: ["students"] });
      queryClient.invalidateQueries({ queryKey: ["imports", "logs"] });
      queryClient.invalidateQueries({ queryKey: ["meta", "filters"] });
    },
  });
}

export function useImports(limit: number = 50) {
  const query = useImportLogs(limit);
  const uploadMutation = useUploadDataset();

  return {
    ...query,
    imports: query.data,
    uploadMutation,
  };
}
