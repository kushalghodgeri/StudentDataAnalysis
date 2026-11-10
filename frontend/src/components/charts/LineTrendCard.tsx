import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { cn } from "../../lib/utils";
import { Skeleton } from "../ui/Skeleton";

export interface LineSeries {
  dataKey: string;
  name: string;
  color: string;
  strokeDasharray?: string;
}

export interface LineTrendCardProps {
  title: string;
  subtitle?: string;
  data: Record<string, unknown>[];
  xAxisKey?: string;
  series: LineSeries[];
  yDomain?: [number, number];
  unit?: string;
  isLoading?: boolean;
  className?: string;
}

export const LineTrendCard: React.FC<LineTrendCardProps> = ({
  title,
  subtitle,
  data,
  xAxisKey = "semester",
  series,
  yDomain = [0, 100],
  unit = "",
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
      <div className="mb-4">
        <h3 className="text-base font-semibold text-slate-800 dark:text-slate-100">{title}</h3>
        {subtitle && (
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>
        )}
      </div>

      <div className="h-64 w-full flex-1">
        {isLoading ? (
          <div className="h-full flex items-center justify-center">
            <Skeleton className="h-4/5 w-full rounded-lg" />
          </div>
        ) : data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-slate-400">
            No data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 15, left: -15, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.5} />
              <XAxis
                dataKey={xAxisKey}
                tick={{ fontSize: 11, fill: "#64748b" }}
                stroke="#cbd5e1"
              />
              <YAxis
                domain={yDomain}
                unit={unit}
                tick={{ fontSize: 11, fill: "#64748b" }}
                stroke="#cbd5e1"
              />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-slate-900/90 text-white dark:bg-slate-800 text-xs rounded-lg p-2.5 shadow-lg border border-slate-700 space-y-1">
                        <p className="font-semibold text-slate-300 border-b border-slate-700 pb-1">
                          {xAxisKey.toUpperCase()}: {label}
                        </p>
                        {payload.map((entry, idx) => (
                          <div key={idx} className="flex items-center justify-between gap-3">
                            <span style={{ color: entry.color }}>{entry.name}:</span>
                            <span className="font-bold text-white">
                              {Number(entry.value).toFixed(1)}{unit}
                            </span>
                          </div>
                        ))}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              {series.length > 1 && (
                <Legend
                  verticalAlign="top"
                  align="right"
                  iconType="circle"
                  iconSize={8}
                  formatter={(val: string) => (
                    <span className="text-xs text-slate-600 dark:text-slate-300 font-medium">
                      {val}
                    </span>
                  )}
                />
              )}
              {series.map((s) => (
                <Line
                  key={s.dataKey}
                  type="monotone"
                  dataKey={s.dataKey}
                  name={s.name}
                  stroke={s.color}
                  strokeWidth={2.5}
                  dot={{ r: 4, strokeWidth: 2, fill: "#ffffff" }}
                  activeDot={{ r: 6, strokeWidth: 0 }}
                  strokeDasharray={s.strokeDasharray}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
