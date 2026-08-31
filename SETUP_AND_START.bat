@echo off
setlocal
cd /d "%~dp0"
if not exist "Server\.env" (
  copy "Server\.env.example" "Server\.env" >nul
  echo.
  echo IMPORTANT: Open Server\.env and enter your MySQL password, then run this file again.
  notepad "Server\.env"
  pause
  exit /b
)
if not exist ".venv\Scripts\python.exe" (
  py -m venv .venv 2>nul || python -m venv .venv
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r "Server\requirements.txt"
cd Server
start "" http://127.0.0.1:5000
"..\.venv\Scripts\python.exe" app.py
pause
