@echo off
cd /d "%~dp0Server"
"..\.venv\Scripts\python.exe" backup_hrms.py
pause
