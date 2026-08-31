@echo off
cd /d "%~dp0Server"
"..\.venv\Scripts\python.exe" attendance_rules_sync.py
