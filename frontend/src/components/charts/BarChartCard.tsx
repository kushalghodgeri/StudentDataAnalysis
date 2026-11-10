import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { cn } from "../../lib/utils";
import { CHART_PALETTE } from "../../lib/constants";
import { Skeleton } from "../ui/Skeleton";

export interface BarChartDataPoint {
  name: string;
  value: number;
  [key: string]: unknown;
}

export interface BarChartCardProps {
  title: string;
  subtitle?: string;
  data: BarChartDataPoint[];
  dataKey?: string;
  nameKey?: string;
  yAxisUnit?: string;
  yDomain?: [number, number];
  color?: string;
  multiColor?: boolean;
  isLoading?: boolean;
  className?: string;
}

export const BarChartCard: React.FC<BarChartCardProps> = ({
  title,
  subtitle,
  data,
  dataKey = "value",
  nameKey = "name",
  yAxisUnit = "",
  yDomain = [0, 100],
  color = "#6366f1",
  multiColor = false,
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
            <BarChart data={data} margin={{ top: 10, right: 10, left: -15, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.5} />
              <XAxis
                dataKey={nameKey}
                tick={{ fontSize: 11, fill: "#64748b" }}
                angle={-20}
                textAnchor="end"
                interval={0}
                stroke="#cbd5e1"
              />
              <YAxis
                domain={yDomain}
                unit={yAxisUnit}
                tick={{ fontSize: 11, fill: "#64748b" }}
                stroke="#cbd5e1"
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const row = payload[0].payload;
                    const val = Number(row[dataKey]);
                    return (
                      <div className="bg-slate-900/90 text-white dark:bg-slate-800 text-xs rounded-lg p-2.5 shadow-lg border border-slate-700">
                        <p className="font-semibold text-slate-200">{row[nameKey]}</p>
                        <p className="mt-1 text-indigo-300">
                          Average: <span className="font-bold text-white">{val.toFixed(1)}{yAxisUnit}</span>
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey={dataKey} radius={[4, 4, 0, 0]} maxBarSize={48} fill={color}>
                {multiColor &&
                  data.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={CHART_PALETTE[index % CHART_PALETTE.length]}
                    />
                  ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
