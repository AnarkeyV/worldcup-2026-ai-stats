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

$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

Write-Host "Registering tasks as: $CurrentUser"
Write-Host "Project directory: $ProjectDir"
Write-Host ""

$Principal = New-ScheduledTaskPrincipal `
    -UserId $CurrentUser `
    -LogonType Interactive `
    -RunLevel Highest

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

$StartupAction = New-ScheduledTaskAction `
    -Execute $PowerShellExe `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$StartupScript`"" `
    -WorkingDirectory $ProjectDir

$StartupTrigger = New-ScheduledTaskTrigger -AtLogOn

Write-Host "Registering startup task: $StartupTaskName"

Register-ScheduledTask `
    -TaskName $StartupTaskName `
    -Action $StartupAction `
    -Trigger $StartupTrigger `
    -Principal $Principal `
    -Settings $Settings `
    -Description "Starts the World Cup 2026 AI Stats Docker runtime and verifies public dashboard health at Windows logon." `
    -Force | Out-Null

$WatchdogAction = New-ScheduledTaskAction `
    -Execute $PowerShellExe `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$WatchdogScript`"" `
    -WorkingDirectory $ProjectDir

$WatchdogTrigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 15) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

Write-Host "Registering watchdog task: $WatchdogTaskName"

Register-ScheduledTask `
    -TaskName $WatchdogTaskName `
    -Action $WatchdogAction `
    -Trigger $WatchdogTrigger `
    -Principal $Principal `
    -Settings $Settings `
    -Description "Checks the World Cup 2026 AI Stats runtime every 15 minutes and attempts safe self-healing." `
    -Force | Out-Null

Write-Host ""
Write-Host "Registered tasks:"
Get-ScheduledTask | Where-Object {
    $_.TaskName -eq $StartupTaskName -or
    $_.TaskName -eq $WatchdogTaskName
} | Select-Object TaskName, State, TaskPath

Write-Host ""
Write-Host "Done. The startup task runs at Windows logon. The watchdog task runs every 15 minutes."
