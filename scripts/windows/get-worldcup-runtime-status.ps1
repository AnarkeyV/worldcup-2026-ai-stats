[CmdletBinding()]
param(
    [string]$ProjectDir = "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats",
    [string]$LocalHealthUrl = "http://localhost:8000/health",
    [string]$AiHealthUrl = "http://localhost:8000/ai/health",
    [string]$DashboardHealthUrl = "http://localhost:18501/_stcore/health",
    [string]$PublicHealthUrl = "https://wc2026.khairulrizal.qzz.io/health",
    [string]$OllamaTagsUrl = "http://127.0.0.1:11434/api/tags",
    [string]$OllamaTaskName = "WorldCup2026 - Ollama Local AI",
    [switch]$FailOnCritical
)

$ErrorActionPreference = "Continue"
$script:CriticalFailures = New-Object System.Collections.Generic.List[string]
$script:Warnings = New-Object System.Collections.Generic.List[string]
$script:LocalBackendVersion = $null
$script:PublicBackendVersion = $null

function Write-Section {
    param([string]$Title)

    Write-Host ""
    Write-Host "===== $Title =====" -ForegroundColor Cyan
}

function Write-Result {
    param(
        [ValidateSet("PASS", "WARN", "FAIL", "INFO")]
        [string]$State,
        [string]$Component,
        [string]$Message
    )

    $Color = switch ($State) {
        "PASS" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
        default { "Gray" }
    }

    Write-Host ("[{0}] {1}: {2}" -f $State, $Component, $Message) -ForegroundColor $Color
}

function Add-Critical {
    param([string]$Message)

    $script:CriticalFailures.Add($Message)
}

function Add-Warning {
    param([string]$Message)

    $script:Warnings.Add($Message)
}

function Get-HttpResponse {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 10
    )

    try {
        $Response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSeconds

        return [PSCustomObject]@{
            Success = ($Response.StatusCode -ge 200 -and $Response.StatusCode -lt 300)
            StatusCode = $Response.StatusCode
            Error = $null
        }
    }
    catch {
        return [PSCustomObject]@{
            Success = $false
            StatusCode = $null
            Error = $_.Exception.Message
        }
    }
}

function Test-DockerEngine {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        return $false
    }

    try {
        docker info *> $null
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
}

Write-Section "Read-only runtime status"

if (-not (Test-Path -LiteralPath $ProjectDir)) {
    Write-Result -State "FAIL" -Component "Project directory" -Message "Not found: $ProjectDir"
    Add-Critical "Project directory is missing."
}
else {
    Write-Result -State "PASS" -Component "Project directory" -Message $ProjectDir
}

Write-Section "Docker and containers"

if (Test-DockerEngine) {
    Write-Result -State "PASS" -Component "Docker engine" -Message "Available."

    if (Test-Path -LiteralPath $ProjectDir) {
        Push-Location -LiteralPath $ProjectDir

        try {
            $ComposeOutput = & docker compose ps 2>&1

            if ($LASTEXITCODE -eq 0) {
                Write-Result -State "PASS" -Component "Docker Compose" -Message "Container state follows."
                $ComposeOutput | ForEach-Object { Write-Host $_ }
            }
            else {
                Write-Result -State "WARN" -Component "Docker Compose" -Message "docker compose ps returned exit code $LASTEXITCODE."
                Add-Warning "Docker Compose status could not be read."
            }
        }
        finally {
            Pop-Location
        }
    }
}
else {
    Write-Result -State "FAIL" -Component "Docker engine" -Message "Unavailable."
    Add-Critical "Docker engine is unavailable."
}

Write-Section "Local application endpoints"

try {
    $BackendHealth = Invoke-RestMethod -Uri $LocalHealthUrl -TimeoutSec 10
    $script:LocalBackendVersion = if ($BackendHealth.version) { [string]$BackendHealth.version } else { $null }

    if ($BackendHealth.status -eq "healthy") {
        $Version = if ($script:LocalBackendVersion) { $script:LocalBackendVersion } else { "unknown version" }
        Write-Result -State "PASS" -Component "Backend health" -Message "healthy ($Version)"
    }
    else {
        Write-Result -State "FAIL" -Component "Backend health" -Message "Unexpected status: $($BackendHealth.status)"
        Add-Critical "Backend health is not healthy."
    }
}
catch {
    Write-Result -State "FAIL" -Component "Backend health" -Message $_.Exception.Message
    Add-Critical "Backend health endpoint is unavailable."
}

$DashboardResult = Get-HttpResponse -Url $DashboardHealthUrl

if ($DashboardResult.Success) {
    Write-Result -State "PASS" -Component "Dashboard health" -Message "HTTP $($DashboardResult.StatusCode)"
}
else {
    Write-Result -State "WARN" -Component "Dashboard health" -Message $DashboardResult.Error
    Add-Warning "Dashboard health endpoint is unavailable."
}

Write-Section "Cloudflared and public reachability"

$Cloudflared = Get-Service -Name cloudflared -ErrorAction SilentlyContinue

if (-not $Cloudflared) {
    Write-Result -State "WARN" -Component "Cloudflared service" -Message "Not found. No service action was attempted."
    Add-Warning "Cloudflared service was not found."
}
elseif ($Cloudflared.Status -eq "Running") {
    Write-Result -State "PASS" -Component "Cloudflared service" -Message "Running."
}
else {
    Write-Result -State "WARN" -Component "Cloudflared service" -Message "$($Cloudflared.Status). No service action was attempted."
    Add-Warning "Cloudflared service is not running."
}

try {
    $PublicHealth = Invoke-RestMethod -Uri $PublicHealthUrl -TimeoutSec 20
    $script:PublicBackendVersion = if ($PublicHealth.version) { [string]$PublicHealth.version } else { $null }
    $PublicVersion = if ($script:PublicBackendVersion) { $script:PublicBackendVersion } else { "unknown version" }

    if ($PublicHealth.status -eq "healthy") {
        Write-Result -State "PASS" -Component "Public health" -Message "healthy ($PublicVersion)"
    }
    else {
        Write-Result -State "WARN" -Component "Public health" -Message "Unexpected status: $($PublicHealth.status) ($PublicVersion)"
        Add-Warning "Public health response is not healthy."
    }
}
catch {
    Write-Result -State "WARN" -Component "Public health" -Message $_.Exception.Message
    Add-Warning "Public health is unavailable."
}

if (
    $script:LocalBackendVersion -and
    $script:PublicBackendVersion -and
    $script:LocalBackendVersion -ne $script:PublicBackendVersion
) {
    Write-Result -State "WARN" -Component "Version consistency" -Message "Local backend version $($script:LocalBackendVersion) differs from public version $($script:PublicBackendVersion)."
    Add-Warning "Local and public backend versions differ."
}
elseif ($script:LocalBackendVersion -and $script:PublicBackendVersion) {
    Write-Result -State "PASS" -Component "Version consistency" -Message "Local and public backend versions match ($($script:LocalBackendVersion))."
}
else {
    Write-Result -State "INFO" -Component "Version consistency" -Message "Comparison skipped because one or both backend versions were unavailable."
}

Write-Section "Ollama and local AI"

try {
    $OllamaTags = Invoke-RestMethod -Uri $OllamaTagsUrl -TimeoutSec 10
    $ModelNames = @($OllamaTags.models | ForEach-Object { $_.name } | Where-Object { $_ })

    if ($ModelNames.Count -gt 0) {
        Write-Result -State "PASS" -Component "Host Ollama API" -Message ("Available. Models: " + ($ModelNames -join ", "))
    }
    else {
        Write-Result -State "WARN" -Component "Host Ollama API" -Message "Available but no installed models were returned."
        Add-Warning "Ollama returned no installed models."
    }
}
catch {
    Write-Result -State "WARN" -Component "Host Ollama API" -Message $_.Exception.Message
    Add-Warning "Ollama host API is unavailable."
}

try {
    $AiHealth = Invoke-RestMethod -Uri $AiHealthUrl -TimeoutSec 10

    if ($AiHealth.available -eq $true) {
        $Model = if ($AiHealth.configured_model) { $AiHealth.configured_model } else { "unknown model" }
        Write-Result -State "PASS" -Component "Application AI health" -Message "Available ($Model)"
    }
    else {
        $Detail = if ($AiHealth.error) { $AiHealth.error } else { "provider unavailable" }
        Write-Result -State "WARN" -Component "Application AI health" -Message $Detail
        Add-Warning "Application AI health is unavailable."
    }
}
catch {
    Write-Result -State "WARN" -Component "Application AI health" -Message $_.Exception.Message
    Add-Warning "Application AI health endpoint is unavailable."
}

$OllamaTask = Get-ScheduledTask -TaskName $OllamaTaskName -ErrorAction SilentlyContinue

if (-not $OllamaTask) {
    Write-Result -State "WARN" -Component "Ollama scheduled task" -Message "Not found: $OllamaTaskName"
    Add-Warning "Ollama scheduled task was not found."
}
else {
    try {
        $OllamaTaskInfo = Get-ScheduledTaskInfo -TaskName $OllamaTaskName -ErrorAction Stop
        $LastRun = if ($OllamaTaskInfo.LastRunTime) { $OllamaTaskInfo.LastRunTime } else { "never" }
        Write-Result -State "INFO" -Component "Ollama scheduled task" -Message "State: $($OllamaTask.State); last run: $LastRun; result: $($OllamaTaskInfo.LastTaskResult)"
    }
    catch {
        Write-Result -State "WARN" -Component "Ollama scheduled task" -Message "State: $($OllamaTask.State); task detail could not be read."
        Add-Warning "Ollama scheduled task detail could not be read."
    }
}

Write-Section "Summary"

Write-Result -State "INFO" -Component "Critical issues" -Message $script:CriticalFailures.Count
Write-Result -State "INFO" -Component "Warnings" -Message $script:Warnings.Count
Write-Result -State "INFO" -Component "Safety" -Message "No Docker restart, provider sync, Telegram action, Cloudflared action, Ollama action, or configuration change was performed."

if ($FailOnCritical -and $script:CriticalFailures.Count -gt 0) {
    exit 1
}
