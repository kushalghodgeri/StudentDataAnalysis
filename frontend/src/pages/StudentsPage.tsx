import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, X, ChevronRight } from "lucide-react";
import { PageHeader } from "../components/layout/PageHeader";
import { DataTable, ColumnDef } from "../components/ui/DataTable";
import { Badge } from "../components/ui/Badge";
import { ErrorState } from "../components/ui/ErrorState";
import { useStudents } from "../hooks/useStudents";
import { useMetaFilters } from "../hooks/useMetaFilters";
import { Student } from "../types/student";
import { GENDER_COLORS } from "../lib/constants";

export const StudentsPage: React.FC = () => {
  const navigate = useNavigate();

  // Local search and filter states
  const [searchInput, setSearchInput] = useState("");
  const [selectedDept, setSelectedDept] = useState<string>("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [sortBy, setSortBy] = useState<string>("student_id");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const { data: meta } = useMetaFilters();
  const { data, isLoading, isError, refetch } = useStudents({
    page,
    page_size: pageSize,
    department: selectedDept || undefined,
    search: searchInput || undefined,
    sort_by: sortBy,
    order: sortOrder,
  });

  const handleSortChange = (colKey: string) => {
    if (sortBy === colKey) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(colKey);
      setSortOrder("asc");
    }
  };

  const columns: ColumnDef<Student>[] = [
    {
      key: "student_id",
      header: "ID",
      sortable: true,
      className: "w-20 font-mono text-xs text-slate-500",
      render: (s) => <span>#{s.student_id}</span>,
    },
    {
      key: "name",
      header: "Student Name",
      sortable: true,
      render: (s) => (
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center text-slate-600 dark:text-slate-300 font-semibold text-xs">
            {s.first_name[0]}
            {s.last_name[0]}
          </div>
          <div>
            <p className="font-medium text-slate-900 dark:text-slate-100">
              {s.first_name} {s.last_name}
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400">{s.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: "department",
      header: "Department",
      sortable: true,
      render: (s) => (
        <Badge variant="default" size="sm">
          {s.department}
        </Badge>
      ),
    },
    {
      key: "gender",
      header: "Gender",
      sortable: true,
      className: "w-24 text-center",
      render: (s) => (
        <span
          className="inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-semibold text-white"
          style={{ backgroundColor: GENDER_COLORS[s.gender] || "#6366f1" }}
        >
          {s.gender}
        </span>
      ),
    },
    {
      key: "admission_year",
      header: "Admission Year",
      sortable: true,
      className: "w-32 font-mono text-xs text-slate-600 dark:text-slate-300",
      render: (s) => <span>{s.admission_year}</span>,
    },
    {
      key: "actions",
      header: "",
      className: "w-16 text-right",
      render: (s) => (
        <button
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/students/${s.student_id}`);
          }}
          className="p-1 rounded-md text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
          aria-label={`View details for ${s.first_name} ${s.last_name}`}
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Students Directory"
        subtitle="Search, filter, and review comprehensive student academic profiles."
      />

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200/80 dark:border-slate-700/80 shadow-sm">
        {/* Search input */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => {
              setSearchInput(e.target.value);
              setPage(1);
            }}
            placeholder="Search by student name or email..."
            className="w-full pl-9 pr-8 py-2 text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
          />
          {searchInput && (
            <button
              onClick={() => {
                setSearchInput("");
                setPage(1);
              }}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              aria-label="Clear search"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Department Filter */}
        <div className="flex items-center gap-2">
          <label htmlFor="dept-select" className="text-xs font-medium text-slate-500 dark:text-slate-400 whitespace-nowrap">
            Department:
          </label>
          <select
            id="dept-select"
            value={selectedDept}
            onChange={(e) => {
              setSelectedDept(e.target.value);
              setPage(1);
            }}
            className="text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Departments</option>
            {meta?.departments.map((dept) => (
              <option key={dept} value={dept}>
                {dept}
              </option>
            ))}
          </select>
        </div>
      </div>

      {isError && (
        <ErrorState
          title="Failed to load students"
          message="Could not retrieve student list from the server."
          onRetry={refetch}
        />
      )}

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={data?.items || []}
        keyExtractor={(s) => s.student_id}
        isLoading={isLoading}
        emptyTitle="No students found"
        emptyDescription="No students matched your search criteria or department filter."
        onRowClick={(s) => navigate(`/students/${s.student_id}`)}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={handleSortChange}
        page={page}
        pageSize={pageSize}
        total={data?.total || 0}
        onPageChange={(p) => setPage(p)}
        onPageSizeChange={(sz) => {
          setPageSize(sz);
          setPage(1);
        }}
      />
    </div>
  );
};
