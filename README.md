# World Cup 2026 AI Stats

![Version](https://img.shields.io/badge/version-v1.11.0-purple)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Database](https://img.shields.io/badge/database-PostgreSQL-336791)
![AI](https://img.shields.io/badge/AI-Ollama%20%2B%20Local%20Llama-green)
![Notifications](https://img.shields.io/badge/notifications-Telegram-lightblue)
![Monitoring](https://img.shields.io/badge/monitoring-Prometheus%20%2B%20Grafana-orange)

A self-hosted World Cup 2026 intelligence dashboard for provider-backed fixtures, rich match detail, standings, player event leaders, local AI summaries, Telegram alerts, and runtime observability.

**Public dashboard**

```text
https://wc2026.khairulrizal.qzz.io/dashboard
```

**Current release**

```text
v1.11.0 — Mobile Rich Match Dashboard, Provider Leaders, and Group Race
```

---

## Why This Project Exists

World Cup 2026 AI Stats is a local-first football analytics project built as a practical DevOps, backend, automation, observability, and AI portfolio system.

It is designed to answer useful matchday questions:

- Which fixtures are complete, live, or upcoming?
- What happened in a completed match beyond the final score?
- Which players are leading in goals, yellow cards, and red cards?
- Who currently occupies the top two positions in each group?
- Can a local model provide summaries without a paid cloud LLM?
- Can match updates open directly on a mobile dashboard from Telegram?
- Can the system be operated from a Windows home runtime while development stays on a MacBook?

The project is intentionally self-hosted, provider-backed, explainable, and safe to demo.

---

## v1.11.0 Highlights

### Rich Match Detail Dashboard

Fixtures are browsed by **Completed**, **Live**, and **Upcoming** status, then narrowed by group. Selecting a fixture opens a provider-backed detail dashboard with:

- scoreline, kickoff, venue, stage, group, and provider context
- match event timeline
- goals and cards
- team statistics
- formations and lineups when present
- referee and weather context when present
- local AI match-summary controls

The layout keeps fixture browsing and match detail together on desktop, then prioritises the selected match detail on narrower screens.

### Persistent Quick Links

A sticky Quick Links bar makes it easy to move between:

```text
Overview · Sync · AI Summary · AI Insights · Group Insights · Players · Standings · Fixtures
```

The active link follows the currently viewed section. The navigation remains horizontally usable on smaller screens.

### Provider-Backed Player Leaders

The dashboard now derives player leaderboards only from stored provider match details:

- top scorers
- yellow-card leaders
- red-card leaders
- team and group filters
- clear match-detail coverage information

Assist leaders are intentionally shown as unavailable when the provider payload does not include assist events. No generic sample player records are presented as live data.

### Latest Completed Result

The AI area includes an always-visible provider-backed latest-result card. It prioritises major incidents when present, then provides the final result and scorer context from stored detail events.

### Group Race

Structured AI Insights now includes a **Group Race** board that shows the top two teams in every populated group, ordered by the existing standings rules. This gives a concise qualification-picture view without relying on a generic strongest-attacks card.

### Release Verification Snapshot

At v1.11.0 release validation, the self-hosted runtime showed:

```text
72 provider fixtures available
40 completed fixtures
40 of 40 completed fixtures with stored match details
12 populated Group Race boards
184 automated tests passing
```

These are runtime verification values, not hard-coded product limits. They may change after future provider syncs.

---

## Architecture at a Glance

```text
MacBook Pro
VS Code + Python venv + Git
        |
        | git push / SSH control
        v
Windows Laptop Runtime Host
Docker Desktop + Docker Compose
        |
        |-- FastAPI backend + static dashboard
        |-- PostgreSQL
        |-- Prometheus
        |-- Grafana
        |-- Cloudflare Tunnel
        |-- Telegram integration
        |-- Ollama on the Windows host
        |
        +--> Public mobile dashboard
             https://wc2026.khairulrizal.qzz.io/dashboard
```

External integrations:

```text
Zafronix Provider API  --->  FastAPI backend  --->  PostgreSQL
Telegram Bot API       <---  notification routes
Cloudflare Tunnel      --->  public dashboard URL
Ollama                <---  local AI health and summaries
Prometheus            <---  backend metrics
Grafana               <---  dashboard visualization
```

Read the detailed design in [docs/architecture.md](docs/architecture.md).

---

## Core Capabilities

### Fixture and Provider Data

The backend stores:

- competition, stage, group, teams, team codes
- kickoff time and venue
- fixture status and score
- provider external ID
- created and updated timestamps
- optional provider-backed rich match detail

Core fixture routes:

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/fixtures` | List and filter fixtures |
| `GET` | `/fixtures/{fixture_id}` | Read one fixture |
| `GET` | `/fixtures/{fixture_id}/detail` | Read fixture plus stored rich detail |
| `POST` | `/fixtures/sync/sample` | Seed deterministic sample fixtures |
| `POST` | `/fixtures/sync/provider` | Sync configured provider data |
| `GET` | `/fixtures/sync/status` | Read latest in-process sync status |

### Standings and Group Analysis

Completed results feed deterministic standings and group analytics:

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/standings` | Group table calculation |
| `GET` | `/insights/groups` | Group leaders, attacks, defences, unbeaten and winless teams |
| `GET` | `/ai/insights` | Structured AI-ready insights and Group Race |

`/ai/insights` is deterministic and does not depend on Ollama availability.

### Provider-Backed Match and Player Detail

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/players/leaders` | Provider-derived scorer and card leaderboards |
| `GET` | `/ai/latest-completed/summary` | Latest completed result with stored incidents and scorers |

The project does not infer assists when the provider does not supply them.

### Local AI With Ollama

The AI layer is local-first and fallback-safe.

```text
Current Windows runtime model: llama3.2:1b
```

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/ai/health` | Confirm local AI availability |
| `GET` | `/ai/fixtures/summary` | Tournament-wide fixture summary |
| `GET` | `/ai/fixtures/{fixture_id}/summary` | Fixture-specific summary |
| `GET` | `/ai/insights` | Deterministic structured insights |
| `GET` | `/ai/latest-completed/summary` | Provider-backed latest result card |

When a live local summary is unavailable or contradicts known fixture state, the API falls back to deterministic, fact-preserving output.

### Telegram and Mobile Access

Telegram support is optional and uses local environment variables.

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/notifications/telegram/status` | Read Telegram configuration readiness |
| `POST` | `/notifications/telegram/test` | Send a test message |

The public dashboard URL can be included in Telegram messages so a match update can open on mobile.

### Monitoring and Observability

The project exposes:

```text
Backend API:    http://localhost:8000
Dashboard:      http://localhost:8000/dashboard
API Docs:       http://localhost:8000/docs
Metrics:        http://localhost:8000/metrics
Prometheus:     http://localhost:9090
Grafana:        http://localhost:3000
```

Observability includes HTTP metrics, fixture-sync metrics, provider sync runtime state, local AI health visibility, Prometheus scraping, and Grafana dashboards.

---

## Tech Stack

| Area | Technology |
|---|---|
| Backend | FastAPI |
| Runtime database | PostgreSQL |
| Dashboard | FastAPI-served HTML, CSS, JavaScript |
| Provider data | Zafronix |
| Local AI | Ollama + Llama |
| Notifications | Telegram Bot API |
| Monitoring | Prometheus + Grafana |
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

## Development and Runtime Workflow

| Machine | Role |
|---|---|
| MacBook Pro | Main development and Git control machine |
| Windows laptop | Docker runtime and demo host |
| VS Code | Main editor |
| Python venv | Local test environment |
| SSH | Remote runtime verification |

### MacBook Development

```bash
cd ~/documents/worldcup-2026-ai-stats
source .venv/bin/activate

pytest -q
git status --short
git diff --check
```

Run the backend locally when needed:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Windows Docker Runtime

From Windows PowerShell:

```powershell
cd "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats"

docker compose up -d --build
docker compose ps

curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/ai/health
curl.exe http://localhost:8000/players/leaders
curl.exe http://localhost:8000/ai/insights
```

Stop the stack:

```powershell
docker compose down
```

### SSH from MacBook to Windows

```bash
ssh windows-laptop
```

Then run the Windows PowerShell commands above. This preserves the preferred model: MacBook for development, Windows for the live Docker runtime.

---

## Configuration

Create a local environment file:

```bash
cp .env.example .env
```

Edit `.env` locally. Do not commit it.

Important configuration groups:

```text
Application version
PostgreSQL connection
Zafronix provider key
Optional API-Football configuration
Telegram bot token and chat ID
Ollama base URL, model, and timeout
Public dashboard URL
```

Never commit:

- `.env`
- provider API keys
- Telegram bot token or chat ID
- Cloudflare credentials
- production database credentials
- host-specific runtime files

---

## Dashboard Demo Flow

1. Open the public dashboard.
2. Use Quick Links to open **AI Insights**.
3. Show the top-two **Group Race** board.
4. Open **Players** and explain that goals and cards are derived from provider event data.
5. Open **AI Summary** and show the provider-backed latest completed result.
6. Open **Fixtures**, select a completed match, and show timeline, statistics, and lineups.
7. Open **Sync** for runtime observability.
8. Show `/docs`, `/metrics`, Prometheus, or Grafana as needed.

For a detailed walkthrough, read [docs/demo-walkthrough.md](docs/demo-walkthrough.md).

> **Safe live-runtime note:** Do not trigger provider sync or rich-detail backfill during a demo unless that is the purpose of the demo. Existing provider data, Telegram notifications, and runtime state may be affected.

---

## Testing

Run the full suite:

```bash
pytest -q
```

Run focused groups:

```bash
pytest backend/tests/test_dashboard.py -q
pytest backend/tests/test_provider_player_leaders.py -q
pytest backend/tests/test_ai_group_race.py -q
pytest backend/tests/test_release_workflow.py -q
```

The v1.11.0 release verification baseline is:

```text
184 passed
```

Python 3.14 may emit FastAPI/Starlette deprecation warnings related to `asyncio.iscoroutinefunction`. They are currently warnings, not failing tests.

---

## Release Workflow

```bash
git checkout main
git pull --ff-only origin main

git checkout -b feature/vX.Y.Z-description
source .venv/bin/activate
pytest -q

git add .
git commit -m "Implement vX.Y.Z"
git push -u origin feature/vX.Y.Z-description
```

Then:

1. Open and review the pull request.
2. Merge into `main`.
3. Pull the merged `main` branch locally.
4. Tag the release.
5. Publish the GitHub release.
6. Delete the merged feature branch locally and remotely.
7. Refresh the Windows runtime from `main`.

Example v1.11.0 tag:

```bash
git checkout main
git pull --ff-only origin main

git tag -a v1.11.0 -m "v1.11.0 Mobile Rich Match Dashboard, Provider Leaders, and Group Race"
git push origin v1.11.0
```

---

## Documentation

- [Architecture](docs/architecture.md)
- [Changelog](docs/changelog.md)
- [Roadmap](docs/roadmap.md)
- [Demo Walkthrough](docs/demo-walkthrough.md)
- [Portfolio Release Summary](docs/portfolio-release.md)
- [v1.11.0 Milestone Guide](docs/v1.11.0-mobile-rich-match-dashboard.md)

---

## Milestone History

| Version | Milestone | Status |
|---|---|---|
| v0.1.0 | Project foundation | Completed |
| v0.2.0 | Fixture and API foundation | Completed |
| v0.3.0 | Provider abstraction | Completed |
| v0.4.0 | Match completion detection | Completed |
| v0.5.0 | Telegram notifications | Completed |
| v0.6.0 | Interactive dashboard | Completed |
| v0.7.0 | Fixture filters and dashboard polish | Completed |
| v0.8.0 | Local Llama summary agent | Completed |
| v1.1.0 | Group standings engine | Completed |
| v1.4.0 | Monitoring and observability foundation | Completed |
| v1.4.1 | Grafana dashboard polish | Completed |
| v1.4.2 | Telegram live-integration hardening | Completed |
| v1.4.3 | Documentation and demo-evidence cleanup | Completed |
| v1.5.0 | Portfolio release polish | Completed |
| v1.6.0 | Real match-data sync improvement | Completed |
| v1.7.0 | Provider sync observability and runtime demo | Completed |
| v1.8.0 | AI insights upgrade | Completed |
| v1.9.0 | Live local AI, Telegram, Cloudflare, and Windows runtime resilience | Completed |
| v1.10.0 | Match detail dashboard and README polish | Completed |
| v1.11.0 | Mobile rich match dashboard, provider leaders, and Group Race | Completed |

---

## Current Limitations

- The application is self-hosted and local-first, not a production SaaS deployment.
- Provider coverage depends on the configured provider and its payload quality.
- Assist leaderboards remain unavailable until the provider supplies assist events.
- Local Llama requires Ollama to be running on the Windows host.
- The default local stack does not implement production authentication or hardened secret management.
- Dashboard data is a current provider snapshot and changes after future syncs.

---

## Security Notes

Keep all secrets local. This repository should contain safe placeholders only.

```text
Do not commit .env files, API keys, bot tokens, chat IDs, Cloudflare credentials,
or host-specific production settings.
```

---

## License

Personal portfolio and learning project.
