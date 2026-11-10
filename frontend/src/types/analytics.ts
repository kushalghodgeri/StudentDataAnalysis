export interface OverviewAnalytics {
  total_students: number;
  total_courses: number;
  avg_marks: number | null;
  pass_rate: number | null;
  avg_attendance: number | null;
  at_risk_count: number;
}

export interface Percentiles {
  p25?: number | null;
  p50?: number | null;
  p75?: number | null;
  p90?: number | null;
}

export interface PerformanceStats {
  count: number;
  mean: number | null;
  median: number | null;
  std: number | null;
  min: number | null;
  max: number | null;
  percentiles: Percentiles;
  pass_rate: number | null;
}

export interface StudentRanking {
  student_id: number;
  student_name?: string;
  full_name?: string;
  department: string;
  marks_avg?: number;
  avg_marks?: number;
  enrolled_courses?: number;
}

export type StudentRank = StudentRanking;

export interface PerformanceAnalytics {
  stats: PerformanceStats;
  grade_distribution: Record<string, number>;
  dept_averages: Record<string, number>;
  semester_trend: Record<string, number>;
  top10: StudentRanking[];
  bottom10: StudentRanking[];
}

export interface AtRiskStudent {
  student_id: number;
  student_name?: string;
  full_name?: string;
  department: string;
  semester?: number;
  course_code?: string;
  marks: number;
  attendance_pct: number;
}

export interface AttendanceAnalytics {
  by_department: Record<string, number>;
  correlation: number | null;
  at_risk: AtRiskStudent[];
}

export interface DemographicsAnalytics {
  gender: Record<string, number>;
  department_counts: Record<string, number>;
  cohorts: Record<string, number>;
}

export interface MetaFilters {
  departments: string[];
  semesters: number[];
  courses: Array<{
    course_id: number;
    course_code: string;
    course_name: string;
    credits: number;
  }>;
}
