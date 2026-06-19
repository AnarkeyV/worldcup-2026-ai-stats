# World Cup 2026 AI Stats

![Version](https://img.shields.io/badge/version-v1.10.0-purple)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Database](https://img.shields.io/badge/database-PostgreSQL-336791)
![AI](https://img.shields.io/badge/AI-Ollama%20%2B%20Local%20Llama-green)
![Notifications](https://img.shields.io/badge/notifications-Telegram-lightblue)
![Monitoring](https://img.shields.io/badge/monitoring-Prometheus%20%2B%20Grafana-orange)

A self-hosted World Cup 2026 dashboard that syncs provider fixture data, tracks matches and standings, generates local AI summaries, sends Telegram alerts, and exposes a mobile-friendly dashboard through Cloudflare Tunnel.

Public dashboard:

```text
https://wc2026.khairulrizal.qzz.io/dashboard
```

Current stable release:

```text
v1.9.0
```

Current working milestone:

```text
v1.10.0 — Match Detail Dashboard + Portfolio README Polish
```

---

## What This Project Does

World Cup 2026 AI Stats is a personal football intelligence dashboard built to track the FIFA World Cup 2026 from a self-hosted runtime environment.

It is designed to answer practical questions such as:

- What fixtures are available from the live provider?
- Which matches are completed, scheduled, or live?
- What are the current group standings?
- Which teams are leading on points, goals, and defensive record?
- Can a local AI model summarize fixtures without depending on a paid cloud LLM?
- Can match updates be sent to Telegram with a mobile dashboard link?
- Can the project keep running from a Windows laptop as a home-hosted runtime?

The project is intentionally local-first, portfolio-ready, and demo-friendly.

---

## Current Highlights

### v1.9.0 Live Runtime Features

The v1.9.0 release made the project usable as a live personal dashboard.

Key features include:

- Zafronix World Cup 2026 provider integration
- 72 usable World Cup 2026 fixtures synced from provider data
- Local Ollama AI health checks using `llama3.2:1b`
- Local AI fixture summaries with deterministic fallback behavior
- Telegram notification readiness and live test message delivery
- Telegram messages that can include a mobile dashboard link
- Public dashboard access through Cloudflare Tunnel
- Windows laptop runtime using Docker Compose
- Backend, dashboard, Postgres, Prometheus, Grafana, Cloudflare Tunnel, Telegram, and Ollama running together
- Docker health checks and runtime resilience improvements
- Provider sync observability through dashboard, API, metrics, and Grafana

### v1.10.0 Dashboard UX Work

The v1.10.0 milestone improves presentation quality and dashboard usability.

Planned and in-progress work:

- Make fixture cards clickable
- Open a match-detail dashboard panel when a fixture is selected
- Show scoreline, status, venue, kickoff time, teams, group, stage, and provider-backed context
- Reuse local AI fixture summaries inside match detail views
- Keep the dashboard mobile-friendly
- Add safe placeholders for future match events, cards, lineups, formations, and advanced stats
- Refresh this README as a stronger portfolio landing page

---

## Why This Project Exists

This project was built as a practical DevOps, backend, automation, observability, and AI portfolio project.

It demonstrates:

- API backend development with FastAPI
- PostgreSQL-backed local runtime
- provider API integration and data normalization
- Docker Compose deployment
- local AI integration using Ollama
- notification workflows through Telegram
- Cloudflare Tunnel public access
- Prometheus metrics
- Grafana dashboards
- automated tests with pytest
- release-based GitHub workflow
- MacBook development with a Windows laptop runtime host

---

## Architecture Overview

```text
MacBook Pro
VS Code + Python venv + Git
        |
        | git push / SSH control
        v
Windows Laptop Runtime Host
Docker Desktop + Docker Compose
        |
        |-- FastAPI backend
        |-- Static dashboard
        |-- PostgreSQL
        |-- Prometheus
        |-- Grafana
        |-- Cloudflare Tunnel
        |-- Telegram notifier
        |-- Ollama local AI
```

External services:

```text
Zafronix Provider API  --->  FastAPI backend  --->  PostgreSQL
Telegram Bot API      <---  notification routes
Cloudflare Tunnel     --->  public dashboard URL
Ollama                <---  local AI health and summaries
Prometheus            <---  backend metrics
Grafana               <---  dashboard visualization
```

---

## Main Features

### Fixture Tracking

The backend stores World Cup fixtures with:

- competition
- stage
- group
- home and away teams
- team codes
- kickoff time
- venue
- match status
- home and away score
- provider external ID
- created and updated timestamps

Fixture endpoints support:

- listing fixtures
- filtering by group, team, and status
- reading a single fixture
- syncing sample data
- syncing provider data
- checking provider sync runtime status

---

### Zafronix Provider Sync

The project supports Zafronix as the current provider for World Cup 2026 fixture data.

The provider layer normalizes fixture payloads into the local database format and keeps the dashboard independent from raw provider response shapes.

Provider configuration is handled through local environment variables.

Do not commit real provider credentials.

---

### Local AI With Ollama

The AI layer is local-first.

The project can check Ollama health and use a local model for fixture summaries.

Current local model used in the Windows runtime:

```text
llama3.2:1b
```

The AI layer is designed to be demo-safe. If Ollama is unavailable, deterministic fallback summaries keep the dashboard usable instead of breaking the application.

AI features include:

- local AI health endpoint
- tournament fixture summary
- single-match fixture summary
- structured AI insights
- dashboard AI status panel
- fixture-level AI summary buttons

---

### Telegram Alerts

Telegram notification support is optional and controlled through local environment variables.

The project supports:

- readiness checks
- test notification delivery
- dashboard link delivery for mobile viewing
- safe configuration without committing secrets

Never commit Telegram bot tokens, chat IDs, API keys, or `.env` files.

---

### Cloudflare Mobile Dashboard Access

The dashboard can be exposed publicly through Cloudflare Tunnel.

Current public dashboard:

```text
https://wc2026.khairulrizal.qzz.io/dashboard
```

This allows the dashboard to be opened from a mobile phone, including from Telegram notification links.

---

### Monitoring and Observability

The project includes observability through:

- `/metrics` endpoint
- Prometheus
- Grafana
- provider sync runtime status
- fixture sync success/failure metrics
- AI health visibility
- Docker health checks

Useful local URLs:

```text
Backend API:    http://localhost:8000
Dashboard:      http://localhost:8000/dashboard
API Docs:       http://localhost:8000/docs
Metrics:        http://localhost:8000/metrics
Prometheus:     http://localhost:9090
Grafana:        http://localhost:3000
```

---

## Tech Stack

| Area | Technology |
|---|---|
| Backend | FastAPI |
| Runtime database | PostgreSQL |
| Tests | pytest |
| Static dashboard | HTML, CSS, JavaScript |
| Provider data | Zafronix |
| AI | Ollama, local Llama |
| Notifications | Telegram Bot API |
| Monitoring | Prometheus, Grafana |
| Runtime | Docker Compose |
| Public access | Cloudflare Tunnel |
| Development | MacBook Pro, VS Code, Python venv |
| Runtime host | Windows laptop, Docker Desktop |

---

## Repository Structure

```text
worldcup-2026-ai-stats/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── providers/
│   │   ├── routes/
│   │   ├── services/
│   │   └── static/
│   │       ├── dashboard.html
│   │       ├── dashboard.css
│   │       └── dashboard.js
│   ├── tests/
│   └── pytest.ini
├── docs/
├── grafana/
├── prometheus/
├── docker-compose.yml
├── .env.example
├── VERSION
└── README.md
```

---

## Local Development Workflow

The preferred workflow for this project is:

| Machine | Purpose |
|---|---|
| MacBook Pro | Main development and control machine |
| Windows laptop | Docker/runtime/demo host |
| VS Code | Main editor |
| Python venv | Local test environment |
| SSH | Remote checks from MacBook into Windows PowerShell |

Typical development loop:

```bash
cd ~/documents/worldcup-2026-ai-stats

git checkout main
git pull --ff-only origin main
git checkout -b feature/<milestone-name>

source .venv/bin/activate
pytest -q
```

After changes:

```bash
pytest -q
git status
git diff --stat
git add .
git commit -m "Describe the milestone change"
git push -u origin feature/<milestone-name>
```

---

## Environment Configuration

Copy the example environment file locally:

```bash
cp .env.example .env
```

Then edit `.env` locally.

Do not commit `.env`.

Important environment categories:

```text
App configuration
Database configuration
Provider configuration
Telegram configuration
Ollama/local AI configuration
Cloudflare/runtime configuration
```

Real secrets must stay local.

Never commit:

- API keys
- Telegram bot tokens
- Telegram chat IDs
- production URLs that should remain private
- `.env`
- database files
- local runtime artifacts

---

## MacBook Development Setup

Recommended local development setup:

```bash
cd ~/documents/worldcup-2026-ai-stats
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pytest -q
```

Run the backend locally:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000
http://localhost:8000/dashboard
http://localhost:8000/docs
```

---

## Windows Docker Runtime Setup

The Windows laptop acts as the runtime/demo host.

From Windows PowerShell:

```powershell
cd "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats"
docker compose up -d --build
docker compose ps
```

Check the backend:

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/fixtures
curl.exe http://localhost:8000/fixtures/sync/status
curl.exe http://localhost:8000/ai/health
curl.exe http://localhost:8000/notifications/telegram/status
```

Stop the runtime:

```powershell
docker compose down
```

---

## SSH Workflow From MacBook to Windows

From the MacBook:

```bash
ssh windows-laptop
```

Then inside Windows PowerShell:

```powershell
cd "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats"
docker compose ps
curl.exe http://localhost:8000/health
```

This keeps the MacBook as the control machine while the Windows laptop runs Docker, Ollama, monitoring, and Cloudflare Tunnel.

---

## Common Runtime Checks

### Backend Health

```bash
curl http://localhost:8000/health
```

Expected shape:

```json
{
  "status": "healthy",
  "service": "backend",
  "version": "1.9.0"
}
```

### Fixture Sync Status

```bash
curl http://localhost:8000/fixtures/sync/status
```

### Provider Sync

```bash
curl -X POST http://localhost:8000/fixtures/sync/provider
```

### Local AI Health

```bash
curl http://localhost:8000/ai/health
```

### Telegram Status

```bash
curl http://localhost:8000/notifications/telegram/status
```

### Metrics

```bash
curl http://localhost:8000/metrics
```

---

## Dashboard Usage

Open the dashboard:

```text
http://localhost:8000/dashboard
```

Or use the public Cloudflare dashboard:

```text
https://wc2026.khairulrizal.qzz.io/dashboard
```

Dashboard features:

- fixture list
- fixture filters
- group standings
- group insights
- player statistics
- local AI fixture summary
- structured AI insights
- provider sync runtime status
- AI health status
- clickable match detail panel in v1.10.0

---

## Testing

Run all tests:

```bash
pytest -q
```

Run dashboard tests only:

```bash
pytest backend/tests/test_dashboard.py
```

Current known test checkpoint after the v1.10.0 dashboard patch:

```text
161 passed
```

The Python 3.14 environment may show FastAPI/Starlette deprecation warnings related to `asyncio.iscoroutinefunction`. These warnings do not currently indicate failing application tests.

---

## Screenshots and Evidence

Recommended evidence to capture for portfolio use:

- GitHub README top section
- public dashboard open on desktop
- public dashboard open on mobile
- fixture list with Zafronix synced matches
- clickable match detail dashboard panel
- local AI health online
- generated fixture AI summary
- Telegram test message with dashboard link
- provider sync runtime status
- Prometheus targets
- Grafana dashboard
- Docker Compose services healthy on Windows

Suggested local screenshot folder:

```bash
~/documents/world-cup-ai-stats-screenshots/v1.10.0-match-detail-dashboard
```

Avoid adding broken screenshot links to the README unless the image files are committed into the repository.

---

## Troubleshooting

### `.env` not loaded

Confirm `.env` exists locally and contains only local secrets.

Do not paste `.env` contents into chat, GitHub, issues, or commits.

### Provider sync fails

Check:

- provider API key is configured locally
- provider name is set correctly
- backend can reach the provider API
- `/fixtures/sync/status` for the latest error message

### Ollama is offline

Check that Ollama is running on the Windows host and that the expected model exists locally.

Useful check:

```bash
curl http://localhost:8000/ai/health
```

### Telegram is not ready

Check:

```bash
curl http://localhost:8000/notifications/telegram/status
```

Then verify local Telegram environment variables on the runtime host.

Do not commit or paste Telegram credentials.

### Cloudflare dashboard is unavailable

Check:

- Cloudflare Tunnel service is running
- backend/dashboard is healthy locally
- tunnel routes to the correct local service and port
- Windows runtime host is online

### Windows port bind issue

If a port is blocked or already used, check the process using that port and adjust Docker Compose host port mappings if needed.

---

## Release Workflow

Recommended release workflow:

```bash
git checkout main
git pull --ff-only origin main
git checkout -b feature/vX.Y.Z-description
pytest -q
git add .
git commit -m "Implement vX.Y.Z description"
git push -u origin feature/vX.Y.Z-description
```

Then:

1. Open a pull request on GitHub.
2. Confirm tests and review the diff.
3. Merge into `main`.
4. Pull latest `main`.
5. Tag the release.
6. Publish the GitHub release.
7. Delete the feature branch after merge.

Example tagging:

```bash
git checkout main
git pull --ff-only origin main
git tag -a v1.10.0 -m "v1.10.0 Match Detail Dashboard and README Polish"
git push origin v1.10.0
```

---

## Milestone History

| Version | Milestone | Status |
|---|---|---|
| v0.1.0 | Project foundation | Completed |
| v0.2.0 | Football API integration foundation | Completed |
| v0.3.0 | Real football provider integration | Completed |
| v0.4.0 | Match completion detector | Completed |
| v0.5.0 | Telegram notifications | Completed |
| v0.6.0 | Interactive dashboard | Completed |
| v0.7.0 | API filters and dashboard polish | Completed |
| v0.8.0 | Local Llama summary agent | Completed |
| v1.1.0 | Group standings engine | Completed |
| v1.4.0 | Monitoring and observability foundation | Completed |
| v1.4.1 | Grafana dashboard polish | Completed |
| v1.4.2 | Telegram API live integration hardening | Completed |
| v1.4.3 | Documentation and demo evidence cleanup | Completed |
| v1.5.0 | Portfolio release polish | Completed |
| v1.6.0 | Real match data sync improvement | Completed |
| v1.7.0 | Provider sync observability and runtime demo | Completed |
| v1.8.0 | AI insights upgrade | Completed |
| v1.9.0 | Live local AI, Zafronix, Telegram mobile alerts, Cloudflare dashboard, Windows resilience | Completed |
| v1.10.0 | Match detail dashboard and README polish | In progress |

---

## Portfolio Summary

This project demonstrates a practical self-hosted sports analytics platform using DevOps, backend engineering, local AI, observability, and automation.

It is not just a static dashboard. It is a working local runtime that combines provider data sync, FastAPI APIs, PostgreSQL, Docker Compose, Telegram, Cloudflare Tunnel, Prometheus, Grafana, and Ollama into a real personal monitoring system for World Cup 2026.

---

## Security Notes

This repository should never contain real secrets.

Keep these local only:

- `.env`
- provider API keys
- Telegram bot token
- Telegram chat ID
- Cloudflare tunnel credentials
- database credentials
- local machine-specific runtime files

Use `.env.example` for safe placeholders only.

---

## License

Personal portfolio and learning project.
