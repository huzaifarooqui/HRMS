@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0CONFIGURE_DIGILOCKER.ps1"
echo.
pause
