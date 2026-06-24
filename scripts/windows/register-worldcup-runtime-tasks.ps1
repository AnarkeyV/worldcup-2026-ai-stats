[CmdletBinding()]
param(
    [string]$ProjectDir = "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats"
)

$ErrorActionPreference = "Stop"

$StartupScript = Join-Path $ProjectDir "scripts\windows\start-worldcup-runtime.ps1"
$WatchdogScript = Join-Path $ProjectDir "scripts\windows\watch-worldcup-runtime.ps1"
$StartupLauncher = Join-Path $ProjectDir "scripts\windows\start-worldcup-runtime-hidden.vbs"
$WatchdogLauncher = Join-Path $ProjectDir "scripts\windows\watch-worldcup-runtime-hidden.vbs"

foreach ($Path in @($StartupScript, $WatchdogScript, $StartupLauncher, $WatchdogLauncher)) {
    if (-not (Test-Path $Path)) {
        throw "Required runtime script not found: $Path"
    }
}

$WScriptExe = Join-Path $env:SystemRoot "System32\wscript.exe"

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
    -Hidden `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

$StartupAction = New-ScheduledTaskAction `
    -Execute $WScriptExe `
    -Argument "`"$StartupLauncher`"" `
    -WorkingDirectory $ProjectDir

$StartupTrigger = New-ScheduledTaskTrigger -AtLogOn

Write-Host "Registering startup task: $StartupTaskName"

Register-ScheduledTask `
    -TaskName $StartupTaskName `
    -Action $StartupAction `
    -Trigger $StartupTrigger `
    -Principal $Principal `
    -Settings $Settings `
    -Description "Starts the World Cup 2026 AI Stats Docker runtime and verifies local/public health at Windows logon. Cloudflared and Ollama checks are report-only." `
    -Force | Out-Null

$WatchdogAction = New-ScheduledTaskAction `
    -Execute $WScriptExe `
    -Argument "`"$WatchdogLauncher`"" `
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
    -Description "Checks the World Cup 2026 AI Stats runtime every 15 minutes, repairs unhealthy Docker containers, and reports Cloudflared/Ollama state without starting or restarting them." `
    -Force | Out-Null

Write-Host ""
Write-Host "Registered tasks:"
Get-ScheduledTask | Where-Object {
    $_.TaskName -eq $StartupTaskName -or
    $_.TaskName -eq $WatchdogTaskName
} | Select-Object TaskName, State, TaskPath

Write-Host ""
Write-Host "Done. The startup task runs at Windows logon. The watchdog runs every 15 minutes without opening a visible PowerShell window. Docker recovery remains automatic; Cloudflared and Ollama are report-only."
