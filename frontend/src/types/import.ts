export interface CleaningSummary {
  rows_in: number;
  rows_out: number;
  duplicates_removed: number;
  nulls_filled: number;
  outliers_flagged: number;
}

export interface ImportResponse {
  import_id: number;
  cleaning_summary: CleaningSummary;
}

export interface ImportLog {
  import_id: number;
  file_name?: string;
  filename?: string;
  file_type?: string;
  total_rows?: number;
  valid_rows?: number;
  rejected_rows?: number;
  duplicates_removed?: number;
  nulls_filled?: number;
  outliers_flagged?: number;
  status: "SUCCESS" | "FAILED" | "PARTIAL" | string;
  error_summary?: string | null;
  imported_at?: string;
  created_at?: string;
  cleaning_summary?: CleaningSummary;
}

export type ImportRecord = ImportLog;
