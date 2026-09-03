@echo off
REM ============================================================
REM  ORCA - start backend + frontend (each in its own window)
REM  Run this from INSIDE the cloned repo folder, after setup.bat.
REM  Close the two popup windows to stop the servers.
REM ============================================================
set "ROOT=%~dp0"
cd /d "%ROOT%"

if not exist "%ROOT%backend\requirements.txt" (
  echo Run run.bat from inside the cloned repo folder, not a loose copy.
  pause
  exit /b 1
)
if not exist "%ROOT%backend\venv\Scripts\python.exe" (
  echo Backend venv missing - run  setup.bat  first.
  pause
  exit /b 1
)

echo Starting ORCA backend...
start "ORCA backend"  cmd /k "cd /d "%ROOT%backend" && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload"

timeout /t 3 >nul

echo Starting ORCA frontend...
start "ORCA frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

echo.
echo ============================================================
echo   Backend:  http://127.0.0.1:8000/docs
echo   Frontend: http://127.0.0.1:5173
echo   (two new windows opened - close them to stop the servers)
echo ============================================================
