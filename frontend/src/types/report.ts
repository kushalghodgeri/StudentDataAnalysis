export interface ReportRequest {
  semester?: number | null;
  department?: string | null;
  formats: ("pdf" | "csv" | "xlsx")[];
}

export interface ReportFileItem {
  name: string;
  url: string;
}

export interface ReportResponse {
  report_id: string;
  semester?: number;
  files: ReportFileItem[];
  charts: ReportFileItem[];
}

export interface ReportLog {
  report_id: string;
  created_at: string;
  semester?: number | null;
  department?: string | null;
  formats: string[];
  files: ReportFileItem[];
  charts: ReportFileItem[];
}

export type ReportRecord = ReportLog;
export type ReportFile = ReportFileItem;
export type ReportChart = ReportFileItem;
