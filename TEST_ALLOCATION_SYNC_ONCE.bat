@echo off
cd /d "%~dp0Server"
"..\.venv\Scripts\python.exe" allocation_sync_once.py
echo.
pause
