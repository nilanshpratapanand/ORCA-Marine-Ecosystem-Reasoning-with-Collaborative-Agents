@echo off
REM ============================================================
REM  ORCA - full installer for a clean Windows PC.
REM  Send this ONE file to a teammate. They double-click it.
REM  It installs Git / Python 3.12 / Node (if missing),
REM  downloads the repo to the Desktop, sets up backend +
REM  frontend, and offers to start the app.
REM  Safe to run again (updates + re-checks).
REM ============================================================
setlocal enabledelayedexpansion
title ORCA installer

set "REPO_URL=https://github.com/nilanshpratapanand/ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents.git"
set "DEST=%USERPROFILE%\Desktop\ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents"

echo.
echo ============================================================
echo   ORCA installer
echo   target folder: %DEST%
echo ============================================================
echo.

set NEED_RESTART=0

where git >nul 2>nul
if errorlevel 1 (
  echo [ .. ] Git not found - installing...
  winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
  set NEED_RESTART=1
) else ( echo [ ok ] Git )

py -3.12 --version >nul 2>nul
if errorlevel 1 (
  echo [ .. ] Python 3.12 not found - installing...
  winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
  set NEED_RESTART=1
) else ( echo [ ok ] Python 3.12 )

where node >nul 2>nul
if errorlevel 1 (
  echo [ .. ] Node.js not found - installing...
  winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements
  set NEED_RESTART=1
) else ( echo [ ok ] Node.js )

if "!NEED_RESTART!"=="1" (
  echo.
  echo ============================================================
  echo   Installed missing tools. Windows needs a fresh terminal to
  echo   see them. CLOSE this window, open a NEW one, and run
  echo   install-orca.bat again.
  echo ============================================================
  echo.
  pause
  exit /b 0
)

REM ---------- get the repo ----------
echo.
if exist "%DEST%\.git" (
  echo [repo] already downloaded - pulling latest changes
  cd /d "%DEST%"
  git pull
) else (
  echo [repo] downloading...
  git clone "%REPO_URL%" "%DEST%"
  if errorlevel 1 (
    echo.
    echo [ERROR] download failed. Check your internet connection.
    pause
    exit /b 1
  )
  cd /d "%DEST%"
)

REM ---------- deps (hand off to setup.bat) ----------
call "%DEST%\setup.bat" /nested
if errorlevel 1 (
  echo.
  echo [ERROR] setup step failed - see messages above.
  pause
  exit /b 1
)

REM ---------- optional: start it now ----------
echo.
choice /c YN /m "Start the app now (Y/N)"
if errorlevel 2 goto :done
call "%DEST%\run.bat"

:done
echo.
echo ============================================================
echo   All set. The project is at:
echo   %DEST%
echo.
echo   Next time just run  run.bat  in that folder.
echo   Add a free GROQ_API_KEY to backend\.env for full answers.
echo ============================================================
echo.
pause
