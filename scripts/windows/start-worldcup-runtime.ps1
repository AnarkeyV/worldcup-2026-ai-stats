[CmdletBinding()]
param(
    [string]$ProjectDir = "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats",
    [string]$LocalHealthUrl = "http://localhost:8000/health",
    [string]$DashboardHealthUrl = "http://localhost:18501/_stcore/health",
    [string]$PublicHealthUrl = "https://wc2026.khairulrizal.qzz.io/health",
    [int]$DockerWaitSeconds = 180,
    [int]$AppWaitSeconds = 120
)

$ErrorActionPreference = "Stop"

$LogDir = Join-Path $ProjectDir "runtime-logs"
New-Item -ItemType Directory -Force $LogDir | Out-Null

$script:LogFile = Join-Path $LogDir ("startup-{0}.log" -f (Get-Date -Format "yyyyMMdd"))

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

function Wait-Url {
    param(
        [string]$Url,
        [int]$WaitSeconds
    )

    $Deadline = (Get-Date).AddSeconds($WaitSeconds)

    while ((Get-Date) -lt $Deadline) {
        if (Test-Url -Url $Url -TimeoutSeconds 10) {
            return $true
        }

        Start-Sleep -Seconds 5
    }

    return $false
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
        Write-Log "Docker engine is already available."
        return
    }

    Write-Log "Docker engine is not available. Attempting to start Docker Desktop."

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
        Write-Log "Starting Docker Desktop from: $DockerDesktopPath"
        Start-Process -FilePath $DockerDesktopPath | Out-Null
    }
    else {
        Write-Log "Docker Desktop executable was not found. Waiting for Docker engine anyway."
    }

    $Deadline = (Get-Date).AddSeconds($DockerWaitSeconds)

    while ((Get-Date) -lt $Deadline) {
        if (Test-DockerEngine) {
            Write-Log "Docker engine is available."
            return
        }

        Write-Log "Waiting for Docker engine..."
        Start-Sleep -Seconds 10
    }

    throw "Docker engine did not become available within $DockerWaitSeconds seconds."
}

function Ensure-CloudflaredService {
    $Service = Get-Service -Name cloudflared -ErrorAction SilentlyContinue

    if (-not $Service) {
        Write-Log "cloudflared service was not found. Skipping Cloudflare service check."
        return
    }

    if ($Service.Status -eq "Running") {
        Write-Log "cloudflared service is already running."
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

try {
    Write-Log "Starting World Cup runtime startup workflow."

    if (-not (Test-Path $ProjectDir)) {
        throw "Project directory does not exist: $ProjectDir"
    }

    Ensure-CloudflaredService
    Start-DockerDesktopIfNeeded

    Invoke-Compose -ComposeArgs @("up", "-d")

    Write-Log "Waiting for backend health: $LocalHealthUrl"

    if (-not (Wait-Url -Url $LocalHealthUrl -WaitSeconds $AppWaitSeconds)) {
        Write-Log "Backend health check failed. Restarting backend."
        Invoke-Compose -ComposeArgs @("restart", "backend")

        if (-not (Wait-Url -Url $LocalHealthUrl -WaitSeconds 60)) {
            throw "Backend did not become healthy after restart."
        }
    }

    Write-Log "Backend is healthy."

    if (-not (Test-Url -Url $DashboardHealthUrl -TimeoutSeconds 10)) {
        Write-Log "Dashboard health check failed. Restarting dashboard."
        Invoke-Compose -ComposeArgs @("restart", "dashboard")
        Start-Sleep -Seconds 10
    }
    else {
        Write-Log "Dashboard is healthy."
    }

    if (-not (Test-Url -Url $PublicHealthUrl -TimeoutSeconds 20)) {
        Write-Log "Public health check failed. Rechecking cloudflared service."
        Ensure-CloudflaredService

        if (-not (Test-Url -Url $PublicHealthUrl -TimeoutSeconds 20)) {
            Write-Log "WARNING: Public health check is still failing. Local runtime may still be healthy."
        }
    }
    else {
        Write-Log "Public Cloudflare health check is healthy."
    }

    Write-Log "World Cup runtime startup workflow completed."
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}
