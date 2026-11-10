import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { cn } from "../../lib/utils";
import { Skeleton } from "../ui/Skeleton";

export interface DonutSegment {
  name: string;
  value: number;
  color?: string;
  [key: string]: unknown;
}

export interface DonutCardProps {
  title: string;
  subtitle?: string;
  data: DonutSegment[];
  centerLabel?: string;
  centerValue?: string | number;
  isLoading?: boolean;
  className?: string;
}

export const DonutCard: React.FC<DonutCardProps> = ({
  title,
  subtitle,
  data,
  centerLabel,
  centerValue,
  isLoading = false,
  className,
}) => {
  const total = data.reduce((acc, curr) => acc + (curr.value || 0), 0);

  return (
    <div
      className={cn(
        "bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200/80 dark:border-slate-700/80 shadow-sm flex flex-col",
        className
      )}
    >
      <div className="mb-2">
        <h3 className="text-base font-semibold text-slate-800 dark:text-slate-100">{title}</h3>
        {subtitle && (
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>
        )}
      </div>

      <div className="relative h-64 w-full flex-1 flex items-center justify-center">
        {isLoading ? (
          <Skeleton className="h-44 w-44 rounded-full" />
        ) : data.length === 0 ? (
          <div className="text-xs text-slate-400">No data available</div>
        ) : (
          <>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const item = payload[0].payload as DonutSegment;
                      const pct = total > 0 ? ((item.value / total) * 100).toFixed(1) : "0";
                      return (
                        <div className="bg-slate-900/90 text-white dark:bg-slate-800 text-xs rounded-lg p-2.5 shadow-lg border border-slate-700">
                          <p className="font-semibold text-slate-200">{item.name}</p>
                          <p className="mt-1">
                            Count: <span className="font-bold text-white">{item.value}</span> ({pct}%)
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  iconType="circle"
                  iconSize={8}
                  formatter={(value: string) => (
                    <span className="text-xs text-slate-600 dark:text-slate-300 font-medium ml-1">
                      {value}
                    </span>
                  )}
                />
                <Pie
                  data={data}
                  cx="50%"
                  cy="45%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {data.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.color || "#6366f1"}
                      stroke="transparent"
                    />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>

            {/* Centered Stat */}
            {(centerLabel || centerValue !== undefined) && (
              <div className="absolute top-[42%] left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none text-center">
                {centerValue !== undefined && (
                  <span className="block text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {centerValue}
                  </span>
                )}
                {centerLabel && (
                  <span className="block text-[11px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                    {centerLabel}
                  </span>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
