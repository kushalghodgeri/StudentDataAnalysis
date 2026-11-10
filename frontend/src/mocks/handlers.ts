import { http, HttpResponse } from "msw";
import {
  MOCK_ATTENDANCE,
  MOCK_DEMOGRAPHICS,
  MOCK_IMPORT_LOGS,
  MOCK_META_FILTERS,
  MOCK_OVERVIEW,
  MOCK_PERFORMANCE,
  MOCK_REPORTS,
  MOCK_STUDENT_DETAIL,
  MOCK_STUDENTS,
} from "./fixtures";

const API_BASE = "*/api/v1";

export const handlers = [
  // Health Check
  http.get(`${API_BASE}/health`, () => {
    return HttpResponse.json({
      status: "healthy",
      db_connected: true,
    });
  }),
  http.get("*/health", () => {
    return HttpResponse.json({
      status: "healthy",
      db_connected: true,
    });
  }),

  // Meta Filters
  http.get(`${API_BASE}/meta/filters`, () => {
    return HttpResponse.json(MOCK_META_FILTERS);
  }),

  // Analytics Overview
  http.get(`${API_BASE}/analytics/overview`, () => {
    return HttpResponse.json(MOCK_OVERVIEW);
  }),

  // Analytics Performance
  http.get(`${API_BASE}/analytics/performance`, () => {
    return HttpResponse.json(MOCK_PERFORMANCE);
  }),

  // Analytics Attendance
  http.get(`${API_BASE}/analytics/attendance`, () => {
    return HttpResponse.json(MOCK_ATTENDANCE);
  }),

  // Analytics Demographics
  http.get(`${API_BASE}/analytics/demographics`, () => {
    return HttpResponse.json(MOCK_DEMOGRAPHICS);
  }),

  // Paginated Students List
  http.get(`${API_BASE}/students`, ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get("page") || "1", 10);
    const pageSize = parseInt(url.searchParams.get("page_size") || "10", 10);
    const department = url.searchParams.get("department");
    const search = url.searchParams.get("search")?.toLowerCase();
    const sortBy = url.searchParams.get("sort_by") || "student_id";
    const order = (url.searchParams.get("order") || "ASC").toUpperCase();

    let filtered = [...MOCK_STUDENTS];

    if (department) {
      filtered = filtered.filter((s) => s.department === department);
    }

    if (search) {
      filtered = filtered.filter(
        (s) =>
          s.first_name.toLowerCase().includes(search) ||
          s.last_name.toLowerCase().includes(search) ||
          s.email.toLowerCase().includes(search)
      );
    }

    // Sort
    filtered.sort((a, b) => {
      const aVal = (a as unknown as Record<string, unknown>)[sortBy];
      const bVal = (b as unknown as Record<string, unknown>)[sortBy];
      if (typeof aVal === "number" && typeof bVal === "number") {
        return order === "DESC" ? bVal - aVal : aVal - bVal;
      }
      return order === "DESC"
        ? String(bVal).localeCompare(String(aVal))
        : String(aVal).localeCompare(String(bVal));
    });

    const total = filtered.length;
    const startIndex = (page - 1) * pageSize;
    const items = filtered.slice(startIndex, startIndex + pageSize);

    return HttpResponse.json({
      items,
      total,
      page,
      page_size: pageSize,
      total_pages: Math.ceil(total / pageSize) || 1,
    });
  }),

  // Student Detail
  http.get(`${API_BASE}/students/:id`, ({ params }) => {
    const id = parseInt(params.id as string, 10);
    if (id === 1) {
      return HttpResponse.json(MOCK_STUDENT_DETAIL);
    }
    const student = MOCK_STUDENTS.find((s) => s.student_id === id);
    if (!student) {
      return HttpResponse.json(
        {
          error: {
            code: "RESOURCE_NOT_FOUND",
            message: `Student with identifier '${id}' was not found.`,
          },
        },
        { status: 404 }
      );
    }

    // Synthesize detail
    return HttpResponse.json({
      ...student,
      stats: {
        total_enrolled_courses: 5,
        gpa_marks_avg: 74.2,
        overall_attendance_pct: 82.5,
        total_courses_passed: 5,
      },
      enrollments: [
        {
          enrollment_id: 101,
          course_id: 1,
          course_code: "CS101",
          course_name: "Introduction to Computer Science",
          credits: 4,
          semester: 1,
          marks: 78.0,
          attendance_pct: 88.0,
          grade: "B",
          is_passed: true,
          is_at_risk: false,
        },
        {
          enrollment_id: 102,
          course_id: 2,
          course_code: "CS102",
          course_name: "Data Structures & Algorithms",
          credits: 4,
          semester: 2,
          marks: 72.5,
          attendance_pct: 81.0,
          grade: "B",
          is_passed: true,
          is_at_risk: false,
        },
      ],
    });
  }),

  // File Upload Ingestion
  http.post(`${API_BASE}/imports`, () => {
    return HttpResponse.json({
      import_id: 105,
      cleaning_summary: {
        rows_in: 216,
        rows_out: 200,
        duplicates_removed: 10,
        nulls_filled: 6,
        outliers_flagged: 4,
      },
    });
  }),

  // Import History Logs
  http.get(`${API_BASE}/imports`, () => {
    return HttpResponse.json(MOCK_IMPORT_LOGS);
  }),

  // Generate Report
  http.post(`${API_BASE}/reports/generate`, async ({ request }) => {
    const body = (await request.json()) as { semester?: number; department?: string; formats?: string[] };
    const repId = `rep_${Date.now()}_${body.semester || "all"}`;

    return HttpResponse.json({
      report_id: repId,
      files: (body.formats || ["pdf", "csv", "xlsx"]).map((fmt) => ({
        name: `report_${repId}.${fmt}`,
        url: `/api/v1/reports/${repId}/download/report_${repId}.${fmt}`,
      })),
      charts: [
        { name: `${repId}_department_avg_bar.png`, url: `/api/v1/charts/${repId}_department_avg_bar.png` },
        { name: `${repId}_marks_histogram.png`, url: `/api/v1/charts/${repId}_marks_histogram.png` },
        { name: `${repId}_course_boxplot.png`, url: `/api/v1/charts/${repId}_course_boxplot.png` },
        { name: `${repId}_semester_trend_line.png`, url: `/api/v1/charts/${repId}_semester_trend_line.png` },
        { name: `${repId}_attendance_vs_marks_scatter.png`, url: `/api/v1/charts/${repId}_attendance_vs_marks_scatter.png` },
        { name: `${repId}_grade_donut.png`, url: `/api/v1/charts/${repId}_grade_donut.png` },
        { name: `${repId}_dept_course_heatmap.png`, url: `/api/v1/charts/${repId}_dept_course_heatmap.png` },
      ],
    });
  }),

  // List Reports
  http.get(`${API_BASE}/reports`, () => {
    return HttpResponse.json(MOCK_REPORTS);
  }),

  // Static chart image endpoint mock (serves placeholder SVG)
  http.get("*/charts/:filename", () => {
    const svg = `
      <svg width="600" height="350" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#1e1b4b"/>
        <text x="50%" y="45%" font-family="sans-serif" font-size="20" font-weight="bold" fill="#818cf8" text-anchor="middle">
          Analytics Visualization Preview
        </text>
        <text x="50%" y="60%" font-family="sans-serif" font-size="14" fill="#a5b4fc" text-anchor="middle">
          Matplotlib High-Resolution Graphic
        </text>
      </svg>
    `;
    return new HttpResponse(svg, {
      headers: { "Content-Type": "image/svg+xml" },
    });
  }),
];
