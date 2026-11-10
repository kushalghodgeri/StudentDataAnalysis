import {
  AttendanceAnalytics,
  DemographicsAnalytics,
  MetaFilters,
  OverviewAnalytics,
  PerformanceAnalytics,
} from "@/types/analytics";
import { Student, StudentDetail } from "@/types/student";
import { ImportLog } from "@/types/import";
import { ReportLog } from "@/types/report";

export const MOCK_META_FILTERS: MetaFilters = {
  departments: [
    "Computer Science",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Information Technology",
    "Biotechnology",
  ],
  semesters: [1, 2, 3, 4, 5, 6, 7, 8],
  courses: [
    { course_id: 1, course_code: "CS101", course_name: "Introduction to Computer Science", credits: 4 },
    { course_id: 2, course_code: "CS102", course_name: "Data Structures & Algorithms", credits: 4 },
    { course_id: 3, course_code: "CS201", course_name: "Database Management Systems", credits: 3 },
    { course_id: 4, course_code: "EE101", course_name: "Circuit Analysis", credits: 3 },
    { course_id: 5, course_code: "ME101", course_name: "Engineering Mechanics", credits: 3 },
    { course_id: 6, course_code: "CE101", course_name: "Structural Mechanics", credits: 3 },
    { course_id: 7, course_code: "IT101", course_name: "Web Development Fundamentals", credits: 3 },
    { course_id: 8, course_code: "BT101", course_name: "Molecular Biology", credits: 3 },
  ],
};

export const MOCK_OVERVIEW: OverviewAnalytics = {
  total_students: 500,
  total_courses: 20,
  avg_marks: 68.4,
  pass_rate: 88.2,
  avg_attendance: 84.1,
  at_risk_count: 24,
};

export const MOCK_PERFORMANCE: PerformanceAnalytics = {
  stats: {
    count: 3120,
    mean: 68.4,
    median: 70.0,
    std: 14.2,
    min: 15.0,
    max: 99.0,
    percentiles: {
      p25: 58.5,
      p50: 70.0,
      p75: 79.5,
      p90: 88.0,
    },
    pass_rate: 88.2,
  },
  grade_distribution: {
    A: 420,
    B: 1150,
    C: 860,
    D: 320,
    F: 370,
  },
  dept_averages: {
    "Computer Science": 73.8,
    "Information Technology": 71.2,
    "Electrical Engineering": 67.5,
    "Biotechnology": 66.8,
    "Mechanical Engineering": 64.9,
    "Civil Engineering": 63.4,
  },
  semester_trend: {
    "Sem 1": 66.2,
    "Sem 2": 67.1,
    "Sem 3": 69.4,
    "Sem 4": 68.0,
    "Sem 5": 70.5,
    "Sem 6": 71.8,
    "Sem 7": 68.9,
    "Sem 8": 72.4,
  },
  top10: [
    { student_id: 101, full_name: "Sophia Chen", department: "Computer Science", marks_avg: 96.4, enrolled_courses: 7 },
    { student_id: 102, full_name: "Alexander Wright", department: "Computer Science", marks_avg: 94.8, enrolled_courses: 6 },
    { student_id: 103, full_name: "Elena Rostova", department: "Information Technology", marks_avg: 93.5, enrolled_courses: 6 },
    { student_id: 104, full_name: "Liam O'Connor", department: "Electrical Engineering", marks_avg: 92.1, enrolled_courses: 7 },
    { student_id: 105, full_name: "Aria Tanaka", department: "Biotechnology", marks_avg: 91.8, enrolled_courses: 6 },
    { student_id: 106, full_name: "Marcus Vance", department: "Computer Science", marks_avg: 91.2, enrolled_courses: 7 },
    { student_id: 107, full_name: "Maya Patel", department: "Information Technology", marks_avg: 90.6, enrolled_courses: 6 },
    { student_id: 108, full_name: "Gabriel Santos", department: "Mechanical Engineering", marks_avg: 89.9, enrolled_courses: 6 },
    { student_id: 109, full_name: "Chloe Dubois", department: "Biotechnology", marks_avg: 89.5, enrolled_courses: 7 },
    { student_id: 110, full_name: "David Kim", department: "Civil Engineering", marks_avg: 89.2, enrolled_courses: 6 },
  ],
  bottom10: [
    { student_id: 201, full_name: "James Wilson", department: "Civil Engineering", marks_avg: 31.4, enrolled_courses: 5 },
    { student_id: 202, full_name: "Tyler Jenkins", department: "Mechanical Engineering", marks_avg: 33.2, enrolled_courses: 6 },
    { student_id: 203, full_name: "Hannah Abbott", department: "Electrical Engineering", marks_avg: 34.8, enrolled_courses: 5 },
    { student_id: 204, full_name: "Kevin Miller", department: "Civil Engineering", marks_avg: 35.6, enrolled_courses: 6 },
    { student_id: 205, full_name: "Samantha Cruz", department: "Biotechnology", marks_avg: 36.5, enrolled_courses: 5 },
    { student_id: 206, full_name: "Lucas Meyer", department: "Mechanical Engineering", marks_avg: 37.1, enrolled_courses: 6 },
    { student_id: 207, full_name: "Olivia Bailey", department: "Information Technology", marks_avg: 37.8, enrolled_courses: 5 },
    { student_id: 208, full_name: "Daniel Foster", department: "Computer Science", marks_avg: 38.2, enrolled_courses: 6 },
    { student_id: 209, full_name: "Zoe Robinson", department: "Electrical Engineering", marks_avg: 38.9, enrolled_courses: 5 },
    { student_id: 210, full_name: "Ethan Reed", department: "Civil Engineering", marks_avg: 39.4, enrolled_courses: 6 },
  ],
};

export const MOCK_ATTENDANCE: AttendanceAnalytics = {
  by_department: {
    "Computer Science": 87.2,
    "Information Technology": 85.6,
    "Biotechnology": 84.8,
    "Electrical Engineering": 83.1,
    "Civil Engineering": 81.5,
    "Mechanical Engineering": 80.9,
  },
  correlation: 0.6842,
  at_risk: [
    { student_id: 201, full_name: "James Wilson", department: "Civil Engineering", semester: 2, course_code: "CE101", marks: 31.4, attendance_pct: 54.0 },
    { student_id: 202, full_name: "Tyler Jenkins", department: "Mechanical Engineering", semester: 3, course_code: "ME101", marks: 33.2, attendance_pct: 62.5 },
    { student_id: 203, full_name: "Hannah Abbott", department: "Electrical Engineering", semester: 1, course_code: "EE101", marks: 34.8, attendance_pct: 58.0 },
    { student_id: 204, full_name: "Kevin Miller", department: "Civil Engineering", semester: 4, course_code: "CE201", marks: 35.6, attendance_pct: 66.0 },
    { student_id: 205, full_name: "Samantha Cruz", department: "Biotechnology", semester: 2, course_code: "BT101", marks: 36.5, attendance_pct: 68.5 },
    { student_id: 206, full_name: "Lucas Meyer", department: "Mechanical Engineering", semester: 1, course_code: "ME101", marks: 37.1, attendance_pct: 71.0 },
    { student_id: 207, full_name: "Olivia Bailey", department: "Information Technology", semester: 3, course_code: "IT101", marks: 37.8, attendance_pct: 69.5 },
    { student_id: 208, full_name: "Daniel Foster", department: "Computer Science", semester: 2, course_code: "CS102", marks: 38.2, attendance_pct: 73.0 },
  ],
};

export const MOCK_DEMOGRAPHICS: DemographicsAnalytics = {
  gender: {
    M: 275,
    F: 205,
    O: 20,
  },
  department_counts: {
    "Computer Science": 140,
    "Electrical Engineering": 95,
    "Mechanical Engineering": 85,
    "Information Technology": 80,
    "Civil Engineering": 60,
    "Biotechnology": 40,
  },
  cohorts: {
    "2021": 110,
    "2022": 135,
    "2023": 145,
    "2024": 110,
  },
};

export const MOCK_STUDENTS: Student[] = [
  { student_id: 1, first_name: "Sophia", last_name: "Chen", email: "sophia.chen@university.edu", gender: "F", dob: "2003-04-12", department: "Computer Science", admission_year: 2022 },
  { student_id: 2, first_name: "Alexander", last_name: "Wright", email: "alex.wright@university.edu", gender: "M", dob: "2002-09-18", department: "Computer Science", admission_year: 2022 },
  { student_id: 3, first_name: "Elena", last_name: "Rostova", email: "elena.rostova@university.edu", gender: "F", dob: "2003-01-24", department: "Information Technology", admission_year: 2023 },
  { student_id: 4, first_name: "Liam", last_name: "O'Connor", email: "liam.oconnor@university.edu", gender: "M", dob: "2002-11-05", department: "Electrical Engineering", admission_year: 2021 },
  { student_id: 5, first_name: "Aria", last_name: "Tanaka", email: "aria.tanaka@university.edu", gender: "F", dob: "2004-03-30", department: "Biotechnology", admission_year: 2023 },
  { student_id: 6, first_name: "Marcus", last_name: "Vance", email: "marcus.vance@university.edu", gender: "M", dob: "2002-07-14", department: "Computer Science", admission_year: 2022 },
  { student_id: 7, first_name: "Maya", last_name: "Patel", email: "maya.patel@university.edu", gender: "F", dob: "2003-08-09", department: "Information Technology", admission_year: 2022 },
  { student_id: 8, first_name: "Gabriel", last_name: "Santos", email: "gabriel.santos@university.edu", gender: "M", dob: "2001-12-15", department: "Mechanical Engineering", admission_year: 2021 },
  { student_id: 9, first_name: "Chloe", last_name: "Dubois", email: "chloe.dubois@university.edu", gender: "F", dob: "2003-06-22", department: "Biotechnology", admission_year: 2023 },
  { student_id: 10, first_name: "David", last_name: "Kim", email: "david.kim@university.edu", gender: "M", dob: "2002-05-19", department: "Civil Engineering", admission_year: 2022 },
  { student_id: 11, first_name: "Zara", last_name: "Al-Mansoor", email: "zara.almansoor@university.edu", gender: "F", dob: "2003-10-11", department: "Computer Science", admission_year: 2023 },
  { student_id: 12, first_name: "Oliver", last_name: "Bennett", email: "oliver.bennett@university.edu", gender: "M", dob: "2002-02-28", department: "Electrical Engineering", admission_year: 2022 },
  { student_id: 13, first_name: "Hannah", last_name: "Abbott", email: "hannah.abbott@university.edu", gender: "F", dob: "2003-05-04", department: "Electrical Engineering", admission_year: 2023 },
  { student_id: 14, first_name: "James", last_name: "Wilson", email: "james.wilson@university.edu", gender: "M", dob: "2002-04-16", department: "Civil Engineering", admission_year: 2022 },
  { student_id: 15, first_name: "Tyler", last_name: "Jenkins", email: "tyler.jenkins@university.edu", gender: "M", dob: "2001-08-31", department: "Mechanical Engineering", admission_year: 2021 },
];

export const MOCK_STUDENT_DETAIL: StudentDetail = {
  student_id: 1,
  first_name: "Sophia",
  last_name: "Chen",
  email: "sophia.chen@university.edu",
  gender: "F",
  dob: "2003-04-12",
  department: "Computer Science",
  admission_year: 2022,
  stats: {
    total_enrolled_courses: 6,
    gpa_marks_avg: 96.4,
    overall_attendance_pct: 95.8,
    total_courses_passed: 6,
  },
  enrollments: [
    { enrollment_id: 1, course_id: 1, course_code: "CS101", course_name: "Introduction to Computer Science", credits: 4, semester: 1, marks: 98.0, attendance_pct: 96.5, grade: "A", is_passed: true, is_at_risk: false },
    { enrollment_id: 2, course_id: 2, course_code: "CS102", course_name: "Data Structures & Algorithms", credits: 4, semester: 2, marks: 95.5, attendance_pct: 94.0, grade: "A", is_passed: true, is_at_risk: false },
    { enrollment_id: 3, course_id: 3, course_code: "CS201", course_name: "Database Management Systems", credits: 3, semester: 3, marks: 97.0, attendance_pct: 98.0, grade: "A", is_passed: true, is_at_risk: false },
    { enrollment_id: 4, course_id: 7, course_code: "IT101", course_name: "Web Development Fundamentals", credits: 3, semester: 3, marks: 99.0, attendance_pct: 97.5, grade: "A", is_passed: true, is_at_risk: false },
    { enrollment_id: 5, course_id: 4, course_code: "EE101", course_name: "Circuit Analysis", credits: 3, semester: 4, marks: 93.0, attendance_pct: 92.0, grade: "A", is_passed: true, is_at_risk: false },
    { enrollment_id: 6, course_id: 5, course_code: "ME101", course_name: "Engineering Mechanics", credits: 3, semester: 4, marks: 96.0, attendance_pct: 97.0, grade: "A", is_passed: true, is_at_risk: false },
  ],
};

export const MOCK_IMPORT_LOGS: ImportLog[] = [
  {
    import_id: 104,
    file_name: "spring_2024_admissions.xlsx",
    file_type: "EXCEL",
    total_rows: 250,
    valid_rows: 246,
    rejected_rows: 4,
    duplicates_removed: 2,
    nulls_filled: 8,
    outliers_flagged: 3,
    status: "SUCCESS",
    imported_at: "2026-11-08T10:15:30Z",
  },
  {
    import_id: 103,
    file_name: "midterm_exam_marks_batch2.csv",
    file_type: "CSV",
    total_rows: 1200,
    valid_rows: 1188,
    rejected_rows: 12,
    duplicates_removed: 5,
    nulls_filled: 24,
    outliers_flagged: 18,
    status: "PARTIAL",
    error_summary: "12 rows dropped due to missing student IDs.",
    imported_at: "2026-11-05T14:22:10Z",
  },
  {
    import_id: 102,
    file_name: "attendance_records_october.csv",
    file_type: "CSV",
    total_rows: 3100,
    valid_rows: 3100,
    rejected_rows: 0,
    duplicates_removed: 14,
    nulls_filled: 12,
    outliers_flagged: 9,
    status: "SUCCESS",
    imported_at: "2026-10-31T09:00:00Z",
  },
];

export const MOCK_REPORTS: ReportLog[] = [
  {
    report_id: "rep_20261110_154908_1",
    created_at: "2026-11-10T15:49:08Z",
    semester: 1,
    department: "Computer Science",
    formats: ["pdf", "csv", "xlsx"],
    files: [
      { name: "report_rep_20261110_154908_1.pdf", url: "/api/v1/reports/rep_20261110_154908_1/download/report_rep_20261110_154908_1.pdf" },
      { name: "report_rep_20261110_154908_1.xlsx", url: "/api/v1/reports/rep_20261110_154908_1/download/report_rep_20261110_154908_1.xlsx" },
      { name: "report_rep_20261110_154908_1.csv", url: "/api/v1/reports/rep_20261110_154908_1/download/report_rep_20261110_154908_1.csv" },
    ],
    charts: [
      { name: "rep_20261110_154908_1_department_avg_bar.png", url: "/api/v1/charts/rep_20261110_154908_1_department_avg_bar.png" },
      { name: "rep_20261110_154908_1_marks_histogram.png", url: "/api/v1/charts/rep_20261110_154908_1_marks_histogram.png" },
      { name: "rep_20261110_154908_1_course_boxplot.png", url: "/api/v1/charts/rep_20261110_154908_1_course_boxplot.png" },
      { name: "rep_20261110_154908_1_semester_trend_line.png", url: "/api/v1/charts/rep_20261110_154908_1_semester_trend_line.png" },
      { name: "rep_20261110_154908_1_attendance_vs_marks_scatter.png", url: "/api/v1/charts/rep_20261110_154908_1_attendance_vs_marks_scatter.png" },
      { name: "rep_20261110_154908_1_grade_donut.png", url: "/api/v1/charts/rep_20261110_154908_1_grade_donut.png" },
      { name: "rep_20261110_154908_1_dept_course_heatmap.png", url: "/api/v1/charts/rep_20261110_154908_1_dept_course_heatmap.png" },
    ],
  },
];
