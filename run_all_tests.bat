@echo off
echo ========================================================
echo   Running Backend & Frontend Test Suites
echo ========================================================
echo.

set BACKEND_DIR=%~dp0backend
set FRONTEND_DIR=%~dp0frontend

echo [1/2] Running Backend Tests (pytest)...
cd /d %BACKEND_DIR%
if exist "%BACKEND_DIR%\.venv\Scripts\activate.bat" (
    call "%BACKEND_DIR%\.venv\Scripts\activate.bat"
)
python -m pytest -v --tb=short
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend tests failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Running Frontend Tests (Vitest)...
cd /d %FRONTEND_DIR%
call npm run test
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend tests failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2+] Running Frontend Type Check (tsc)...
call npm run lint
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend TypeScript check failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo   ALL TESTS PASSED SUCCESSFULLY! (Backend + Frontend)
echo ========================================================
pause
