# Student Data Analysis and Reporting Tool - Backend

A robust, enterprise-grade Python backend built with **FastAPI**, **MySQL 8**, **Pandas**, **NumPy**, and **Matplotlib**. Designed with a modular, layered Object-Oriented architecture, this system supports high-throughput batch ETL data ingestion, academic performance and attendance analytics, publication-ready data visualization, and automated multi-format report generation (PDF, Excel, CSV).

---

## 🏛️ Architecture Overview

The system strictly follows a layered, single-responsibility, dependency-injected design:

```mermaid
flowchart TD
    subgraph Client Layer
        WebFrontend["Frontend Web Client (React/Vite :5173)"]
        CLIClient["Headless Automation CLI (Cron/Task Scheduler)"]
    end

    subgraph API Layer ["FastAPI Routing Layer (/api/v1)"]
        HealthRoute["health.py"]
        ImportRoute["imports.py"]
        StudentRoute["students.py"]
        AnalyticsRoute["analytics.py"]
        ReportRoute["reports.py"]
    end

    subgraph Service Layer ["Pipeline & Domain Services"]
        ReportPipeline["ReportPipeline (Facade)"]
    end

    subgraph ETL & Analysis Layer
        Importer["DataImporter (Staging + Bulk Insert)"]
        Cleaner["DataCleaner (Chainable Quality Rules)"]
        PerfAnalyzer["PerformanceAnalyzer"]
        AttAnalyzer["AttendanceAnalyzer"]
        DemoAnalyzer["DemographicsAnalyzer"]
        ChartBuilder["ChartBuilder (Matplotlib Agg)"]
        SummaryReport["SummaryReport (PDF / Excel / CSV)"]
    end

    subgraph Repository Layer
        StudentRepo["StudentRepository"]
        CourseRepo["CourseRepository"]
        EnrollmentRepo["EnrollmentRepository"]
        BaseRepo["BaseRepository (No SELECT *, executemany)"]
    end

    subgraph Storage Layer ["Database & Filesystem"]
        DBConn["DatabaseConnection (MySQL Connection Pool)"]
        MySQL[("MySQL 8 Database")]
        FileStore[("File System (Charts, Reports, Raw Data)")]
    end

    WebFrontend --> API Layer
    CLIClient --> ReportPipeline
    API Layer --> ReportPipeline
    ReportPipeline --> Importer
    ReportPipeline --> Cleaner
    ReportPipeline --> PerfAnalyzer
    ReportPipeline --> AttAnalyzer
    ReportPipeline --> DemoAnalyzer
    ReportPipeline --> ChartBuilder
    ReportPipeline --> SummaryReport
    ReportPipeline --> Repository Layer
    Importer --> Repository Layer
    Repository Layer --> DBConn
    DBConn --> MySQL
    ChartBuilder --> FileStore
    SummaryReport --> FileStore
```

---

## 🚀 Key Features

- **Layered OOP Architecture**: Separation of concerns across Routers, Pipelines, Analyzers, Generators, and Repositories.
- **SQL Optimization**: Strict zero `SELECT *` enforcement, selective column projection, server-side aggregations (`AVG`, `COUNT`, `SUM`), composite indexing, covering SQL views (`vw_enrollment_detail`, `vw_student_summary`), and high-performance `executemany` bulk inserts.
- **Automated Data Cleaner**: Chainable methods stripping and title-casing names, validating emails with RFC 5322 regex, clipping impossible scores (0–100), imputing missing marks via course medians, and non-destructively flagging outliers using NumPy Interquartile Range (IQR).
- **Comprehensive Analytics**: Letter grade distribution (`pd.cut`), statistical percentiles (`np.percentile`), attendance-marks Pearson correlation (`np.corrcoef`), top/bottom performer rankings, and at-risk student detection.
- **Headless Visualization & Reporting**: 7 custom Matplotlib charts (Agg backend) and export to CSV, multi-tab Excel (`openpyxl`), and multi-page executive PDF summaries (`PdfPages`).
- **Standardized API Contract**: Pydantic v2 schemas, CORS enabled for `http://localhost:5173`, OpenAPI specification at `/docs`, and consistent `{error: {code, message}}` error responses.

---

## ⚙️ Environment Variables

Configuration is loaded via `pydantic-settings` from `.env` with fallback defaults:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DB_HOST` | `127.0.0.1` | MySQL 8 host address |
| `DB_PORT` | `3306` | MySQL 8 port |
| `DB_USER` | `root` | MySQL user |
| `DB_PASSWORD` | `rootpassword` | MySQL password |
| `DB_NAME` | `student_analytics` | Database schema name |
| `DB_POOL_NAME` | `student_pool` | Connection pool identifier |
| `DB_POOL_SIZE` | `10` | Worker connection pool capacity |
| `APP_ENV` | `development` | Environment mode (`development`, `testing`, `production`) |
| `APP_PORT` | `8000` | Uvicorn API server port |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed browser origins |
| `LOG_LEVEL` | `INFO` | Logger verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `LOG_FILE` | `backend/app.log` | Rotating log file path (10MB max, 5 backups) |
| `DATA_RAW_DIR` | `backend/data/raw` | Raw uploaded datasets |
| `DATA_PROCESSED_DIR` | `backend/data/processed` | Processed/cleaned storage |
| `OUTPUT_CHARTS_DIR` | `backend/output/charts` | Generated chart PNGs |
| `OUTPUT_REPORTS_DIR` | `backend/output/reports` | Exported PDFs, Excels, and CSVs |

---

## 📦 Setup & Installation

### Option 1: Docker Compose (Recommended for MySQL 8)

Start the MySQL 8 container with automatic schema application:

```bash
docker-compose up -d
```

### Option 2: Local Python Setup

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your MySQL credentials
   ```

4. **Initialize database schema & seed data**:
   ```bash
   python backend/scripts/seed_data.py
   ```
   *Seeds 500 students, 20 courses, ~3,000 enrollments, and generates `backend/data/raw/dirty_student_data.csv`.*

5. **Start the API Server**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
   ```
   Visit Interactive Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 REST API Specification (`/api/v1`)

| Method | Endpoint | Query / Body Parameters | Response Model | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | None | `{status, db_connected}` | API and database health check |
| `POST` | `/imports` | `multipart/form-data` (`file`) | `ImportResponse` | Ingest CSV/Excel, stage, clean, bulk persist |
| `GET` | `/imports` | `limit` (int, default: 50) | `List[ImportLogOut]` | Historical import audit logs |
| `GET` | `/students` | `page`, `page_size`, `department`, `search`, `sort_by`, `order` | `PaginatedResponse[StudentOut]` | Paginated student directory with search |
| `GET` | `/students/{id}` | Path: `id` (int) | `StudentDetailOut` | Full profile, courses, grades, GPA stats |
| `GET` | `/meta/filters` | None | `MetaFiltersOut` | Dropdown filters for departments/semesters |
| `GET` | `/analytics/overview` | `semester`, `department` | `OverviewAnalyticsOut` | High-level academic KPIs & at-risk count |
| `GET` | `/analytics/performance` | `semester`, `department` | `PerformanceAnalyticsOut` | Grade tiers, mean/median/std, rankings |
| `GET` | `/analytics/attendance` | `semester`, `department` | `AttendanceAnalyticsOut` | Dept attendance, Pearson correlation, at-risk list |
| `GET` | `/analytics/demographics`| None | `DemographicsAnalyticsOut` | Gender split, department headcount, cohorts |
| `POST` | `/reports/generate` | JSON: `{semester, department?, formats}` | `ReportResponse` | Build charts, PDF, Excel, and CSV files |
| `GET` | `/reports` | None | `List[ReportMetadata]` | Catalog of generated reports |
| `GET` | `/reports/{id}/download/{filename}` | Path: `report_id`, `filename` | File Stream | Download generated report document |
| `GET` | `/charts/{filename}` | Path: `filename` | PNG Image | Static access to generated analytical charts |

### Standardized Error Format

All error responses adhere to the unified contract:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Student with identifier '99999' was not found.",
    "details": {
      "resource": "Student",
      "id": "99999"
    }
  }
}
```

---

## 📊 Analytical Visualizations (Matplotlib Agg)

Generated by `ChartBuilder` and saved in `backend/output/charts/`:

1. `department_avg_bar.png`: Departmental average marks comparison.
2. `marks_histogram.png`: Score frequency distribution with mean, median, and pass mark thresholds.
3. `course_boxplot.png`: Marks variability across top enrolled courses.
4. `semester_trend_line.png`: Academic performance trend line across semesters.
5. `attendance_vs_marks_scatter.png`: Correlation scatter plot with linear trendline and at-risk quadrant.
6. `grade_donut.png`: Proportional donut chart of grade bands (`A`, `B`, `C`, `D`, `F`).
7. `dept_course_heatmap.png`: Two-dimensional performance heatmap across departments and courses.

---

## 💻 Headless CLI & Automation

Execute the analytics and reporting pipeline headlessly for automated reporting:

```bash
# Generate report for Semester 5 in PDF and CSV format
python -m app.cli report --semester 5 --formats pdf,csv

# Generate report for Computer Science across all semesters in PDF, Excel, and CSV
python -m app.cli report --department "Computer Science" --formats pdf,xlsx,csv

# Ingest new raw dataset via CLI
python -m app.cli ingest --file backend/data/raw/dirty_student_data.csv
```

### Automated Scheduling

#### Linux Cron Job (Run every Monday at 6:00 AM)
```cron
0 6 * * 1 cd /path/to/project && /path/to/venv/bin/python -m app.cli report --formats pdf,xlsx >> /var/log/student_reports.log 2>&1
```

#### Windows Task Scheduler (PowerShell)
```powershell
schtasks /create /tn "WeeklyStudentAnalyticsReport" /tr "python -m app.cli report --formats pdf,csv" /sc weekly /d MON /st 06:00
```

---

## 🧪 Testing & Code Coverage

Run the full pytest suite with coverage analysis:

```bash
# Run all tests with coverage report
python -m pytest backend/tests -v --cov=backend/app/etl --cov=backend/app/analysis --cov-report=term-missing
```

**Coverage Report Summary:**
- `app.etl.cleaner`: **90%**
- `app.etl.importer`: **79%**
- `app.analysis.performance`: **91%**
- `app.analysis.demographics`: **93%**
- `app.analysis.attendance`: **79%**
- **Overall Module Coverage**: **86%** (28/28 tests passing)
