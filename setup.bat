@echo off
REM ============================================================
REM  ORCA - one-time dev setup for Windows
REM  Run this from INSIDE the cloned repo folder.
REM  Safe to run again - it skips whatever is already done.
REM ============================================================
setlocal enabledelayedexpansion
set "ROOT=%~dp0"
cd /d "%ROOT%"

echo.
echo ============================================================
echo   ORCA dev setup
echo   folder: %CD%
echo ============================================================
echo.

REM ---------- must be run from inside the repo ----------
if not exist "%ROOT%backend\requirements.txt" (
  echo [ERROR] Can't find backend\requirements.txt next to this script.
  echo         You are running setup.bat from the wrong place, or from a
  echo         loose copy of the file.
  echo.
  echo   Fix: clone the repo and run the setup.bat that is INSIDE it:
  echo     git clone https://github.com/nilanshpratapanand/ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents.git
  echo     cd ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents
  echo     setup.bat
  echo.
  pause
  exit /b 1
)

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
echo [backend] checking virtual environment (needs Python 3.12)...
cd /d "%ROOT%backend"

set REBUILD=0
if exist "venv\Scripts\python.exe" (
  "venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info[:2]==(3,12) else 1)" 2>nul
  if errorlevel 1 (
    echo [backend] existing venv is not Python 3.12 - rebuilding it
    rmdir /s /q venv
    set REBUILD=1
  ) else (
    echo [backend] venv OK
  )
) else (
  set REBUILD=1
)
if "!REBUILD!"=="1" (
  py -3.12 -m venv venv
)

call "venv\Scripts\activate.bat"
echo [backend] installing Python packages (this can take a minute)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo [ERROR] pip install failed. Delete backend\venv and run setup.bat again.
  cd /d "%ROOT%"
  pause
  exit /b 1
)
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo [backend] created backend\.env  -^>  open it and paste a free GROQ_API_KEY
  echo           ^(https://console.groq.com/keys ; optional, app runs without^)
)
cd /d "%ROOT%"

REM ---------- frontend ----------
echo.
echo [frontend] installing npm packages...
cd /d "%ROOT%frontend"
call npm install
if errorlevel 1 (
  echo.
  echo [ERROR] npm install failed. Check your internet and run setup.bat again.
  cd /d "%ROOT%"
  pause
  exit /b 1
)
cd /d "%ROOT%"

echo.
echo ============================================================
echo   Setup complete.
echo.
echo   Start everything:   run.bat
echo   Backend docs:       http://127.0.0.1:8000/docs
echo   Frontend UI:        http://127.0.0.1:5173
echo ============================================================
echo.
if /i not "%~1"=="/nested" pause
