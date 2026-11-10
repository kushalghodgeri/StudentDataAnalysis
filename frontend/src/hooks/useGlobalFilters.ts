import { useSearchParams } from "react-router-dom";
import { useCallback, useMemo } from "react";

export interface GlobalFilters {
  semester?: number;
  department?: string;
}

export function useGlobalFilters() {
  const [searchParams, setSearchParams] = useSearchParams();

  const semester = useMemo(() => {
    const s = searchParams.get("semester");
    return s ? parseInt(s, 10) : undefined;
  }, [searchParams]);

  const department = useMemo(() => {
    return searchParams.get("department") || undefined;
  }, [searchParams]);

  const setSemester = useCallback(
    (sem: number | undefined | null) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (sem !== undefined && sem !== null) {
            next.set("semester", sem.toString());
          } else {
            next.delete("semester");
          }
          return next;
        },
        { replace: true }
      );
    },
    [setSearchParams]
  );

  const setDepartment = useCallback(
    (dept: string | undefined | null) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (dept) {
            next.set("department", dept);
          } else {
            next.delete("department");
          }
          return next;
        },
        { replace: true }
      );
    },
    [setSearchParams]
  );

  const clearFilters = useCallback(() => {
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        next.delete("semester");
        next.delete("department");
        return next;
      },
      { replace: true }
    );
  }, [setSearchParams]);

  const hasActiveFilters = Boolean(semester || department);

  return {
    filters: { semester, department },
    semester,
    department,
    hasActiveFilters,
    setSemester,
    setDepartment,
    clearFilters,
  };
}
