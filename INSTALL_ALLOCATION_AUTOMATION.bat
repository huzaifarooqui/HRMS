@echo off
setlocal
set "TASKNAME=GRSJ Allocation Sync"
set "STARTBAT=%~dp0START_ALLOCATION_SYNC.bat"

echo Installing %TASKNAME% for the current Windows user...
schtasks /Delete /TN "%TASKNAME%" /F >nul 2>&1
schtasks /Create /TN "%TASKNAME%" /TR "\"%STARTBAT%\"" /SC ONLOGON /RL HIGHEST /F
if errorlevel 1 (
  echo ERROR: Could not create the scheduled task.
  echo Run this file as Administrator and try again.
  pause
  exit /b 1
)
schtasks /Run /TN "%TASKNAME%"
echo Allocation automation installed and started.
pause
