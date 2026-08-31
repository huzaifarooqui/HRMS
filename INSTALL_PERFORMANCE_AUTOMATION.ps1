$ErrorActionPreference = "Stop"

$TaskName = "GRSJ Performance Tracking Sync"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Bat = Join-Path $ProjectRoot "START_ALLOCATION_SYNC.bat"
$UserId = "$env:USERDOMAIN\$env:USERNAME"

Write-Host ""
Write-Host "Installing GRSJ Performance Tracking Auto-Sync..." -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot"
Write-Host "Run as:  $UserId"
Write-Host ""

if (-not (Test-Path $Bat)) {
    throw "START_ALLOCATION_SYNC.bat not found."
}

$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$Bat`""
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $UserId
$principal = New-ScheduledTaskPrincipal -UserId $UserId -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0) `
    -MultipleInstances IgnoreNew

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings | Out-Null
Start-ScheduledTask -TaskName $TaskName

Write-Host "Installed and started successfully." -ForegroundColor Green
Write-Host ""
Write-Host "Automation rules:"
Write-Host " Employee sources: Fazil, Harshit Kumar, Heena, Lucky"
Write-Host " Ignored employee sources: Huzaifa, SyncTrash, all other folders"
Write-Host " Admin source only: C:\Users\Lenovo\Koofr\Huzaifa\Master Allocation Aug'2026.xlsb"
Write-Host " Sheet read: Performance only"
Write-Host ""
