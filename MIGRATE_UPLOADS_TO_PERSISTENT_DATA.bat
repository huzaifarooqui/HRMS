@echo off
setlocal
cd /d "%~dp0"

set "SOURCE=%~dp0Server\uploads"
set "TARGET=%~dp0..\GRSJ-HRMS_DATA\uploads"

echo ============================================================
echo GRSJ HRMS - Preserve Employee Photos / Documents / Logo
echo ============================================================
echo Source : %SOURCE%
echo Target : %TARGET%
echo.

if not exist "%SOURCE%" (
  echo No legacy Server\uploads folder found.
  echo Nothing to migrate.
  pause
  exit /b 0
)

mkdir "%TARGET%" 2>nul
robocopy "%SOURCE%" "%TARGET%" /E /COPY:DAT /R:2 /W:1
set RC=%ERRORLEVEL%

if %RC% GEQ 8 (
  echo.
  echo ERROR: Upload migration failed. Robocopy code: %RC%
  pause
  exit /b %RC%
)

echo.
echo DONE. Runtime uploads are now preserved outside the code folder.
echo Future build replacements will not require re-uploading employee photos.
pause
exit /b 0
