@echo off
cd /d "D:\GRSJ\GRSJ-HRMS_v1.0_Stable\Server"
"D:\GRSJ\GRSJ-HRMS_v1.0_Stable\.venv\Scripts\python.exe" backup_production.py >> "D:\GRSJ\GRSJ-HRMS_v1.0_Stable\Backups\backup.log" 2>&1
