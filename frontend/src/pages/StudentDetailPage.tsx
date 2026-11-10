import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Mail,
  Building2,
  Calendar,
  BookOpen,
  Award,
  Clock,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import { StatCard } from "../components/ui/StatCard";
import { Badge, getGradeBadgeVariant } from "../components/ui/Badge";
import { DataTable, ColumnDef } from "../components/ui/DataTable";
import { BarChartCard } from "../components/charts/BarChartCard";
import { ErrorState } from "../components/ui/ErrorState";
import { CardSkeleton } from "../components/ui/Skeleton";
import { useStudentDetail } from "../hooks/useStudentDetail";
import { formatMarks, formatPercent, formatDate } from "../lib/formatters";
import { StudentEnrollment } from "../types/student";

export const StudentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const studentId = id ? parseInt(id, 10) : 0;

  const { data, isLoading, isError, refetch } = useStudentDetail(studentId);

  if (isError) {
    return (
      <div className="space-y-6">
        <button
          onClick={() => navigate("/students")}
          className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Students
        </button>
        <ErrorState
          title="Student Not Found"
          message={`Unable to load details for student #${id}.`}
          onRetry={refetch}
        />
      </div>
    );
  }

  const student = data?.student || data;
  const stats = data?.stats;
  const enrollments = data?.enrollments || [];

  const avgMarks = stats?.avg_marks ?? stats?.gpa_marks_avg ?? 0;
  const avgAttendance = stats?.avg_attendance ?? stats?.overall_attendance_pct ?? 0;
  const totalCourses = stats?.total_courses ?? stats?.total_enrolled_courses ?? enrollments.length;

  // Prepare marks per course data
  const marksPerCourseData = enrollments.map((e) => ({
    name: e.course_name,
    value: Number(e.marks ?? 0),
  }));

  const enrollmentColumns: ColumnDef<StudentEnrollment>[] = [
    {
      key: "course_name",
      header: "Course Name",
      render: (e) => <span className="font-medium text-slate-900 dark:text-slate-100">{e.course_name}</span>,
    },
    {
      key: "semester",
      header: "Semester",
      className: "w-24 text-center",
      render: (e) => <span className="text-xs font-mono">Sem {e.semester}</span>,
    },
    {
      key: "marks",
      header: "Marks",
      className: "w-28",
      render: (e) => (
        <span className="font-semibold text-slate-900 dark:text-slate-100">
          {formatMarks(e.marks)}
        </span>
      ),
    },
    {
      key: "grade",
      header: "Grade",
      className: "w-24",
      render: (e) => {
        if (e.marks === null || e.marks === undefined) return <span>-</span>;
        const m = Number(e.marks);
        const grade =
          m >= 80 ? "A" : m >= 70 ? "B" : m >= 60 ? "C" : m >= 40 ? "D" : "F";
        return <Badge variant={getGradeBadgeVariant(grade)}>{grade}</Badge>;
      },
    },
    {
      key: "attendance_pct",
      header: "Attendance",
      className: "w-28",
      render: (e) => (
        <span
          className={
            e.attendance_pct !== null && e.attendance_pct !== undefined && Number(e.attendance_pct) < 75
              ? "text-rose-600 dark:text-rose-400 font-bold"
              : "text-slate-700 dark:text-slate-300"
          }
        >
          {formatPercent(e.attendance_pct)}
        </span>
      ),
    },
    {
      key: "status",
      header: "Status",
      className: "w-28",
      render: (e) => {
        const m = Number(e.marks ?? 0);
        const attVal = Number(e.attendance_pct ?? 0);
        return m >= 40 && attVal >= 75 ? (
          <Badge variant="success" size="sm">
            Good Standing
          </Badge>
        ) : (
          <Badge variant="danger" size="sm">
            At-Risk
          </Badge>
        );
      },
    },
  ];

  return (
    <div className="space-y-6">
      {/* Back button */}
      <div>
        <button
          onClick={() => navigate("/students")}
          className="inline-flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Students Directory
        </button>
      </div>

      {isLoading ? (
        <CardSkeleton />
      ) : student ? (
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200/80 dark:border-slate-700/80 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-5">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 to-indigo-500 flex items-center justify-center text-white text-xl font-bold shadow-md shadow-indigo-500/20">
              {student.first_name ? student.first_name[0] : "S"}
              {student.last_name ? student.last_name[0] : ""}
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-slate-50">
                  {student.first_name} {student.last_name}
                </h2>
                <Badge variant="primary" size="sm">
                  #{student.student_id}
                </Badge>
              </div>

              <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 mt-2 text-xs text-slate-500 dark:text-slate-400">
                <span className="flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5" />
                  {student.email}
                </span>
                <span className="flex items-center gap-1.5">
                  <Building2 className="w-3.5 h-3.5" />
                  {student.department}
                </span>
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5" />
                  Admitted {student.admission_year}
                </span>
                {student.dob && (
                  <span>DOB: {formatDate(student.dob)}</span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {avgAttendance >= 75 && avgMarks >= 40 ? (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 text-xs font-semibold">
                <CheckCircle2 className="w-4 h-4" />
                Regular Active
              </div>
            ) : (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800 text-xs font-semibold">
                <AlertTriangle className="w-4 h-4" />
                Attention Required
              </div>
            )}
          </div>
        </div>
      ) : null}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Courses Enrolled"
          value={totalCourses}
          icon={<BookOpen className="w-5 h-5" />}
          subtitle="Total course units"
          variant="indigo"
          isLoading={isLoading}
        />
        <StatCard
          title="Overall Average"
          value={formatMarks(avgMarks)}
          icon={<Award className="w-5 h-5" />}
          subtitle="Cumulative score"
          variant="emerald"
          isLoading={isLoading}
        />
        <StatCard
          title="Overall Attendance"
          value={formatPercent(avgAttendance)}
          icon={<Clock className="w-5 h-5" />}
          subtitle="Campus presence"
          variant={avgAttendance < 75 ? "rose" : "purple"}
          isLoading={isLoading}
        />
        <StatCard
          title="Academic Standing"
          value={avgMarks >= 40 ? "Passing" : "Failing"}
          icon={<CheckCircle2 className="w-5 h-5" />}
          subtitle="Threshold >= 40"
          variant={avgMarks >= 40 ? "emerald" : "rose"}
          isLoading={isLoading}
        />
      </div>

      {/* Marks Per Course Bar Chart */}
      <BarChartCard
        title="Performance Across Enrolled Courses"
        subtitle="Individual course scores vs 100 maximum"
        data={marksPerCourseData}
        yDomain={[0, 100]}
        isLoading={isLoading}
      />

      {/* Enrollments Table */}
      <div className="space-y-3">
        <h3 className="text-base font-semibold text-slate-800 dark:text-slate-100">
          Course Enrollments & Academic Records
        </h3>
        <DataTable
          columns={enrollmentColumns}
          data={enrollments}
          keyExtractor={(e, idx) => `${e.course_name}-${e.semester}-${idx}`}
          isLoading={isLoading}
          emptyTitle="No course enrollments"
          emptyDescription="This student is not enrolled in any registered courses."
        />
      </div>
    </div>
  );
};
