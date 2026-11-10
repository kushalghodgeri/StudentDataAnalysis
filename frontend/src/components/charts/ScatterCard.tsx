import React from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { cn } from "../../lib/utils";
import { Skeleton } from "../ui/Skeleton";

export interface ScatterPoint {
  attendance: number;
  marks: number;
  student_name?: string;
  student_id?: number;
  department?: string;
  is_at_risk?: boolean;
}

export interface ScatterCardProps {
  title: string;
  subtitle?: string;
  data: ScatterPoint[];
  isLoading?: boolean;
  className?: string;
}

export const ScatterCard: React.FC<ScatterCardProps> = ({
  title,
  subtitle,
  data,
  isLoading = false,
  className,
}) => {
  const normalPoints = data.filter(
    (p) => !(p.is_at_risk ?? (p.attendance < 75 && p.marks < 40))
  );
  const atRiskPoints = data.filter(
    (p) => p.is_at_risk ?? (p.attendance < 75 && p.marks < 40)
  );

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
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
            <span className="text-slate-500 dark:text-slate-400">Regular</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
            <span className="text-rose-600 dark:text-rose-400 font-semibold">At-Risk</span>
          </div>
        </div>
      </div>

      <div className="h-64 w-full flex-1">
        {isLoading ? (
          <div className="h-full flex items-center justify-center">
            <Skeleton className="h-4/5 w-full rounded-lg" />
          </div>
        ) : data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-slate-400">
            No scatter data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 10, right: 15, left: -15, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" opacity={0.5} />
              <XAxis
                type="number"
                dataKey="attendance"
                name="Attendance"
                unit="%"
                domain={[0, 100]}
                tick={{ fontSize: 11, fill: "#64748b" }}
                stroke="#cbd5e1"
                label={{
                  value: "Attendance (%)",
                  position: "insideBottom",
                  offset: -12,
                  fontSize: 11,
                  fill: "#94a3b8",
                }}
              />
              <YAxis
                type="number"
                dataKey="marks"
                name="Marks"
                domain={[0, 100]}
                tick={{ fontSize: 11, fill: "#64748b" }}
                stroke="#cbd5e1"
                label={{
                  value: "Marks",
                  angle: -90,
                  position: "insideLeft",
                  offset: 25,
                  fontSize: 11,
                  fill: "#94a3b8",
                }}
              />
              {/* Threshold reference lines */}
              <ReferenceLine
                x={75}
                stroke="#f43f5e"
                strokeDasharray="4 4"
                label={{
                  value: "Min 75% Att",
                  position: "top",
                  fontSize: 10,
                  fill: "#f43f5e",
                }}
              />
              <ReferenceLine
                y={40}
                stroke="#f43f5e"
                strokeDasharray="4 4"
                label={{
                  value: "Pass (40)",
                  position: "right",
                  fontSize: 10,
                  fill: "#f43f5e",
                }}
              />
              <Tooltip
                cursor={{ strokeDasharray: "3 3" }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const pt = payload[0].payload as ScatterPoint;
                    const isRisk = pt.is_at_risk ?? (pt.attendance < 75 && pt.marks < 40);
                    return (
                      <div className="bg-slate-900/90 text-white dark:bg-slate-800 text-xs rounded-lg p-2.5 shadow-lg border border-slate-700">
                        {pt.student_name && (
                          <p className="font-semibold text-slate-200">
                            {pt.student_name}
                            {pt.student_id ? ` (#${pt.student_id})` : ""}
                          </p>
                        )}
                        {pt.department && (
                          <p className="text-[11px] text-slate-400">{pt.department}</p>
                        )}
                        <div className="mt-1.5 space-y-0.5">
                          <p className="text-slate-300">
                            Attendance:{" "}
                            <span className="font-bold text-white">{pt.attendance.toFixed(1)}%</span>
                          </p>
                          <p className="text-slate-300">
                            Marks:{" "}
                            <span className="font-bold text-white">{pt.marks.toFixed(1)}</span>
                          </p>
                        </div>
                        {isRisk && (
                          <span className="mt-2 inline-block px-2 py-0.5 text-[10px] font-bold rounded bg-rose-500/20 text-rose-300 border border-rose-500/40">
                            At Risk (Low Att & Marks)
                          </span>
                        )}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Scatter name="Regular" data={normalPoints} fill="#6366f1" fillOpacity={0.65} />
              <Scatter name="At-Risk" data={atRiskPoints} fill="#ef4444" fillOpacity={0.85} />
            </ScatterChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
