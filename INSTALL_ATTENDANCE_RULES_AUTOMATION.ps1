$ErrorActionPreference="Stop"
$TaskName="GRSJ Attendance Rules"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$Bat=Join-Path $Root "START_ATTENDANCE_RULES.bat"
$User="$env:USERDOMAIN\$env:USERNAME"
$action=New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$Bat`""
$trigger=New-ScheduledTaskTrigger -AtLogOn -User $User
$principal=New-ScheduledTaskPrincipal -UserId $User -LogonType Interactive -RunLevel Highest
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings | Out-Null
Start-ScheduledTask -TaskName $TaskName
Write-Host "GRSJ Attendance Rules automation installed and started." -ForegroundColor Green
