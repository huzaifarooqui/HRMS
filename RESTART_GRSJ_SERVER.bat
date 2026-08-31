@echo off
schtasks /end /tn "GRSJ HRMS Server" >nul 2>&1
timeout /t 2 /nobreak >nul
schtasks /run /tn "GRSJ HRMS Server"
echo GRSJ HRMS server restart requested. Wait about 60 seconds before testing the website.
pause
