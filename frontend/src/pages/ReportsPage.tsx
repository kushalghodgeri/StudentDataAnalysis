import React, { useState } from "react";
import {
  FileText,
  Download,
  Image as ImageIcon,
  CheckCircle2,
  FileSpreadsheet,
  FileCode,
  ZoomIn,
} from "lucide-react";
import { PageHeader } from "../components/layout/PageHeader";
import { DataTable, ColumnDef } from "../components/ui/DataTable";
import { Modal } from "../components/ui/Modal";
import { ErrorState } from "../components/ui/ErrorState";
import { useReports } from "../hooks/useReports";
import { useMetaFilters } from "../hooks/useMetaFilters";
import { useToast } from "../context/ToastContext";
import { formatDateTime } from "../lib/formatters";
import { ReportLog, ReportResponse, ReportFileItem } from "../types/report";
import { buildChartUrl, buildReportDownloadUrl } from "../api/reports";

export const ReportsPage: React.FC = () => {
  const { data: meta } = useMetaFilters();
  const { reports, isLoading, isError, refetch, generateMutation } = useReports();
  const { addToast } = useToast();

  // Generator form state
  const [semester, setSemester] = useState<number>(1);
  const [department, setDepartment] = useState<string>("");
  const [selectedFormats, setSelectedFormats] = useState<("pdf" | "csv" | "xlsx")[]>([
    "pdf",
    "csv",
    "xlsx",
  ]);

  // Generated Result state
  const [latestReport, setLatestReport] = useState<ReportResponse | null>(null);

  // Lightbox Modal state
  const [activeLightboxChart, setActiveLightboxChart] = useState<ReportFileItem | null>(null);

  const toggleFormat = (fmt: "pdf" | "csv" | "xlsx") => {
    setSelectedFormats((prev) =>
      prev.includes(fmt) ? prev.filter((f) => f !== fmt) : [...prev, fmt]
    );
  };

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFormats.length === 0) {
      addToast({
        type: "warning",
        title: "Format Required",
        message: "Please select at least one export format (PDF, CSV, or XLSX).",
      });
      return;
    }

    generateMutation.mutate(
      {
        semester,
        department: department || undefined,
        formats: selectedFormats,
      },
      {
        onSuccess: (data: ReportResponse) => {
          setLatestReport(data);
          addToast({
            type: "success",
            title: "Report Generated",
            message: `Report #${data.report_id} and ${data.charts?.length || 0} charts ready.`,
          });
        },
        onError: (err: any) => {
          addToast({
            type: "error",
            title: "Generation Failed",
            message: err?.response?.data?.detail || "Could not generate report.",
          });
        },
      }
    );
  };

  const pastReportsColumns: ColumnDef<ReportLog>[] = [
    {
      key: "report_id",
      header: "ID",
      className: "w-16 font-mono text-xs text-slate-500",
      render: (r) => <span>#{r.report_id}</span>,
    },
    {
      key: "semester",
      header: "Semester",
      className: "w-28",
      render: (r) => <span className="text-xs font-mono">Semester {r.semester}</span>,
    },
    {
      key: "created_at",
      header: "Generated At",
      className: "w-44 text-xs text-slate-500",
      render: (r) => <span>{formatDateTime(r.created_at)}</span>,
    },
    {
      key: "files",
      header: "Available Formats",
      render: (r) => (
        <div className="flex flex-wrap gap-2">
          {r.files.map((f: ReportFileItem) => {
            const ext = f.name.split(".").pop()?.toUpperCase() || "FILE";
            const downloadUrl = buildReportDownloadUrl(r.report_id, f.name);
            return (
              <a
                key={f.name}
                href={downloadUrl}
                download={f.name}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 dark:bg-slate-700 dark:hover:bg-indigo-950/60 dark:hover:text-indigo-300 rounded-md transition-colors"
              >
                <Download className="w-3 h-3" />
                <span>{ext}</span>
              </a>
            );
          })}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Comprehensive Reports"
        subtitle="Generate executive summary documentation, data exports, and high-resolution publication charts."
      />

      {/* Generator Form Card */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-700/80 shadow-sm space-y-5">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
            Generate New Academic Report
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Select target semester, cohort scope, and multi-format document outputs
          </p>
        </div>

        <form onSubmit={handleGenerate} className="space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Semester select */}
            <div>
              <label
                htmlFor="report-semester"
                className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5"
              >
                Target Semester *
              </label>
              <select
                id="report-semester"
                value={semester}
                onChange={(e) => setSemester(parseInt(e.target.value, 10))}
                className="w-full text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3.5 py-2.5 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {(meta?.semesters || [1, 2, 3, 4, 5, 6, 7, 8]).map((s) => (
                  <option key={s} value={s}>
                    Semester {s}
                  </option>
                ))}
              </select>
            </div>

            {/* Department select */}
            <div>
              <label
                htmlFor="report-dept"
                className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5"
              >
                Department (Optional)
              </label>
              <select
                id="report-dept"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3.5 py-2.5 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Departments (Institutional)</option>
                {meta?.departments.map((dept) => (
                  <option key={dept} value={dept}>
                    {dept}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Format Checkboxes */}
          <div>
            <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-2">
              Export Formats *
            </label>
            <div className="flex flex-wrap gap-4">
              {[
                { id: "pdf" as const, label: "Executive PDF Summary", icon: FileText },
                { id: "csv" as const, label: "CSV Raw Export", icon: FileCode },
                { id: "xlsx" as const, label: "Excel Spreadsheet (XLSX)", icon: FileSpreadsheet },
              ].map((fmt) => {
                const Icon = fmt.icon;
                const isChecked = selectedFormats.includes(fmt.id);
                return (
                  <label
                    key={fmt.id}
                    className={`flex items-center gap-2.5 px-3.5 py-2 rounded-xl border cursor-pointer select-none transition-colors text-xs font-medium ${
                      isChecked
                        ? "border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300"
                        : "border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleFormat(fmt.id)}
                      className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                    />
                    <Icon className="w-4 h-4" />
                    <span>{fmt.label}</span>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Action button */}
          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={generateMutation.isPending}
              className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-xl shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <FileText className="w-4 h-4" />
              {generateMutation.isPending ? "Generating Reports & Charts..." : "Generate Report Package"}
            </button>
          </div>
        </form>
      </div>

      {/* Generated Results Panel */}
      {latestReport && (
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-indigo-200 dark:border-indigo-800/80 shadow-md space-y-6 animate-in fade-in duration-200">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-700">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-600 text-white rounded-xl">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  Report #{latestReport.report_id} Ready for Download
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Semester {latestReport.semester ?? semester} • Generated successfully
                </p>
              </div>
            </div>
          </div>

          {/* Download Buttons */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Download Files
            </h4>
            <div className="flex flex-wrap gap-3">
              {latestReport.files.map((file: ReportFileItem) => {
                const downloadUrl = buildReportDownloadUrl(latestReport.report_id, file.name);
                return (
                  <a
                    key={file.name}
                    href={downloadUrl}
                    download={file.name}
                    className="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow-sm transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download {file.name}</span>
                  </a>
                );
              })}
            </div>
          </div>

          {/* Matplotlib Charts Gallery */}
          {latestReport.charts && latestReport.charts.length > 0 && (
            <div className="space-y-3 pt-2">
              <div className="flex items-center gap-2">
                <ImageIcon className="w-4 h-4 text-indigo-500" />
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  Generated Matplotlib Charts (Click to expand)
                </h4>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {latestReport.charts.map((chart: ReportFileItem) => {
                  const chartUrl = buildChartUrl(chart.url || chart.name);
                  return (
                    <div
                      key={chart.name}
                      onClick={() => setActiveLightboxChart(chart)}
                      className="group relative cursor-pointer overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 aspect-video flex items-center justify-center transition-all hover:shadow-md hover:border-indigo-400"
                    >
                      <img
                        src={chartUrl}
                        alt={chart.name}
                        className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-200"
                        onError={(e) => {
                          (e.currentTarget as HTMLImageElement).src =
                            "https://placehold.co/600x400/6366f1/ffffff?text=" + chart.name;
                        }}
                      />
                      <div className="absolute inset-0 bg-slate-900/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white">
                        <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 text-xs font-semibold">
                          <ZoomIn className="w-4 h-4" />
                          Expand Chart
                        </span>
                      </div>
                      <div className="absolute bottom-0 inset-x-0 p-2 bg-gradient-to-t from-slate-900/90 to-transparent text-white text-[11px] font-medium truncate">
                        {chart.name}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Lightbox Modal for Chart PNGs */}
      {activeLightboxChart && (
        <Modal
          isOpen={!!activeLightboxChart}
          onClose={() => setActiveLightboxChart(null)}
          title={activeLightboxChart.name}
          size="lg"
        >
          <div className="space-y-4">
            <div className="rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-950 flex items-center justify-center p-2">
              <img
                src={buildChartUrl(activeLightboxChart.url || activeLightboxChart.name)}
                alt={activeLightboxChart.name}
                className="max-h-[70vh] w-auto object-contain rounded-lg"
              />
            </div>
            <div className="flex justify-between items-center text-xs text-slate-500">
              <span>High-resolution Matplotlib publication figure</span>
              <a
                href={buildChartUrl(activeLightboxChart.url || activeLightboxChart.name)}
                download={activeLightboxChart.name}
                className="inline-flex items-center gap-1 text-indigo-600 dark:text-indigo-400 hover:underline font-semibold"
              >
                <Download className="w-3.5 h-3.5" />
                Download PNG
              </a>
            </div>
          </div>
        </Modal>
      )}

      {/* Past Reports Table */}
      <div className="space-y-3">
        <h3 className="text-base font-semibold text-slate-800 dark:text-slate-100">
          Historical Reports Catalog
        </h3>

        {isError && (
          <ErrorState
            title="Failed to load past reports"
            message="Could not retrieve historical reports catalog."
            onRetry={refetch}
          />
        )}

        <DataTable
          columns={pastReportsColumns}
          data={reports || []}
          keyExtractor={(r) => r.report_id}
          isLoading={isLoading}
          emptyTitle="No reports generated yet"
          emptyDescription="Configure the options above and click 'Generate Report Package' to create your first report."
        />
      </div>
    </div>
  );
};
