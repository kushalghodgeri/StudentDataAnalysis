import React, { useState } from "react";
import { cn } from "../../lib/utils";
import { Skeleton } from "../ui/Skeleton";

export interface HeatmapCell {
  department: string;
  course: string;
  avg_marks: number;
  students_count?: number;
}

export interface HeatmapCardProps {
  title: string;
  subtitle?: string;
  data: HeatmapCell[];
  departments?: string[];
  courses?: string[];
  isLoading?: boolean;
  className?: string;
}

function getCellBgColor(score: number): string {
  if (score >= 80) return "bg-emerald-600 text-white font-bold";
  if (score >= 70) return "bg-emerald-500 text-white font-medium";
  if (score >= 60) return "bg-indigo-500 text-white font-medium";
  if (score >= 50) return "bg-indigo-400 text-white";
  if (score >= 40) return "bg-amber-400 text-slate-900";
  return "bg-rose-500 text-white font-semibold";
}

export const HeatmapCard: React.FC<HeatmapCardProps> = ({
  title,
  subtitle,
  data,
  departments: customDepts,
  courses: customCourses,
  isLoading = false,
  className,
}) => {
  const [hoveredCell, setHoveredCell] = useState<HeatmapCell | null>(null);

  // Derive unique departments and courses if not provided
  const departments =
    customDepts || Array.from(new Set(data.map((d) => d.department))).sort();
  const courses =
    customCourses || Array.from(new Set(data.map((d) => d.course))).sort();

  // Map for fast O(1) lookup
  const cellMap = new Map<string, HeatmapCell>();
  data.forEach((d) => {
    cellMap.set(`${d.department}__${d.course}`, d);
  });

  return (
    <div
      className={cn(
        "bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200/80 dark:border-slate-700/80 shadow-sm flex flex-col",
        className
      )}
    >
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-800 dark:text-slate-100">{title}</h3>
          {subtitle && (
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>
          )}
        </div>

        {/* Legend */}
        <div className="flex items-center gap-1.5 text-[11px] text-slate-500 dark:text-slate-400">
          <span>&lt;40</span>
          <span className="w-3.5 h-3.5 rounded bg-rose-500 inline-block" />
          <span className="w-3.5 h-3.5 rounded bg-amber-400 inline-block" />
          <span className="w-3.5 h-3.5 rounded bg-indigo-400 inline-block" />
          <span className="w-3.5 h-3.5 rounded bg-indigo-500 inline-block" />
          <span className="w-3.5 h-3.5 rounded bg-emerald-500 inline-block" />
          <span className="w-3.5 h-3.5 rounded bg-emerald-600 inline-block" />
          <span>80+</span>
        </div>
      </div>

      {isLoading ? (
        <Skeleton className="h-64 w-full rounded-lg" />
      ) : departments.length === 0 || courses.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-xs text-slate-400">
          No heatmap data available
        </div>
      ) : (
        <div className="overflow-x-auto relative pb-2">
          <table className="w-full border-separate border-spacing-1.5 text-xs">
            <thead>
              <tr>
                <th className="p-2 text-left text-slate-500 dark:text-slate-400 font-semibold max-w-[140px] truncate">
                  Dept \ Course
                </th>
                {courses.map((c) => (
                  <th
                    key={c}
                    className="p-2 text-center text-slate-600 dark:text-slate-300 font-medium whitespace-nowrap min-w-[70px]"
                  >
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {departments.map((dept) => (
                <tr key={dept}>
                  <td className="p-2 font-medium text-slate-700 dark:text-slate-200 whitespace-nowrap max-w-[140px] truncate">
                    {dept}
                  </td>
                  {courses.map((crs) => {
                    const cell = cellMap.get(`${dept}__${crs}`);
                    const score = cell ? cell.avg_marks : 0;
                    return (
                      <td
                        key={`${dept}-${crs}`}
                        onMouseEnter={() => cell && setHoveredCell(cell)}
                        onMouseLeave={() => setHoveredCell(null)}
                        className={cn(
                          "p-2 text-center rounded-lg transition-transform hover:scale-105 cursor-pointer select-none",
                          cell ? getCellBgColor(score) : "bg-slate-100 dark:bg-slate-800 text-slate-400"
                        )}
                      >
                        {cell ? score.toFixed(0) : "-"}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>

          {/* Hover details badge */}
          {hoveredCell && (
            <div className="mt-3 p-2 bg-slate-900/90 text-white text-xs rounded-lg inline-flex items-center gap-3 shadow-md animate-in fade-in duration-150">
              <span className="font-semibold">{hoveredCell.department}</span>
              <span className="text-slate-400">|</span>
              <span className="text-indigo-300">{hoveredCell.course}</span>
              <span className="text-slate-400">|</span>
              <span>
                Avg Marks: <strong className="text-white">{hoveredCell.avg_marks.toFixed(1)}</strong>
              </span>
              {hoveredCell.students_count !== undefined && (
                <>
                  <span className="text-slate-400">|</span>
                  <span>Students: {hoveredCell.students_count}</span>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
