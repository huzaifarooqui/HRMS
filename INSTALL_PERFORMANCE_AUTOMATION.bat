@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALL_PERFORMANCE_AUTOMATION.ps1"
if errorlevel 1 (
  echo.
  echo Installation failed. Run this BAT as Administrator.
  pause
  exit /b 1
)
echo.
pause
