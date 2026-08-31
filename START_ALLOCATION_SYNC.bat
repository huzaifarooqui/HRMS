@echo off
setlocal
cd /d "%~dp0Server"

set "LOCKFILE=%TEMP%\GRSJ_Allocation_Sync.lock"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p=Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object {$_.CommandLine -like '*allocation_sync.py*'}; if($p){exit 10}else{exit 0}"
if %errorlevel%==10 exit /b 0

echo [%date% %time%] Starting GRSJ Performance Tracking Auto-Sync...
"..\.venv\Scripts\python.exe" allocation_sync.py
