@echo off
cls
echo.
echo ============================================
echo    Men's Clothes Store - Local Development
echo ============================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%

echo [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo [*] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH!
    echo Please install Node.js 18+ and try again.
    pause
    exit /b 1
)

echo [*] Stopping old processes (if any)...
taskkill /IM python.exe /F >nul 2>&1
taskkill /IM node.exe /F >nul 2>&1
timeout /t 1 /nobreak >nul

echo.
echo [1/3] Starting Backend API (port 8000)...
start "Backend API" cmd /k "cd /d %PROJECT_ROOT% && backend\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Admin Panel (port 5173)...
start "Admin Panel" cmd /k "cd /d %PROJECT_ROOT%admin && npm run dev"
timeout /t 1 /nobreak >nul

echo [3/3] Starting Client Store (port 5174)...
start "Client Store" cmd /k "cd /d %PROJECT_ROOT%client && npm run dev"

timeout /t 3 /nobreak >nul
cls
echo.
echo ============================================
echo          All Services Started!
echo ============================================
echo.
echo   Backend API:    http://localhost:8000
echo   API Docs:       http://localhost:8000/docs
echo.
echo   Admin Panel:    http://localhost:5173
echo   Client Store:   http://localhost:5174
echo.
echo ============================================
echo.
echo   Test accounts:
echo     admin / Admin1pass   (System Admin)
echo     manager / Manager1   (Manager)
echo     client / Client1     (Client)
echo.
echo   Each service runs in a separate window.
echo   Close individual windows to stop services.
echo.
pause
