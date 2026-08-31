$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnvFile = Join-Path $Root 'Server\.env'

Write-Host ''
Write-Host 'GRSJ HRMS - DigiLocker Requester Configuration' -ForegroundColor Cyan
Write-Host '------------------------------------------------'
Write-Host 'Registered callback URL should be:' -ForegroundColor Yellow
Write-Host 'https://hrms.grsj.in/admin/digilocker/callback'
Write-Host ''

$ClientId = Read-Host 'Enter DigiLocker / API Setu Client ID'
if ([string]::IsNullOrWhiteSpace($ClientId)) { throw 'Client ID cannot be blank.' }
$SecretSecure = Read-Host 'Enter Client Secret' -AsSecureString
$BSTR = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecretSecure)
try { $ClientSecret = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($BSTR) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR) }
if ([string]::IsNullOrWhiteSpace($ClientSecret)) { throw 'Client Secret cannot be blank.' }

$Callback = Read-Host 'Callback URL [press Enter for production default]'
if ([string]::IsNullOrWhiteSpace($Callback)) { $Callback = 'https://hrms.grsj.in/admin/digilocker/callback' }

$existing = @()
if (Test-Path $EnvFile) { $existing = Get-Content $EnvFile }
$keys = @('DIGILOCKER_CLIENT_ID','DIGILOCKER_CLIENT_SECRET','DIGILOCKER_REDIRECT_URI','DIGILOCKER_SCOPE','DIGILOCKER_PURPOSE')
$filtered = $existing | Where-Object {
    $line = $_
    -not ($keys | Where-Object { $line -match ('^' + [regex]::Escape($_) + '=') })
}
$new = @($filtered) + @(
    "DIGILOCKER_CLIENT_ID=$ClientId",
    "DIGILOCKER_CLIENT_SECRET=$ClientSecret",
    "DIGILOCKER_REDIRECT_URI=$Callback",
    'DIGILOCKER_SCOPE=files.issueddocs',
    'DIGILOCKER_PURPOSE=verification'
)
$new | Set-Content -Path $EnvFile -Encoding UTF8

Write-Host ''
Write-Host 'Saved successfully to Server\.env' -ForegroundColor Green
Write-Host 'Restart GRSJ HRMS. Employee Profile > Documents will then show Verify / Import from DigiLocker.' -ForegroundColor Green
Write-Host 'Client Secret was not printed and is not stored in any template or source file.' -ForegroundColor DarkGray
