# Student Data Analysis and Reporting Tool

A production-grade, full-stack institutional analytics and reporting platform built with **Python 3.11+ / FastAPI** and **React 18 / TypeScript / Vite**.

---

## 🏛️ System Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │               Web Browser (UI)               │
                    │        http://localhost:5173 (React 18)      │
                    └──────────────────────┬───────────────────────┘
                                           │
                        REST API (HTTP / JSON / Multipart)
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │           Backend API (FastAPI)              │
                    │        http://localhost:8000/api/v1          │
                    └──────┬───────────────┬───────────────┬───────┘
                           │               │               │
                           ▼               ▼               ▼
                    ┌────────────┐  ┌─────────────┐  ┌─────────────┐
                    │    ETL     │  │  Analytics  │  │  Reporting  │
                    │  Pipeline  │  │   Engine    │  │   Engine    │
                    │ (Cleaning, │  │ (Pandas /   │  │ (PDF/CSV/   │
                    │  IQR, Med) │  │   NumPy)    │  │ Matplotlib) │
                    └──────┬─────┘  └──────┬──────┘  └──────┬──────┘
                           │               │                │
                           └───────────────┼────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │          Repository Layer & SQL Pool         │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │            MySQL 8 Database                  │
                    │  (Indexed Tables, Views, Parameterized SQL)  │
                    └──────────────────────────────────────────────┘
```

---

## 🚀 Tech Stack

### Backend (`/backend`)
- **Runtime & Framework**: Python 3.11+, FastAPI, Uvicorn (ASGI)
- **Database & Pooling**: MySQL 8, `mysql-connector-python` connection pool, SQLAlchemy (`read_sql`)
- **Data Science & Analytics**: Pandas, NumPy, Matplotlib (`Agg` headless backend)
- **Validation & Serialization**: Pydantic v2, Python-dotenv
- **Document Generation**: ReportLab (`PdfPages`), openpyxl (Excel), CSV
- **Testing & Quality**: pytest, pytest-cov, pytest-asyncio, Faker (synthetic seed data)

### Frontend (`/frontend`)
- **Runtime & Framework**: React 18, Vite 6, TypeScript 5 (Strict Mode)
- **Routing & Navigation**: React Router v6
- **Data Caching & Invalidation**: TanStack Query v5
- **HTTP Client**: Axios with centralized error interceptors
- **Styling & UI**: Tailwind CSS 3, Lucide React icons, Indigo/Slate palette
- **Data Visualization**: Recharts (Responsive SVG Bar, Donut, Line, Scatter, and Heatmap cards)
- **File Ingestion**: react-dropzone with validation and live progress animation
- **Testing & Mocking**: Vitest, React Testing Library, JSDOM, Mock Service Worker (MSW v2)

---

## 🌟 Key Capabilities

### 1. Executive Institutional Dashboard (`/`)
- Real-time stat cards: Total Students, Total Courses, Average Marks, Pass Rate ($\ge 40$), Average Attendance, and At-Risk Count.
- Interactive visualizations: Department average marks bar chart, letter grade distribution donut, multi-semester performance trend line, and attendance vs. marks scatter plot highlighting academic vulnerability zones.
- Global filter bar for semester and department filtering with persistent URL search parameters.

### 2. Student Directory & Profiles (`/students`, `/students/:id`)
- Server-side paginated, sortable, and searchable student directory.
- Detailed academic profiles displaying matriculation details, cumulative GPA, course enrollments, letter grades, and attendance standing.

### 3. Comprehensive Analytics (`/analytics`)
- **Academic Performance**: Descriptive statistics (mean, median, standard deviation, min, max, pass rate), Top 10 High Achievers, Bottom 10 Students needing support, and Department $\times$ Course score heatmap.
- **Attendance Intelligence**: Pearson $r$ correlation coefficient between attendance and marks, department-wise attendance bar chart, and identified At-Risk registry with severity classifications.
- **Cohort Demographics**: Gender representation donut, department headcount bar chart, and matriculation cohort progression.

### 4. Automated ETL & Data Cleaning (`/import`)
- Drag-and-drop CSV and Excel (`.xlsx`, `.xls`) ingestion with 15MB file size limits.
- Automated `DataCleaner` pipeline:
  - Deduplication by email and student ID.
  - Name title-casing, email normalization, and regex validation.
  - Out-of-bounds score clipping to $[0, 100]$.
  - Missing marks imputation using the target course median.
  - Outlier detection via the Interquartile Range (IQR, $1.5 \times \text{IQR}$) in an `is_outlier` flag column.
- Visual Cleaning Summary card reporting rows in, rows out, duplicates removed, nulls imputed, and outliers flagged.
- Audit history table logging every import event.

### 5. Multi-Format Reporting (`/reports`)
- Scope reports by semester and optional department.
- Export to **PDF Summary**, **CSV**, and **Excel (XLSX)**.
- Publication-quality Matplotlib chart gallery with an accessible lightbox modal for full-size inspection and downloading.

### 6. Settings & System Diagnostics (`/settings`)
- Light and Dark mode switcher persisted in `localStorage`.
- Real-time backend `/health` monitoring checking MySQL connection status and response latency.

---

## ⚡ Quick Start

### Option 1: Docker Compose (All-in-One)

Start MySQL 8, the FastAPI backend, and the React frontend in containers:

```bash
docker compose up --build
```

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MySQL Database**: `localhost:3306` (database: `student_analytics`, user: `root`, password: `rootpassword`)

---

### Option 2: Local Development Setup

#### 1. Start MySQL 8
Ensure MySQL 8 is running locally or via Docker:
```bash
docker compose up -d mysql
```

#### 2. Setup and Run the Backend
```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # On Windows
# source .venv/bin/activate # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Initialize database schema and seed synthetic data
python scripts/seed_data.py

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

#### 3. Setup and Run the Frontend
```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env

# Run Vite dev server in MSW mock mode (or live backend)
npm run dev
```

Frontend application is available at [http://localhost:5173](http://localhost:5173).

---

## 🧪 Testing & Verification

### Backend Tests (pytest)
```bash
cd backend
pytest -v --cov=app --cov-report=term-missing
```
**Results**: 28 passed, 0 failed, **86% code coverage**.

### Frontend Tests (Vitest)
```bash
cd frontend
npm run test
```
**Results**: 5 test suites passed, 15 tests passed, 0 errors.

### TypeScript Typecheck & Build
```bash
cd frontend
npm run lint    # Runs tsc -b --noEmit (0 errors)
npm run build   # Builds production bundle to frontend/dist/
```

---

## 📁 Repository Structure

```
.
├── backend/                     # Python FastAPI application
│   ├── app/
│   │   ├── main.py              # Application entrypoint & CORS
│   │   ├── api/routes/          # API endpoints (health, students, analytics, imports, reports)
│   │   ├── analysis/            # Performance, Attendance, Demographics analyzers
│   │   ├── etl/                 # Importer & DataCleaner pipelines
│   │   ├── reporting/           # Matplotlib ChartBuilder & multi-format reports
│   │   ├── db/                  # Connection pool, schema.sql, repositories
│   │   └── models/              # Pydantic v2 schemas & dataclasses
│   ├── scripts/seed_data.py     # Faker data generator (500 students, 3000 enrollments, dirty samples)
│   ├── tests/                   # Pytest unit & integration test suite
│   ├── requirements.txt
│   └── README.md
├── frontend/                    # React 18 / Vite / TypeScript application
│   ├── src/
│   │   ├── api/                 # Axios clients
│   │   ├── components/          # Recharts visualizations, layout, and UI primitives
│   │   ├── hooks/               # TanStack Query custom hooks
│   │   ├── pages/               # Dashboard, Students, Detail, Analytics, Import, Reports, Settings
│   │   ├── mocks/               # MSW v2 mock worker & fixtures
│   │   └── __tests__/           # Vitest component test suites
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── README.md
├── docker-compose.yml           # Multi-container orchestration
└── README.md                    # Root project documentation
```
