export interface Student {
  student_id: number;
  first_name: string;
  last_name: string;
  email: string;
  gender: "M" | "F" | "O";
  dob: string;
  department: string;
  admission_year: number;
}

export interface StudentEnrollment {
  enrollment_id?: number;
  course_id?: number;
  course_code?: string;
  course_name: string;
  credits?: number;
  semester: number;
  marks: number | null;
  attendance_pct: number | null;
  grade?: string;
  is_passed?: boolean;
  is_at_risk?: boolean;
}

export interface StudentStats {
  total_enrolled_courses?: number;
  total_courses?: number;
  gpa_marks_avg?: number | null;
  avg_marks?: number | null;
  overall_attendance_pct?: number | null;
  avg_attendance?: number | null;
  total_courses_passed?: number;
}

export interface StudentDetail extends Student {
  student?: Student;
  enrollments: StudentEnrollment[];
  stats: StudentStats;
}

export interface StudentQueryParams {
  page?: number;
  page_size?: number;
  department?: string;
  search?: string;
  sort_by?: string;
  order?: "ASC" | "DESC" | "asc" | "desc";
}
