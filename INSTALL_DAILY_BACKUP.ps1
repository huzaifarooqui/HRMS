$ErrorActionPreference="Stop"
$TaskName="GRSJ HRMS Daily Backup"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$Python=Join-Path $Root ".venv\Scripts\python.exe"
$Script=Join-Path $Root "Server\backup_hrms.py"
$action=New-ScheduledTaskAction -Execute $Python -Argument "`"$Script`""
$trigger=New-ScheduledTaskTrigger -Daily -At 1:00AM
$principal=New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings | Out-Null
Write-Host "Daily HRMS backup scheduled for 1:00 AM." -ForegroundColor Green
