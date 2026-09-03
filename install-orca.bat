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

REM Some installers put tools on disk but not on this shell's PATH. Add the
REM usual locations up front so we don't try to "install" something that's
REM already here (that was causing an install -> restart -> install loop).
set "PATH=%PATH%;%ProgramFiles%\Git\cmd;%ProgramFiles%\Git\bin;%LOCALAPPDATA%\Programs\Git\cmd;%ProgramFiles%\nodejs;%LOCALAPPDATA%\Programs\nodejs;%APPDATA%\npm"

set NEED_RESTART=0
set PATH_PROBLEM=0

call :ensure git   "Git.Git"            "Git"
call :ensure node  "OpenJS.NodeJS.LTS"  "Node.js"

REM Python: the "py" launcher finds versions even when python.exe isn't on PATH.
py -3.12 --version >nul 2>nul
if errorlevel 1 (
  echo [ .. ] Python 3.12 not found - installing...
  winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
  py -3.12 --version >nul 2>nul && ( echo [ ok ] Python 3.12 ) || set NEED_RESTART=1
) else ( echo [ ok ] Python 3.12 )

if "!PATH_PROBLEM!"=="1" (
  echo.
  echo ============================================================
  echo   A tool is installed but not on your PATH, and I couldn't
  echo   find it in the usual folders. Re-install it from the official
  echo   site ^(the installer adds it to PATH^), then run this again:
  echo     Git :  https://git-scm.com/download/win
  echo     Node:  https://nodejs.org   ^(LTS^)
  echo ============================================================
  echo.
  pause
  exit /b 1
)

if "!NEED_RESTART!"=="1" (
  echo.
  echo ============================================================
  echo   Installed missing tools. CLOSE this window, open a NEW one,
  echo   and run install-orca.bat again so PATH refreshes.
  echo ============================================================
  echo.
  pause
  exit /b 0
)

goto :deps_done

REM ---- :ensure <command> <winget-id> <label> -------------------------------
:ensure
where %~1 >nul 2>nul
if not errorlevel 1 ( echo [ ok ] %~3 & exit /b 0 )
echo [ .. ] %~3 not found - installing...
winget install --id %~2 -e --accept-source-agreements --accept-package-agreements
REM re-add likely paths and re-check (winget won't refresh this shell's PATH)
set "PATH=%PATH%;%ProgramFiles%\Git\cmd;%LOCALAPPDATA%\Programs\Git\cmd;%ProgramFiles%\nodejs;%LOCALAPPDATA%\Programs\nodejs"
where %~1 >nul 2>nul
if not errorlevel 1 ( echo [ ok ] %~3 ^(found after install^) & exit /b 0 )
winget list --id %~2 -e >nul 2>nul
if not errorlevel 1 (
  echo [warn] %~3 is installed but not on PATH
  set PATH_PROBLEM=1
) else (
  set NEED_RESTART=1
)
exit /b 0

:deps_done

REM ---------- get the repo ----------
echo.
set REPO_OK=0
if exist "%DEST%\.git" (
  git -C "%DEST%" rev-parse --is-inside-work-tree >nul 2>nul && set REPO_OK=1
)

if "!REPO_OK!"=="1" (
  echo [repo] already downloaded - pulling latest changes
  git -C "%DEST%" pull --ff-only
) else (
  if exist "%DEST%\backend\app\main.py" (
    echo.
    echo [ERROR] "%DEST%"
    echo         has project files but is not a working git checkout
    echo         ^(a past download probably failed half-way^).
    echo         Rename or delete that folder, then run this again.
    echo.
    pause
    exit /b 1
  )
  if exist "%DEST%" (
    echo [repo] removing incomplete download...
    rmdir /s /q "%DEST%"
  )
  echo [repo] downloading...
  git clone "%REPO_URL%" "%DEST%"
  if errorlevel 1 (
    echo.
    echo [ERROR] download failed. Check your internet connection.
    pause
    exit /b 1
  )
)

if not exist "%DEST%\setup.bat" (
  echo.
  echo [ERROR] download finished but setup.bat is missing - the clone is
  echo         incomplete. Delete "%DEST%" and run this again.
  pause
  exit /b 1
)
cd /d "%DEST%"

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
