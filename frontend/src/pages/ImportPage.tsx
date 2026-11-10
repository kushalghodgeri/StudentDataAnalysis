import React, { useState } from "react";
import {
  UploadCloud,
  History,
  CheckCircle2,
} from "lucide-react";
import { PageHeader } from "../components/layout/PageHeader";
import { FileDropzone } from "../components/ui/FileDropzone";
import { StatCard } from "../components/ui/StatCard";
import { DataTable, ColumnDef } from "../components/ui/DataTable";
import { Badge } from "../components/ui/Badge";
import { ErrorState } from "../components/ui/ErrorState";
import { useImports } from "../hooks/useImports";
import { useToast } from "../context/ToastContext";
import { formatDateTime, formatInteger } from "../lib/formatters";
import { ImportLog, CleaningSummary, ImportResponse } from "../types/import";

export const ImportPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [lastSummary, setLastSummary] = useState<CleaningSummary | null>(null);

  const { imports, isLoading, isError, refetch, uploadMutation } = useImports();
  const { addToast } = useToast();

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setLastSummary(null);
  };

  const handleUpload = () => {
    if (!selectedFile) return;

    setUploadProgress(15);
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 85) {
          clearInterval(interval);
          return 85;
        }
        return prev + 25;
      });
    }, 150);

    uploadMutation.mutate(selectedFile, {
      onSuccess: (data: ImportResponse) => {
        clearInterval(interval);
        setUploadProgress(100);
        setLastSummary(data.cleaning_summary);
        setSelectedFile(null);
        addToast({
          type: "success",
          title: "Import Successful",
          message: `Cleaned and imported ${data.cleaning_summary.rows_out} records.`,
        });
        setTimeout(() => setUploadProgress(0), 1000);
      },
      onError: (err: any) => {
        clearInterval(interval);
        setUploadProgress(0);
        addToast({
          type: "error",
          title: "Import Failed",
          message: err?.response?.data?.detail || "Failed to process the uploaded dataset.",
        });
      },
    });
  };

  const historyColumns: ColumnDef<ImportLog>[] = [
    {
      key: "import_id",
      header: "ID",
      className: "w-16 font-mono text-xs text-slate-500",
      render: (r) => <span>#{r.import_id}</span>,
    },
    {
      key: "filename",
      header: "File Name",
      render: (r) => (
        <span className="font-medium text-slate-900 dark:text-slate-100">
          {r.filename || r.file_name || `Dataset #${r.import_id}`}
        </span>
      ),
    },
    {
      key: "created_at",
      header: "Timestamp",
      className: "w-44 text-xs text-slate-500",
      render: (r) => <span>{formatDateTime(r.created_at || r.imported_at)}</span>,
    },
    {
      key: "status",
      header: "Status",
      className: "w-28",
      render: (r) => (
        <Badge
          variant={r.status.toLowerCase() === "success" ? "success" : "warning"}
          size="sm"
        >
          {r.status}
        </Badge>
      ),
    },
    {
      key: "cleaning_summary",
      header: "Pipeline Stats",
      render: (r) => {
        const s = r.cleaning_summary || {
          rows_in: r.total_rows || 0,
          rows_out: r.valid_rows || 0,
          duplicates_removed: r.duplicates_removed || 0,
          nulls_filled: r.nulls_filled || 0,
          outliers_flagged: r.outliers_flagged || 0,
        };
        return (
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-700 font-medium">
              In: {formatInteger(s.rows_in)}
            </span>
            <span className="px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-medium">
              Out: {formatInteger(s.rows_out)}
            </span>
            {s.duplicates_removed > 0 && (
              <span className="px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300">
                {s.duplicates_removed} dups
              </span>
            )}
            {s.outliers_flagged > 0 && (
              <span className="px-2 py-0.5 rounded bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300">
                {s.outliers_flagged} outliers
              </span>
            )}
          </div>
        );
      },
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Import Student Data"
        subtitle="Ingest CSV or XLSX spreadsheets directly into the automated cleaning and validation pipeline."
      />

      {/* File Dropzone Section */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-700/80 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-1">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
            Select or drag your CSV/Excel file
          </span>
          <a
            href="/sample_dirty_student_data.csv"
            download="sample_dirty_student_data.csv"
            className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
          >
            Download test dataset (dirty sample)
          </a>
        </div>

        <FileDropzone
          onFileSelect={handleFileSelect}
          isUploading={uploadMutation.isPending}
          uploadProgress={uploadProgress}
        />

        <div className="flex justify-end gap-3">
          {selectedFile && !uploadMutation.isPending && (
            <button
              onClick={() => setSelectedFile(null)}
              type="button"
              className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-colors"
            >
              Cancel
            </button>
          )}

          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploadMutation.isPending}
            type="button"
            className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:pointer-events-none rounded-xl shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <UploadCloud className="w-4 h-4" />
            {uploadMutation.isPending ? "Executing ETL Pipeline..." : "Process & Import Data"}
          </button>
        </div>
      </div>

      {/* Cleaning Summary Panel (Shown immediately after upload) */}
      {lastSummary && (
        <div className="p-6 bg-gradient-to-r from-emerald-500/10 via-indigo-500/10 to-teal-500/5 rounded-2xl border border-emerald-300 dark:border-emerald-800 space-y-4 animate-in fade-in duration-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-600 text-white rounded-xl shadow-sm">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                Data Cleaning & Validation Summary
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Automated sanitization results from the DataCleaner pipeline
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            <StatCard
              title="Rows Ingested"
              value={formatInteger(lastSummary.rows_in)}
              subtitle="Raw input records"
              variant="indigo"
            />
            <StatCard
              title="Rows Processed"
              value={formatInteger(lastSummary.rows_out)}
              subtitle="Passed to database"
              variant="emerald"
            />
            <StatCard
              title="Duplicates Removed"
              value={formatInteger(lastSummary.duplicates_removed)}
              subtitle="By email / ID"
              variant="amber"
            />
            <StatCard
              title="Nulls Imputed"
              value={formatInteger(lastSummary.nulls_filled)}
              subtitle="Course median value"
              variant="sky"
            />
            <StatCard
              title="Outliers Flagged"
              value={formatInteger(lastSummary.outliers_flagged)}
              subtitle="IQR 1.5x bounds"
              variant="rose"
            />
          </div>
        </div>
      )}

      {/* Import History Table */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-indigo-500" />
          <h3 className="text-base font-semibold text-slate-800 dark:text-slate-100">
            Import Audit History
          </h3>
        </div>

        {isError && (
          <ErrorState
            title="Failed to load import history"
            message="Could not retrieve past import audit logs."
            onRetry={refetch}
          />
        )}

        <DataTable
          columns={historyColumns}
          data={imports || []}
          keyExtractor={(r) => r.import_id}
          isLoading={isLoading}
          emptyTitle="No import records"
          emptyDescription="You have not uploaded any datasets yet. Use the dropzone above to begin."
        />
      </div>
    </div>
  );
};
