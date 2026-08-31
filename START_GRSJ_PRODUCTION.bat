@echo off
setlocal

rem Wait until MySQL84 is actually ready instead of relying on a fixed boot delay.
for /L %%I in (1,1,18) do (
  sc query MySQL84 | findstr /I "RUNNING" >nul 2>&1 && goto MYSQL_READY
  timeout /t 5 /nobreak >nul
)

:MYSQL_READY
netstat -ano | findstr "127.0.0.1:5000" | findstr "LISTENING" >nul
if %errorlevel%==0 exit /b 0

cd /d "D:\GRSJ\GRSJ-HRMS_v1.0_Stable\Server"

"D:\GRSJ\GRSJ-HRMS_v1.0_Stable\.venv\Scripts\python.exe" -m waitress ^
  --listen=127.0.0.1:5000 ^
  --threads=8 ^
  app:app >> "D:\GRSJ\GRSJ-HRMS_v1.0_Stable\Server\waitress.log" 2>&1
