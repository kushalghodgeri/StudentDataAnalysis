# Student Data Analysis & Reporting Tool — Frontend

A production-grade, responsive analytics dashboard and institutional reporting interface for academic institutions, built with **React 18**, **Vite**, **TypeScript**, **TanStack Query v5**, **Tailwind CSS**, and **Recharts**.

---

## 🌟 Key Features

- **Executive Analytics Dashboard (`/`)**:
  - High-level institutional metrics: Total Students, Total Courses, Average Marks, Pass Rate, Average Attendance, and At-Risk Count.
  - Interactive visual charts: Department Average Marks bar chart, Grade Distribution donut, Semester Performance trend line, and Attendance vs. Marks scatter plot highlighting academic thresholds.
  - Global filter bar for filtering by semester and department with synchronized URL query parameters.

- **Students Directory & Profiles (`/students`, `/students/:id`)**:
  - Server-side paginated, sortable, and searchable directory of student records.
  - Individual student profile cards with matriculation details, cumulative GPA, course enrollments table, letter grade badges, and a course performance bar chart.

- **In-Depth Analytics (`/analytics`)**:
  - **Performance Tab**: Summary statistics (mean, median, standard deviation, min, max, pass rate), Top 10 High Achievers, Bottom 10 Students needing support, and Department × Course score heatmap.
  - **Attendance Tab**: Pearson $r$ correlation coefficient badge, department-wise attendance bar chart, and identified At-Risk student registry with severity flags.
  - **Demographics Tab**: Gender distribution donut chart, department headcount breakdown, and multi-year admission cohort intake charts.

- **Automated Data Ingestion (`/import`)**:
  - Drag-and-drop CSV and Excel (`.xlsx`, `.xls`) uploader with format validation and a 15MB file size limit.
  - Live upload progress indicator.
  - Automated DataCleaner summary card reporting: Rows Ingested, Rows Processed, Duplicates Removed, Nulls Imputed (course median), and Outliers Flagged via the IQR method.
  - Complete historical import audit log.

- **Multi-Format Report Generation (`/reports`)**:
  - Custom report generator supporting semester targeting and department scoping.
  - Document export options for **PDF**, **CSV**, and **Excel (XLSX)**.
  - High-resolution Matplotlib chart gallery with an accessible lightbox modal for full-size inspection and downloading.
  - Historical generated report catalog.

- **Settings & Live Diagnostics (`/settings`)**:
  - Persistent Light and Dark mode switcher.
  - Real-time API health monitor querying `/health` for backend status, MySQL pool connectivity, and round-trip latency.
  - Architecture breakdown and mock mode documentation.

- **Zero-Backend Development with MSW**:
  - Integrated Mock Service Worker (MSW v2) providing mock data that matches the backend API specification. Switchable via `VITE_USE_MOCKS=true`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | React 18, Vite 6, TypeScript 5 (Strict Mode) |
| **Routing** | React Router v6 |
| **Data Fetching & Caching** | TanStack Query v5 |
| **HTTP Client** | Axios (configured with unified error interceptors) |
| **Styling & Design** | Tailwind CSS 3, Lucide React icons, Indigo/Slate palette |
| **Data Visualization** | Recharts (Responsive SVG Bar, Pie, Line, Scatter, and Heatmap components) |
| **File Ingestion** | react-dropzone |
| **Testing** | Vitest, React Testing Library, JSDOM |
| **Mocking** | Mock Service Worker (MSW v2) |

---

## 📁 Directory Structure

```
frontend/
├── public/
│   └── mockServiceWorker.js     # MSW Service Worker script
├── src/
│   ├── api/                     # Axios client & typed endpoint services
│   │   ├── client.ts            # Base client with interceptor error extraction
│   │   ├── health.ts            # API health check client
│   │   ├── students.ts          # Student directory & detail endpoints
│   │   ├── analytics.ts         # Overview, performance, attendance, demographics
│   │   ├── imports.ts           # Multipart upload & import history
│   │   └── reports.ts           # Generation, logs, download URLs
│   ├── components/
│   │   ├── charts/              # Reusable Recharts visualizations
│   │   │   ├── BarChartCard.tsx
│   │   │   ├── DonutCard.tsx
│   │   │   ├── HeatmapCard.tsx
│   │   │   ├── HistogramCard.tsx
│   │   │   ├── LineTrendCard.tsx
│   │   │   └── ScatterCard.tsx
│   │   ├── layout/              # Responsive shell & navigation
│   │   │   ├── Layout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Topbar.tsx
│   │   │   ├── PageHeader.tsx
│   │   │   └── ThemeToggle.tsx
│   │   └── ui/                  # Accessible UI primitives
│   │       ├── Badge.tsx
│   │       ├── DataTable.tsx
│   │       ├── EmptyState.tsx
│   │       ├── ErrorState.tsx
│   │       ├── FileDropzone.tsx
│   │       ├── FilterBar.tsx
│   │       ├── Modal.tsx
│   │       ├── Skeleton.tsx
│   │       └── StatCard.tsx
│   ├── context/
│   │   ├── ThemeContext.tsx     # Light/Dark mode with localStorage sync
│   │   └── ToastContext.tsx     # Toast notification queue
│   ├── hooks/                   # Custom TanStack Query & filter hooks
│   ├── lib/                     # Formatters, constants, and utilities
│   ├── mocks/                   # MSW handlers, browser worker, and fixtures
│   ├── pages/                   # Application views
│   ├── test/                    # Vitest setup & testing configuration
│   ├── types/                   # TypeScript interfaces matching API contract
│   ├── App.tsx                  # Root routes & query providers
│   ├── main.tsx                 # MSW initialization & DOM mount
│   └── index.css                # Tailwind directives & CSS custom properties
├── package.json
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Node.js** 18+ (Node.js 20+ recommended)
- **npm** or **pnpm**

### 2. Installation
```bash
cd frontend
npm install
```

### 3. Environment Configuration
Copy the sample environment file:
```bash
cp .env.example .env
```

Default variables in `.env`:
```env
# Backend API Base URL
VITE_API_URL=http://localhost:8000/api/v1

# Set to true to run MSW in-browser mock handlers (no backend required)
# Set to false to proxy requests to the live Python FastAPI backend
VITE_USE_MOCKS=true
```

---

## 💻 Running the Application

### Development Server (with MSW Mock Mode)
Run the Vite development server with mock mode enabled by default:
```bash
npm run dev
```
Navigate to `http://localhost:5173`. You can explore all 6 pages with realistic academic data, test CSV uploads, run reports, and preview chart lightboxes.

### Running with the Live FastAPI Backend
1. Ensure the backend is running at `http://localhost:8000`:
   ```bash
   cd ../backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. In `frontend/.env`, set:
   ```env
   VITE_API_URL=http://localhost:8000/api/v1
   VITE_USE_MOCKS=false
   ```
3. Restart or reload the frontend:
   ```bash
   npm run dev
   ```

---

## 🧪 Testing

The test suite runs with **Vitest** and **React Testing Library**:
```bash
# Run all unit and integration tests
npm run test

# Run tests in watch mode
npx vitest

# Run tests with coverage
npx vitest run --coverage
```

All 5 test suites pass cleanly:
- `Badge.test.tsx` (grade variants, style classes)
- `StatCard.test.tsx` (values, skeleton state, badges)
- `FileDropzone.test.tsx` (drop triggers, validation, progress state)
- `FilterBar.test.tsx` (URL parameter sync, active badges, clear filters)
- `formatters.test.ts` (marks formatting, percentages, dates)

---

## 📦 Production Build

Typecheck and generate an optimized production bundle:
```bash
# Check TypeScript with zero errors
npm run lint

# Build for production
npm run build

# Preview production build locally
npm run preview
```
Production assets are output to `frontend/dist/`.

---

## 🎨 Design System & Accessibility

- **Theme Support**: Seamless Light and Dark mode switching with immediate `dark` class toggling on `document.documentElement` and automatic persistence to `localStorage`.
- **Consistent Visual Hierarchy**: Clean indigo/slate design palette, rounded cards (`rounded-xl` / `rounded-2xl`), subtle shadows, and responsive layouts for desktop, tablet, and mobile.
- **Resilient States**: Every view includes loading skeletons (`<Skeleton />`, `<CardSkeleton />`, `<TableSkeleton />`), empty data states (`<EmptyState />`), and network error banners with automatic retry handlers (`<ErrorState />`).
- **Accessible Controls**: Semantic HTML `<header>`, `<aside>`, `<main>`, `<table>`, `<dialog role="dialog">`, keyboard ESC listeners for modals, and ARIA labels on all buttons.
