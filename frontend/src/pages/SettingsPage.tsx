import React from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Sun,
  Moon,
  CheckCircle2,
  XCircle,
  Database,
  Layers,
  Code2,
  RefreshCw,
} from "lucide-react";
import { PageHeader } from "../components/layout/PageHeader";
import { Badge } from "../components/ui/Badge";
import { useTheme } from "../context/ThemeContext";
import { fetchHealth } from "../api/health";
import { cn } from "../lib/utils";

export const SettingsPage: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const isMockMode = import.meta.env.VITE_USE_MOCKS === "true";
  const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

  const {
    data: health,
    isLoading: isHealthLoading,
    isError: isHealthError,
    refetch: refetchHealth,
    dataUpdatedAt,
  } = useQuery({
    queryKey: ["healthCheck"],
    queryFn: fetchHealth,
    refetchInterval: 15000,
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings & System Diagnostics"
        subtitle="Manage appearance preferences, inspect API connectivity, and verify system status."
      />

      {/* Theme Preference Section */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-700/80 shadow-sm space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
            Interface Appearance
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Choose your preferred dashboard theme. Settings persist in local storage.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-md">
          {/* Light Mode */}
          <button
            onClick={() => setTheme("light")}
            type="button"
            className={cn(
              "flex items-center gap-3 p-4 rounded-xl border text-left transition-all",
              theme === "light"
                ? "border-indigo-600 bg-indigo-50/50 text-indigo-900 font-semibold ring-2 ring-indigo-500/20"
                : "border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/40"
            )}
          >
            <div className="w-10 h-10 rounded-lg bg-amber-100 text-amber-600 flex items-center justify-center shrink-0">
              <Sun className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-semibold">Light Theme</p>
              <p className="text-xs text-slate-500">Crisp, clean contrast</p>
            </div>
          </button>

          {/* Dark Mode */}
          <button
            onClick={() => setTheme("dark")}
            type="button"
            className={cn(
              "flex items-center gap-3 p-4 rounded-xl border text-left transition-all",
              theme === "dark"
                ? "border-indigo-500 bg-indigo-950/40 text-indigo-200 font-semibold ring-2 ring-indigo-500/20"
                : "border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/40"
            )}
          >
            <div className="w-10 h-10 rounded-lg bg-indigo-950 text-indigo-400 flex items-center justify-center shrink-0">
              <Moon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-semibold">Dark Theme</p>
              <p className="text-xs text-slate-500">Subtle slate palette</p>
            </div>
          </button>
        </div>
      </div>

      {/* Backend API Health Section */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-700/80 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
              Backend API Health Diagnostics
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Continuous live status monitor targeting endpoint <code className="text-indigo-500">{apiUrl}/health</code>
            </p>
          </div>

          <button
            onClick={() => refetchHealth()}
            disabled={isHealthLoading}
            type="button"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300 bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 rounded-lg transition-colors"
          >
            <RefreshCw className={cn("w-3.5 h-3.5", isHealthLoading && "animate-spin")} />
            <span>Check Now</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Server Status */}
          <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/50">
            <span className="text-xs text-slate-500 font-medium">Service Status</span>
            <div className="flex items-center gap-2 mt-2">
              {isHealthError ? (
                <>
                  <XCircle className="w-5 h-5 text-rose-500" />
                  <span className="text-base font-bold text-rose-600 dark:text-rose-400">
                    Unavailable
                  </span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                  <span className="text-base font-bold text-emerald-600 dark:text-emerald-400">
                    {health?.status ? health.status.toUpperCase() : "HEALTHY"}
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Database Connection */}
          <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/50">
            <span className="text-xs text-slate-500 font-medium">MySQL Connection</span>
            <div className="flex items-center gap-2 mt-2">
              {health?.db_connected !== false ? (
                <>
                  <Database className="w-5 h-5 text-indigo-500" />
                  <span className="text-base font-bold text-slate-800 dark:text-slate-200">
                    Connected
                  </span>
                </>
              ) : (
                <>
                  <XCircle className="w-5 h-5 text-amber-500" />
                  <span className="text-base font-bold text-amber-600 dark:text-amber-400">
                    Disconnected
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Execution Environment */}
          <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/50">
            <span className="text-xs text-slate-500 font-medium">Active Data Layer</span>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant={isMockMode ? "warning" : "success"} size="sm">
                {isMockMode ? "MSW Mock Handlers" : "Live FastAPI Backend"}
              </Badge>
            </div>
          </div>
        </div>

        {dataUpdatedAt && (
          <p className="text-[11px] text-slate-400">
            Last pinged at: {new Date(dataUpdatedAt).toLocaleTimeString()}
          </p>
        )}
      </div>

      {/* Architecture & About Card */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-700/80 shadow-sm space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
            System Architecture
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Production grade layered full-stack application
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-600 dark:text-slate-300">
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200/60 dark:border-slate-700/60 space-y-2">
            <div className="flex items-center gap-2 font-semibold text-slate-900 dark:text-slate-100">
              <Layers className="w-4 h-4 text-indigo-500" />
              <span>Frontend Stack</span>
            </div>
            <ul className="list-disc list-inside space-y-1 text-slate-500 dark:text-slate-400">
              <li>React 18 + Vite + TypeScript</li>
              <li>TanStack Query v5 (Data caching & invalidation)</li>
              <li>Tailwind CSS + Lucide Icons</li>
              <li>Recharts (Responsive SVG visual data charts)</li>
              <li>MSW (Mock Service Worker v2) for autonomous UI dev</li>
            </ul>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200/60 dark:border-slate-700/60 space-y-2">
            <div className="flex items-center gap-2 font-semibold text-slate-900 dark:text-slate-100">
              <Code2 className="w-4 h-4 text-emerald-500" />
              <span>Backend Stack</span>
            </div>
            <ul className="list-disc list-inside space-y-1 text-slate-500 dark:text-slate-400">
              <li>Python 3.11+ / FastAPI / Uvicorn</li>
              <li>MySQL 8 Connection Pool + SQLAlchemy</li>
              <li>Pandas & NumPy statistical analyzers</li>
              <li>Matplotlib headless Agg chart generator</li>
              <li>Clean ETL pipeline (IQR outlier detection, imputation)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
