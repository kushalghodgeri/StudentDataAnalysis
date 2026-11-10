import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { cn } from "../../lib/utils";
import { Skeleton } from "../ui/Skeleton";

export interface HistogramBin {
  range: string;
  count: number;
}

export interface HistogramCardProps {
  title: string;
  subtitle?: string;
  data: HistogramBin[];
  mean?: number;
  median?: number;
  isLoading?: boolean;
  className?: string;
}

export const HistogramCard: React.FC<HistogramCardProps> = ({
  title,
  subtitle,
  data,
  mean,
  median,
  isLoading = false,
  className,
}) => {
  return (
    <div
      className={cn(
        "bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200/80 dark:border-slate-700/80 shadow-sm flex flex-col",
        className
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-800 dark:text-slate-100">{title}</h3>
          {subtitle && (
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>
          )}
        </div>
        {(mean !== undefined || median !== undefined) && (
          <div className="flex items-center gap-2 text-xs">
            {mean !== undefined && (
              <span className="px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-medium">
                Mean: {mean.toFixed(1)}
              </span>
            )}
            {median !== undefined && (
              <span className="px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-medium">
                Median: {median.toFixed(1)}
              </span>
            )}
          </div>
        )}
      </div>

      <div className="h-64 w-full flex-1">
        {isLoading ? (
          <div className="h-full flex items-center justify-center">
            <Skeleton className="h-4/5 w-full rounded-lg" />
          </div>
        ) : data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-slate-400">
            No histogram data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: -15, bottom: 15 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.5} />
              <XAxis dataKey="range" tick={{ fontSize: 11, fill: "#64748b" }} stroke="#cbd5e1" />
              <YAxis tick={{ fontSize: 11, fill: "#64748b" }} stroke="#cbd5e1" />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const row = payload[0].payload as HistogramBin;
                    return (
                      <div className="bg-slate-900/90 text-white dark:bg-slate-800 text-xs rounded-lg p-2.5 shadow-lg border border-slate-700">
                        <p className="font-semibold text-slate-200">Score Range: {row.range}</p>
                        <p className="mt-1 text-indigo-300">
                          Students: <span className="font-bold text-white">{row.count}</span>
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={54} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
