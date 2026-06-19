[CmdletBinding()]
param(
    [string]$ProjectDir = "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats"
)

$ErrorActionPreference = "Stop"

$StartupScript = Join-Path $ProjectDir "scripts\windows\start-worldcup-runtime.ps1"
$WatchdogScript = Join-Path $ProjectDir "scripts\windows\watch-worldcup-runtime.ps1"

if (-not (Test-Path $StartupScript)) {
    throw "Startup script not found: $StartupScript"
}

if (-not (Test-Path $WatchdogScript)) {
    throw "Watchdog script not found: $WatchdogScript"
}

$PowerShellExe = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"

$StartupTaskName = "WorldCup Runtime Startup"
$WatchdogTaskName = "WorldCup Runtime Watchdog"

$StartupCommand = "`"$PowerShellExe`" -NoProfile -ExecutionPolicy Bypass -File `"$StartupScript`""
$WatchdogCommand = "`"$PowerShellExe`" -NoProfile -ExecutionPolicy Bypass -File `"$WatchdogScript`""

Write-Host "Registering startup task: $StartupTaskName"
& schtasks.exe /Create /TN $StartupTaskName /TR $StartupCommand /SC ONLOGON /RL HIGHEST /F

if ($LASTEXITCODE -ne 0) {
    throw "Failed to register startup scheduled task."
}

Write-Host "Registering watchdog task: $WatchdogTaskName"
& schtasks.exe /Create /TN $WatchdogTaskName /TR $WatchdogCommand /SC MINUTE /MO 15 /RL HIGHEST /F

if ($LASTEXITCODE -ne 0) {
    throw "Failed to register watchdog scheduled task."
}

Write-Host ""
Write-Host "Registered tasks:"
& schtasks.exe /Query /TN $StartupTaskName
& schtasks.exe /Query /TN $WatchdogTaskName

Write-Host ""
Write-Host "Done. The startup task runs at Windows logon. The watchdog task runs every 15 minutes."
