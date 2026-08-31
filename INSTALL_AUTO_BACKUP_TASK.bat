@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
  echo Please right-click this file and choose Run as administrator.
  pause
  exit /b 1
)
schtasks /create /tn "GRSJ HRMS Daily Backup" /tr "\"D:\GRSJ\GRSJ-HRMS_v1.0_Stable\BACKUP_GRSJ_DAILY.bat\"" /sc daily /st 23:30 /ru SYSTEM /rl HIGHEST /f
if %errorlevel%==0 (
  echo Automatic daily backup task installed for 11:30 PM.
) else (
  echo Could not create the backup task.
)
pause
