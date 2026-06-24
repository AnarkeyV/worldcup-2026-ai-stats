# Windows Runtime Recovery Guide

## Purpose

This guide is for the self-hosted Windows runtime used by World Cup 2026 AI Stats.

It covers safe checks for:

- Docker Desktop and the Docker Compose runtime
- local backend and dashboard health
- Cloudflared service state and public reachability
- Ollama availability and the local AI integration
- the user-level Ollama background-launch task

It intentionally does **not** store or display secrets, Cloudflare tunnel credentials, task XML, active `.env` values, or provider credentials.

---

## First response: collect status without changing anything

Run this in normal Windows PowerShell:

```powershell
cd "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats"
.\scripts\windows\get-worldcup-runtime-status.ps1
```

This script is read-only. It does not:

- start, stop, restart, rebuild, or remove Docker containers
- run a provider sync, scheduled digest, or Telegram action
- start, stop, restart, reinstall, or reconfigure Cloudflared
- start, stop, or reconfigure Ollama
- read or print `.env` values
- create, modify, or remove Scheduled Tasks

Use `-FailOnCritical` only when you need an exit code for a local automated check:

```powershell
.\scripts\windows\get-worldcup-runtime-status.ps1 -FailOnCritical
```

---

## Normal healthy state

The expected status is:

- Docker engine available
- backend health reports `healthy`
- dashboard health reports HTTP `200`
- Cloudflared service is `Running`
- public health reports `healthy` and the deployed application version
- local and public backend versions match
- host Ollama API lists `llama3.2:1b`
- application AI health reports `available: true`
- `WorldCup2026 - Ollama Local AI` is present

The Ollama scheduled task may show `Ready` after it launches the hidden server process. That can be normal: the launcher exits while Ollama continues in the background.

The read-only status checker treats public health as healthy only when its response reports `status: healthy`. It also compares local and public backend versions when both are available. A version mismatch is a warning: it can indicate a partial deployment, a stale public route, or a runtime version setting that has not been promoted.

---

## Local backend or dashboard is unavailable

1. Run the read-only status checker first.
2. Confirm Docker Desktop is available:

   ```powershell
   docker info
   ```

3. Inspect the runtime without making a change:

   ```powershell
   cd "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats"
   docker compose ps
   curl.exe http://localhost:8000/health
   ```

4. If Docker is available and a container is stopped or unhealthy, use the existing runtime recovery workflow or make an explicit, approved Docker recovery decision.

Do not use `docker compose down -v` for normal recovery. It can remove runtime data.

---

## Public dashboard is unavailable but local health is healthy

A working local backend with failed public health usually points to Cloudflared or public routing, not the application itself. A public response whose `status` is not `healthy`, or whose version differs from local backend health, should be treated as a warning and investigated before calling a deployment complete.

Start with read-only checks:

```powershell
Get-Service -Name Cloudflared
sc.exe queryex Cloudflared
```

Do not paste or commit any of the following:

- Cloudflare tunnel token
- `cert.pem`
- tunnel credential JSON
- `config.yml` contents
- Cloudflare service command line if it includes credentials

Do not blindly copy tunnel configuration files between Windows profiles and do not recreate a tunnel just because public health is unavailable.

If the Cloudflared service is stopped or repeatedly fails:

1. Confirm the local application is healthy.
2. Record only the service state and non-secret file paths/metadata.
3. Check that the service points to the intended existing configuration.
4. Restore or repair the existing configuration through a human-approved change.
5. Recheck local health, then public `/health`.

The project runtime scripts are deliberately **report-only** for Cloudflared. They do not start or restart the service automatically.

---

## Ollama or dashboard AI is unavailable

Check the local host API first:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags |
    Select-Object -ExpandProperty models |
    Select-Object name
```

Then check the application view:

```powershell
Invoke-RestMethod http://localhost:8000/ai/health |
    ConvertTo-Json -Depth 6
```

The expected model is:

```text
llama3.2:1b
```

The scheduled task is named:

```text
WorldCup2026 - Ollama Local AI
```

Inspect its state without changing it:

```powershell
Get-ScheduledTask -TaskName "WorldCup2026 - Ollama Local AI" |
    Select-Object TaskName, State

Get-ScheduledTaskInfo -TaskName "WorldCup2026 - Ollama Local AI" |
    Select-Object LastRunTime, LastTaskResult
```

For an explicit human-approved manual recovery during a logged-in session, use the tested hidden launch command:

```powershell
Start-Process `
    -FilePath "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" `
    -ArgumentList "serve" `
    -WindowStyle Hidden
```

Then verify the host API and `/ai/health` again.

Do not pull, delete, or replace models as part of an availability check.

The project runtime scripts are deliberately **report-only** for Ollama. They do not start, stop, kill, or reconfigure the local AI process.

---

## Windows sign-in check

After a normal Windows sign-in, confirm that the background Ollama task started successfully:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags |
    Select-Object -ExpandProperty models |
    Select-Object name

Invoke-RestMethod http://localhost:8000/ai/health |
    ConvertTo-Json -Depth 6
```

Expected result:

- `llama3.2:1b` appears in the model list
- application AI health reports `available: true`

---

## Recovery boundaries

Do not perform these actions without a separate explicit decision:

- modifying the active `.env`
- rebuilding or replacing Docker images
- deleting volumes, database data, or runtime logs
- running provider sync or backfills
- sending test Telegram messages
- changing Cloudflare tunnel hostnames, tokens, config contents, or credentials
- creating a replacement tunnel
- exposing the Ollama API beyond the Windows host
- changing the Ollama model or pulling a new model

The Windows startup and watchdog scripts may still repair unhealthy Docker containers. Cloudflared and Ollama are intentionally outside their automatic repair scope.
