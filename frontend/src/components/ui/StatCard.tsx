import React from "react";
import { CardSkeleton } from "./Skeleton";
import { cn } from "../../lib/utils";

export interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  subtitle?: string;
  badge?: React.ReactNode;
  variant?: "indigo" | "emerald" | "amber" | "rose" | "sky" | "purple";
  isLoading?: boolean;
  className?: string;
}

const variantStyles: Record<
  NonNullable<StatCardProps["variant"]>,
  { iconBg: string; iconColor: string; accentBorder: string }
> = {
  indigo: {
    iconBg: "bg-indigo-50 dark:bg-indigo-950/60",
    iconColor: "text-indigo-600 dark:text-indigo-400",
    accentBorder: "border-l-indigo-500",
  },
  emerald: {
    iconBg: "bg-emerald-50 dark:bg-emerald-950/60",
    iconColor: "text-emerald-600 dark:text-emerald-400",
    accentBorder: "border-l-emerald-500",
  },
  amber: {
    iconBg: "bg-amber-50 dark:bg-amber-950/60",
    iconColor: "text-amber-600 dark:text-amber-400",
    accentBorder: "border-l-amber-500",
  },
  rose: {
    iconBg: "bg-rose-50 dark:bg-rose-950/60",
    iconColor: "text-rose-600 dark:text-rose-400",
    accentBorder: "border-l-rose-500",
  },
  sky: {
    iconBg: "bg-sky-50 dark:bg-sky-950/60",
    iconColor: "text-sky-600 dark:text-sky-400",
    accentBorder: "border-l-sky-500",
  },
  purple: {
    iconBg: "bg-purple-50 dark:bg-purple-950/60",
    iconColor: "text-purple-600 dark:text-purple-400",
    accentBorder: "border-l-purple-500",
  },
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  subtitle,
  badge,
  variant = "indigo",
  isLoading = false,
  className,
}) => {
  if (isLoading) {
    return <CardSkeleton />;
  }

  const v = variantStyles[variant];

  return (
    <div
      className={cn(
        "relative overflow-hidden bg-white dark:bg-slate-800 rounded-xl p-5 shadow-sm border border-slate-100 dark:border-slate-700/60 border-l-4 transition-all duration-200 hover:shadow-md",
        v.accentBorder,
        className
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 truncate">
          {title}
        </span>
        {icon && (
          <div
            className={cn(
              "w-9 h-9 rounded-lg flex items-center justify-center shrink-0",
              v.iconBg,
              v.iconColor
            )}
          >
            {icon}
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
          {value}
        </span>
        {badge && <span className="ml-auto">{badge}</span>}
      </div>

      {subtitle && (
        <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{subtitle}</p>
      )}
    </div>
  );
};
