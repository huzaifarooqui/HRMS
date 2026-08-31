@echo off
setlocal
cd /d "%~dp0"

echo ==========================================================
echo   GRSJ HRMS - Digital ID Browser PDF Installer
echo ==========================================================
echo.

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  echo Extract this ZIP inside your GRSJ-HRMS_v1.0_Stable folder.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" "INSTALL_DIGITAL_ID_BROWSER_PDF.py"
if errorlevel 1 (
  echo.
  echo Installation failed. Read the message above.
  pause
  exit /b 1
)

echo.
echo Patch complete. Restart the HRMS server, then test Digital ID ^> Download PDF.
pause
