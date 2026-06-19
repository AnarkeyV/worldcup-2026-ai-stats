[CmdletBinding()]
param(
    [string]$ProjectDir = "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats",
    [string]$LocalHealthUrl = "http://localhost:8000/health",
    [string]$AiHealthUrl = "http://localhost:8000/ai/health",
    [string]$DashboardHealthUrl = "http://localhost:18501/_stcore/health",
    [string]$PublicHealthUrl = "https://wc2026.khairulrizal.qzz.io/health",
    [int]$DockerWaitSeconds = 120
)

$ErrorActionPreference = "Stop"

$LogDir = Join-Path $ProjectDir "runtime-logs"
New-Item -ItemType Directory -Force $LogDir | Out-Null

$script:LogFile = Join-Path $LogDir ("watchdog-{0}.log" -f (Get-Date -Format "yyyyMMdd"))

function Write-Log {
    param([string]$Message)

    $Line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Write-Host $Line
    Add-Content -Path $script:LogFile -Value $Line
}

function Test-Url {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 10
    )

    try {
        $Response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSeconds
        return ($Response.StatusCode -ge 200 -and $Response.StatusCode -lt 300)
    }
    catch {
        return $false
    }
}

function Test-DockerEngine {
    try {
        docker info *> $null
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
}

function Start-DockerDesktopIfNeeded {
    if (Test-DockerEngine) {
        Write-Log "Docker engine is available."
        return
    }

    Write-Log "Docker engine is unavailable. Attempting to start Docker Desktop."

    $ProgramFilesX86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
    $PossiblePaths = @()

    if ($env:ProgramFiles) {
        $PossiblePaths += (Join-Path $env:ProgramFiles "Docker\Docker\Docker Desktop.exe")
    }

    if ($ProgramFilesX86) {
        $PossiblePaths += (Join-Path $ProgramFilesX86 "Docker\Docker\Docker Desktop.exe")
    }

    $DockerDesktopPath = $PossiblePaths | Where-Object { Test-Path $_ } | Select-Object -First 1

    if ($DockerDesktopPath) {
        Start-Process -FilePath $DockerDesktopPath | Out-Null
    }

    $Deadline = (Get-Date).AddSeconds($DockerWaitSeconds)

    while ((Get-Date) -lt $Deadline) {
        if (Test-DockerEngine) {
            Write-Log "Docker engine became available."
            return
        }

        Start-Sleep -Seconds 10
    }

    throw "Docker engine did not become available within $DockerWaitSeconds seconds."
}

function Ensure-CloudflaredService {
    $Service = Get-Service -Name cloudflared -ErrorAction SilentlyContinue

    if (-not $Service) {
        Write-Log "cloudflared service was not found."
        return
    }

    if ($Service.Status -eq "Running") {
        Write-Log "cloudflared service is running."
        return
    }

    Write-Log "cloudflared service is $($Service.Status). Attempting to start it."

    try {
        Start-Service cloudflared
        Start-Sleep -Seconds 5
        $Service.Refresh()
        Write-Log "cloudflared service status: $($Service.Status)"
    }
    catch {
        Write-Log "WARNING: Failed to start cloudflared service. $($_.Exception.Message)"
    }
}

function Invoke-Compose {
    param([string[]]$ComposeArgs)

    Push-Location $ProjectDir

    try {
        Write-Log "Running: docker compose $($ComposeArgs -join ' ')"
        & docker compose @ComposeArgs

        if ($LASTEXITCODE -ne 0) {
            throw "docker compose $($ComposeArgs -join ' ') failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }
}

function Restart-UnhealthyContainers {
    $Containers = @(
        "worldcup-postgres",
        "worldcup-backend",
        "worldcup-dashboard"
    )

    foreach ($Container in $Containers) {
        $HealthLine = & docker inspect --format "{{.Name}} {{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}" $Container 2>$null

        if ($LASTEXITCODE -ne 0) {
            Write-Log "Container not found or not inspectable: $Container"
            continue
        }

        Write-Log "Container health: $HealthLine"

        if ($HealthLine -match "unhealthy") {
            Write-Log "Restarting unhealthy container: $Container"
            & docker restart $Container | Out-Null
        }
    }
}

try {
    Write-Log "Starting World Cup runtime watchdog check."

    if (-not (Test-Path $ProjectDir)) {
        throw "Project directory does not exist: $ProjectDir"
    }

    Ensure-CloudflaredService
    Start-DockerDesktopIfNeeded

    Invoke-Compose -ComposeArgs @("up", "-d")
    Restart-UnhealthyContainers

    if (-not (Test-Url -Url $LocalHealthUrl -TimeoutSeconds 10)) {
        Write-Log "Backend local health failed. Restarting backend."
        Invoke-Compose -ComposeArgs @("restart", "backend")
        Start-Sleep -Seconds 10
    }
    else {
        Write-Log "Backend local health is OK."
    }

    if (-not (Test-Url -Url $DashboardHealthUrl -TimeoutSeconds 10)) {
        Write-Log "Dashboard health failed. Restarting dashboard."
        Invoke-Compose -ComposeArgs @("restart", "dashboard")
        Start-Sleep -Seconds 10
    }
    else {
        Write-Log "Dashboard health is OK."
    }

    if (-not (Test-Url -Url $AiHealthUrl -TimeoutSeconds 10)) {
        Write-Log "WARNING: AI health endpoint did not respond. Backend may still be healthy."
    }
    else {
        Write-Log "AI health endpoint responded."
    }

    if (-not (Test-Url -Url $PublicHealthUrl -TimeoutSeconds 20)) {
        Write-Log "Public Cloudflare health failed. Restarting cloudflared service."

        try {
            Restart-Service cloudflared -ErrorAction Stop
            Start-Sleep -Seconds 10
        }
        catch {
            Write-Log "WARNING: Failed to restart cloudflared. $($_.Exception.Message)"
        }
    }
    else {
        Write-Log "Public Cloudflare health is OK."
    }

    Write-Log "World Cup runtime watchdog check completed."
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}
