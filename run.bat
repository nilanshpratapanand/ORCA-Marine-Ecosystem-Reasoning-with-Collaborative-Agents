@echo off
REM ============================================================
REM  ORCA - start backend + frontend (each in its own window)
REM  Run setup.bat once first. Close the two popup windows to stop.
REM ============================================================
cd /d "%~dp0"

if not exist backend\venv\Scripts\python.exe (
  echo Backend venv missing - run  setup.bat  first.
  pause
  exit /b 1
)

echo Starting ORCA backend...
start "ORCA backend"  cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload"

timeout /t 3 >nul

echo Starting ORCA frontend...
start "ORCA frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ============================================================
echo   Backend:  http://127.0.0.1:8000/docs
echo   Frontend: http://127.0.0.1:5173
echo   (two new windows opened - close them to stop the servers)
echo ============================================================
