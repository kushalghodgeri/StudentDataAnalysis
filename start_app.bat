@echo off
echo ========================================================
echo   Student Data Analysis and Reporting Tool - Full Stack
echo ========================================================
echo.

set BACKEND_DIR=%~dp0backend
set FRONTEND_DIR=%~dp0frontend

echo [1/2] Launching FastAPI Backend on port 8000...
if exist "%BACKEND_DIR%\.venv\Scripts\activate.bat" (
    start "Backend Server (FastAPI :8000)" cmd /k "cd /d %BACKEND_DIR% && call .venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
) else (
    start "Backend Server (FastAPI :8000)" cmd /k "cd /d %BACKEND_DIR% && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
)

echo [2/2] Launching Vite Frontend on port 5173...
start "Frontend App (Vite :5173)" cmd /k "cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo ========================================================
echo   Both services launched in separate windows!
echo   - Frontend: http://localhost:5173
echo   - Backend:  http://localhost:8000/docs
echo ========================================================
echo.
pause
