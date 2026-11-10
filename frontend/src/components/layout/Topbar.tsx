import React from "react";
import { Menu, Database, ShieldCheck } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import { Badge } from "../ui/Badge";
import { cn } from "../../lib/utils";

export interface TopbarProps {
  onMenuClick: () => void;
  className?: string;
}

export const Topbar: React.FC<TopbarProps> = ({ onMenuClick, className }) => {
  const isMockMode = import.meta.env.VITE_USE_MOCKS === "true";

  return (
    <header
      className={cn(
        "h-16 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30",
        className
      )}
    >
      <div className="flex items-center gap-3">
        {/* Mobile menu toggle */}
        <button
          onClick={onMenuClick}
          type="button"
          className="p-2 rounded-xl text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 lg:hidden transition-colors"
          aria-label="Open sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:flex items-center gap-2">
          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
            Analytics Studio
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Mock Mode or Live indicator */}
        {isMockMode ? (
          <Badge variant="warning" size="sm" className="gap-1.5 hidden xs:inline-flex">
            <Database className="w-3.5 h-3.5 text-amber-500" />
            <span>Mock Mode (MSW)</span>
          </Badge>
        ) : (
          <Badge variant="success" size="sm" className="gap-1.5 hidden xs:inline-flex">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
            <span>Live API</span>
          </Badge>
        )}

        {/* Theme Toggle */}
        <ThemeToggle />
      </div>
    </header>
  );
};
