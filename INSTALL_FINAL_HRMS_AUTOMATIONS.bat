@echo off
setlocal
cd /d "%~dp0"
echo ============================================================
echo GRSJ HRMS - Final Automation Installer
echo ============================================================
echo.
echo [1/3] Performance Tracking automation...
call "INSTALL_PERFORMANCE_AUTOMATION.bat"
echo.
echo [2/3] Attendance Rules automation...
call "INSTALL_ATTENDANCE_RULES_AUTOMATION.bat"
echo.
echo [3/3] Daily Backup automation...
call "INSTALL_DAILY_BACKUP.bat"
echo.
echo ============================================================
echo All requested HRMS automations have been invoked.
echo Review each task result above for any Windows permission errors.
echo ============================================================
pause
