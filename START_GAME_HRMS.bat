@echo off
cd /d "%~dp0Server"
start "" http://127.0.0.1:5000
"..\.venv\Scripts\python.exe" app.py
pause
