@echo off
REM ============================================================
REM  ORCA - one-time dev setup for Windows
REM  Double-click this file, or run  setup.bat  from a terminal.
REM  Safe to run again - it skips whatever is already done.
REM ============================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================================
echo   ORCA dev setup
echo ============================================================
echo.

set NEED_RESTART=0

REM ---------- prerequisites (installed via winget if missing) ----------
where git >nul 2>nul
if errorlevel 1 (
  echo [ .. ] Git not found - installing...
  winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
  set NEED_RESTART=1
) else (
  echo [ ok ] Git
)

py -3.12 --version >nul 2>nul
if errorlevel 1 (
  echo [ .. ] Python 3.12 not found - installing...
  winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
  set NEED_RESTART=1
) else (
  echo [ ok ] Python 3.12
)

where node >nul 2>nul
if errorlevel 1 (
  echo [ .. ] Node.js not found - installing...
  winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements
  set NEED_RESTART=1
) else (
  echo [ ok ] Node.js
)

if "!NEED_RESTART!"=="1" (
  echo.
  echo ============================================================
  echo   Installed missing tools.
  echo   CLOSE this window, open a NEW one, and run setup.bat again
  echo   so Windows picks up the new PATH.
  echo ============================================================
  echo.
  pause
  exit /b 0
)

REM ---------- backend ----------
echo.
echo [backend] setting up virtual environment (Python 3.12)...
pushd backend
if exist venv\Scripts\python.exe (
  echo [backend] venv already exists - reusing
) else (
  py -3.12 -m venv venv
)
call venv\Scripts\activate.bat
echo [backend] installing Python packages (this can take a minute)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo [ERROR] pip install failed. Most common cause: the venv was made with
  echo         the wrong Python. Delete backend\venv and run setup.bat again.
  popd
  pause
  exit /b 1
)
if not exist .env (
  copy .env.example .env >nul
  echo [backend] created backend\.env  -^>  open it and paste a free GROQ_API_KEY
  echo           ^(get one at https://console.groq.com/keys ; optional, app runs without^)
)
popd

REM ---------- frontend ----------
echo.
echo [frontend] installing npm packages...
pushd frontend
call npm install
if errorlevel 1 (
  echo.
  echo [ERROR] npm install failed. Check your internet and try setup.bat again.
  popd
  pause
  exit /b 1
)
popd

echo.
echo ============================================================
echo   Setup complete.
echo.
echo   Start everything:   run.bat
echo   Backend docs:       http://127.0.0.1:8000/docs
echo   Frontend UI:        http://127.0.0.1:5173
echo ============================================================
echo.
pause
