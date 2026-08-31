@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo GRSJ Performance Tracking - Production Activation
echo ============================================================
echo.

if not exist "Server\.env" (
  echo ERROR: Server\.env not found.
  echo Keep your production .env with DB_NAME=game_db before running this.
  pause
  exit /b 1
)

findstr /I /C:"DB_NAME=game_db_test" "Server\.env" >nul
if %errorlevel%==0 (
  echo ERROR: Production .env still points to game_db_test.
  echo Change it to DB_NAME=game_db first.
  pause
  exit /b 1
)

echo [1/4] Installing/updating Python requirements...
".venv\Scripts\python.exe" -m pip install -r "Server\requirements.txt"
if errorlevel 1 goto :fail

echo.
echo [2/4] Running one-time Performance Tracking sync...
cd /d "%~dp0Server"
"..\.venv\Scripts\python.exe" allocation_sync_once.py
if errorlevel 1 goto :fail
cd /d "%~dp0"

echo.
echo [3/4] Installing automatic logon task...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALL_PERFORMANCE_AUTOMATION.ps1"
if errorlevel 1 goto :fail

echo.
echo [4/4] Checking task...
schtasks /query /tn "GRSJ Performance Tracking Sync" /v /fo list

echo.
echo ============================================================
echo DONE.
echo Performance Tracking has been synced once and automation
echo is installed for future Windows logons.
echo ============================================================
pause
exit /b 0

:fail
echo.
echo ERROR: Activation did not complete.
echo Check Server\allocation_sync.log for details.
pause
exit /b 1
