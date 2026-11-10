import React from "react";
import { Filter, X, RotateCcw } from "lucide-react";
import { useGlobalFilters } from "../../hooks/useGlobalFilters";
import { useMetaFilters } from "../../hooks/useMetaFilters";
import { Badge } from "./Badge";
import { cn } from "../../lib/utils";

export interface FilterBarProps {
  className?: string;
  showCourseFilter?: boolean;
}

export const FilterBar: React.FC<FilterBarProps> = ({ className }) => {
  const { filters, setSemester, setDepartment, clearFilters, hasActiveFilters } = useGlobalFilters();
  const { data: meta, isLoading } = useMetaFilters();

  const semesters = meta?.semesters || [1, 2, 3, 4, 5, 6, 7, 8];
  const departments = meta?.departments || [
    "Computer Science",
    "Data Science",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Information Technology",
  ];

  return (
    <div
      className={cn(
        "flex flex-wrap items-center justify-between gap-3 p-3.5 bg-white dark:bg-slate-800/90 rounded-xl border border-slate-200/80 dark:border-slate-700/80 shadow-sm",
        className
      )}
    >
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          <Filter className="w-4 h-4 text-indigo-500" />
          <span>Filters:</span>
        </div>

        {/* Semester Select */}
        <div className="relative">
          <select
            value={filters.semester !== undefined ? String(filters.semester) : ""}
            onChange={(e) => {
              const val = e.target.value;
              setSemester(val === "" ? undefined : parseInt(val, 10));
            }}
            disabled={isLoading}
            aria-label="Filter by semester"
            className="text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors disabled:opacity-50"
          >
            <option value="">All Semesters</option>
            {semesters.map((s) => (
              <option key={s} value={s}>
                Semester {s}
              </option>
            ))}
          </select>
        </div>

        {/* Department Select */}
        <div className="relative">
          <select
            value={filters.department || ""}
            onChange={(e) => {
              const val = e.target.value;
              setDepartment(val === "" ? undefined : val);
            }}
            disabled={isLoading}
            aria-label="Filter by department"
            className="text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors disabled:opacity-50"
          >
            <option value="">All Departments</option>
            {departments.map((dept) => (
              <option key={dept} value={dept}>
                {dept}
              </option>
            ))}
          </select>
        </div>

        {/* Active badges */}
        {filters.semester && (
          <Badge variant="primary" className="gap-1 pl-2 pr-1 py-0.5">
            Sem {filters.semester}
            <button
              onClick={() => setSemester(undefined)}
              className="hover:text-indigo-900 dark:hover:text-white"
              aria-label="Clear semester filter"
            >
              <X className="w-3 h-3" />
            </button>
          </Badge>
        )}

        {filters.department && (
          <Badge variant="primary" className="gap-1 pl-2 pr-1 py-0.5">
            {filters.department}
            <button
              onClick={() => setDepartment(undefined)}
              className="hover:text-indigo-900 dark:hover:text-white"
              aria-label="Clear department filter"
            >
              <X className="w-3 h-3" />
            </button>
          </Badge>
        )}
      </div>

      {/* Clear All */}
      {hasActiveFilters && (
        <button
          onClick={clearFilters}
          type="button"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors px-2 py-1 rounded-md hover:bg-slate-100 dark:hover:bg-slate-700/50"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Clear filters
        </button>
      )}
    </div>
  );
};
