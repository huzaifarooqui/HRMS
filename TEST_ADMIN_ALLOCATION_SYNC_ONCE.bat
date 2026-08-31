@echo off
cd /d "%~dp0Server"
"..\.venv\Scripts\python.exe" -c "from allocation_sync import sync_admin_allocation; print('Starting Admin Allocation sync...'); sync_admin_allocation(); print('Admin Allocation sync finished. Refresh Admin > Allocation.')"
echo.
pause
