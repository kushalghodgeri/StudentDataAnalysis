import { apiClient } from "./client";
import { ImportLog, ImportResponse } from "@/types/import";

export async function uploadDataset(
  file: File,
  onProgress?: (percent: number) => void
): Promise<ImportResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post<ImportResponse>("/imports", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const percent = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percent);
      }
    },
  });
  return response.data;
}

export async function fetchImportLogs(limit: number = 50): Promise<ImportLog[]> {
  const response = await apiClient.get<ImportLog[]>("/imports", {
    params: { limit },
  });
  return response.data;
}
