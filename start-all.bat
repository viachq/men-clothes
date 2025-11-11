@echo off
echo ============================================
echo Starting Food Delivery Application
echo ============================================
echo.

echo [1/3] Starting Backend (port 8000)...
start cmd /k "cd /d %~dp0 && uv run uvicorn backend.main:app --reload --port 8000"
timeout /t 2 /nobreak >nul

echo [2/3] Starting Admin Panel (port 5173)...
start cmd /k "cd /d %~dp0admin && npm run dev"
timeout /t 2 /nobreak >nul

echo [3/3] Starting Client Site (port 5174)...
start cmd /k "cd /d %~dp0client && npm run dev"
timeout /t 2 /nobreak >nul

echo.
echo ============================================
echo All services started!
echo ============================================
echo.
echo Backend API:      http://localhost:8000/docs
echo Admin Panel:      http://localhost:5173
echo Client Site:      http://localhost:5174
echo.
echo Press any key to exit (services will keep running)...
pause >nul

