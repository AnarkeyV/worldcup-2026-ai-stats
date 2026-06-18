# ⚽ World Cup 2026 AI Stats Dashboard

![FastAPI](https://img.shields.io/badge/backend-FastAPI-green)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-blue)
![Dashboard](https://img.shields.io/badge/dashboard-FastAPI%20Static%20Dashboard-skyblue)
![Docker](https://img.shields.io/badge/container-Docker-blue)
![Python](https://img.shields.io/badge/python-3.14-yellow)
![Version](https://img.shields.io/badge/version-v1.4.3-purple)
![Tests](https://img.shields.io/badge/tests-114%20passed-brightgreen)

A self-hosted, containerized, AI-assisted World Cup 2026 match tracking and insights platform built with **FastAPI**, **SQLAlchemy**, **PostgreSQL-ready database configuration**, **Docker Compose**, a **FastAPI static dashboard**, **Prometheus**, **Grafana**, **Telegram Bot API notifications**, and a **local-first Llama/Ollama AI summary workflow**.

This project is intentionally being built in public, milestone by milestone, to demonstrate backend development, API integration, database design, testing, DevOps fundamentals, notification workflows, dashboard development, deterministic AI-assisted summaries, local-first AI integration, observability, and practical sports analytics.

---

## 📌 Current Version

**v1.4.3 — Documentation and Demo Evidence Cleanup**

This milestone refreshes the project documentation after the Grafana dashboard polish and live Telegram API integration milestones. It aligns the README, changelog, roadmap, service URLs, screenshot evidence notes, and release metadata with the current working application.

The application now supports:

- fixture syncing
- fixture filtering
- match completion detection
- Telegram notification workflows
- real Telegram Bot API delivery testing
- interactive dashboard cards
- dashboard group standings
- dashboard group insights
- dashboard player statistics cards
- `/standings` API endpoint
- `/insights/groups` API endpoint
- `/players/stats` API endpoint
- `/players/stats/sync/sample` sample sync endpoint
- `/metrics` Prometheus metrics endpoint
- Prometheus container in Docker Compose
- Grafana container in Docker Compose
- provisioned Grafana Prometheus datasource
- provisioned Grafana dashboard
- deterministic AI summaries
- standings-aware tournament summaries
- insights-aware tournament summaries
- local Llama/Ollama health checks
- safe fallback behavior when optional services are not configured

---

## 🎯 Project Purpose

The World Cup is a strong use case for a practical DevOps and backend portfolio project because match data changes over time.

Fixtures begin as scheduled, become live, then become completed. Once completed, downstream workflows can be triggered, such as:

1. updating the database
2. detecting newly completed matches
3. sending notifications
4. updating standings
5. generating summaries
6. exposing metrics
7. viewing observability dashboards
8. demonstrating operational readiness

This project shows how an application can grow from a simple health endpoint into a more complete backend, dashboard, notification, monitoring, and AI-assisted analytics platform.

---

## 🧭 Project Goals

This project is designed to demonstrate:

- backend API development with FastAPI
- SQLAlchemy database modelling
- PostgreSQL-ready application configuration
- Docker Compose local deployment
- API provider integration patterns
- sample-data fallback design
- match status transition handling
- Telegram notification workflows
- local-first AI integration patterns
- deterministic summary generation
- dashboard development with HTML, CSS, and JavaScript
- player and team analytics
- Prometheus metrics instrumentation
- Grafana dashboard provisioning
- automated tests with pytest
- safe secret handling with `.env`
- public portfolio documentation

---

## 🧱 Architecture Overview

```text
User / Browser
    |
    +--> FastAPI Static Dashboard
    |       |
    |       +--> /dashboard
    |       +--> /fixtures
    |       +--> /standings
    |       +--> /insights/groups
    |       +--> /players/stats
    |       +--> /ai/fixtures/summary
    |
    +--> FastAPI Backend API
            |
            +--> Fixture Routes
            |       +--> sample sync
            |       +--> provider sync
            |       +--> fixture filtering
            |
            +--> Standings Routes
            |       +--> group table calculation
            |
            +--> Insights Routes
            |       +--> group analytics
            |
            +--> Player Stats Routes
            |       +--> player sample sync
            |       +--> player stat filtering/sorting
            |
            +--> Notification Routes
            |       +--> Telegram readiness status
            |       +--> Telegram test notification
            |
            +--> Metrics Route
            |       +--> Prometheus metrics
            |
            +--> AI Routes
                    +--> deterministic summaries
                    +--> local Llama/Ollama health checks
```

---

## 🔄 Data and Notification Flow

### Sample Fixture Sync Flow

```text
POST /fixtures/sync/sample
    |
    +--> load sample fixtures
    +--> insert or update database records
    +--> detect newly completed fixtures
    +--> send Telegram notifications if configured
    +--> update Prometheus metrics
    +--> return sync and notification summary
```

### Provider Fixture Sync Flow

```text
POST /fixtures/sync/provider
    |
    +--> API-Football provider client
    +--> normalize provider fixture response
    +--> insert or update database records
    +--> detect newly completed fixtures
    +--> send Telegram notifications if configured
    +--> update Prometheus metrics
    +--> return provider sync and notification summary
```

### Telegram Notification Flow

```text
Completed fixture detected
    |
    +--> build_completed_fixture_message()
    +--> check TELEGRAM_BOT_TOKEN
    +--> check TELEGRAM_CHAT_ID
    +--> send message using Telegram Bot API
    +--> record sent/skipped/failed metric
    +--> return notification result
```

### Observability Flow

```text
FastAPI Backend
    |
    +--> /metrics
            |
            +--> Prometheus scrapes backend:8000/metrics
                    |
                    +--> Grafana reads from Prometheus
                            |
                            +--> World Cup overview dashboard
```

---

## 🧩 Main Features

### Fixtures

- list fixtures
- get single fixture
- sync sample fixtures
- sync provider fixtures
- filter by group
- filter by status
- search by team name or code
- detect newly completed fixtures during sync

### Standings

- calculate group standings
- expose standings through API
- show standings in dashboard
- support standings-aware AI summaries

### Group Insights

- generate group-level analytics
- expose insight cards through API
- show insight cards in dashboard
- support insights-aware tournament summaries

### Player Statistics

- sync sample player statistics
- expose player statistics through API
- filter by team
- filter by group
- sort by goals, assists, cards, minutes, player name, and team
- show player statistics in dashboard cards

### Telegram Notifications

- format completed match notifications
- safely skip sending when credentials are missing
- expose Telegram readiness endpoint
- send real Telegram Bot API test messages when configured
- handle Telegram API/network failures safely
- record notification metrics

### AI Summary Layer

- deterministic fixture summaries
- standings-aware tournament summaries
- insights-aware tournament summaries
- local Llama/Ollama health checks
- safe fallback behavior when local AI is unavailable

### Monitoring and Observability

- Prometheus metrics endpoint
- Prometheus Docker Compose service
- Prometheus scrape config
- Grafana Docker Compose service
- Grafana datasource provisioning
- Grafana dashboard provisioning
- useful backend runtime panels

---

## 🛠️ Tech Stack

| Area | Technology |
|---|---|
| Backend API | FastAPI |
| Database | PostgreSQL-ready configuration |
| ORM | SQLAlchemy |
| Dashboard | FastAPI static HTML/CSS/JS |
| Legacy Dashboard | Streamlit |
| Containerization | Docker Compose |
| Testing | pytest |
| HTTP Client | httpx, urllib standard library |
| Settings | pydantic-settings |
| CI | GitHub Actions |
| Notifications | Telegram Bot API |
| Local AI Health | Ollama / Llama |
| Deterministic Summaries | Rules-based Python service logic |
| Metrics | Prometheus client |
| Monitoring | Prometheus |
| Observability Dashboard | Grafana |

---

## 📁 Project Structure

```text
worldcup-2026-ai-stats/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── fixture.py
│   │   │   └── player_stat.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── api_football.py
│   │   │   └── base.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── ai.py
│   │   │   ├── dashboard.py
│   │   │   ├── fixtures.py
│   │   │   ├── insights.py
│   │   │   ├── metrics.py
│   │   │   ├── notifications.py
│   │   │   ├── players.py
│   │   │   └── standings.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── fixture_sync_service.py
│   │   │   ├── insights_service.py
│   │   │   ├── local_llama_client.py
│   │   │   ├── metrics_service.py
│   │   │   ├── player_stats_sample_data.py
│   │   │   ├── player_stats_service.py
│   │   │   ├── sample_data.py
│   │   │   ├── standings_service.py
│   │   │   └── telegram_notifier.py
│   │   ├── static/
│   │   │   ├── dashboard.css
│   │   │   ├── dashboard.html
│   │   │   └── dashboard.js
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_ai_routes.py
│   │   ├── test_api_football_provider.py
│   │   ├── test_dashboard.py
│   │   ├── test_fixture_sync_service.py
│   │   ├── test_fixtures.py
│   │   ├── test_health.py
│   │   ├── test_insights_routes.py
│   │   ├── test_insights_service.py
│   │   ├── test_local_llama_client.py
│   │   ├── test_metrics.py
│   │   ├── test_monitoring_config.py
│   │   ├── test_notifications.py
│   │   ├── test_player_stats_routes.py
│   │   ├── test_player_stats_service.py
│   │   ├── test_release_workflow.py
│   │   ├── test_standings_routes.py
│   │   ├── test_standings_service.py
│   │   └── test_telegram_notifier.py
│   ├── Dockerfile
│   ├── pytest.ini
│   └── requirements.txt
├── dashboard/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── monitoring/
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   └── worldcup-overview.json
│   │   └── provisioning/
│   │       ├── dashboards/
│   │       │   └── dashboards.yml
│   │       └── datasources/
│   │           └── prometheus.yml
│   └── prometheus.yml
├── docs/
│   ├── architecture.md
│   ├── changelog.md
│   └── roadmap.md
├── infra/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── VERSION
```

---

## 🚀 Getting Started

### Prerequisites

Install the following:

- Git
- Docker Desktop
- Python 3.14 or compatible Python 3 version
- VS Code or another code editor

Optional:

- API-Football / API-Sports account for real provider syncing
- Telegram bot token and chat ID for real Telegram notification testing
- Ollama for local AI health testing and future local AI workflows
- Postman or curl for endpoint testing

---

## 📦 Clone the Repository

```bash
git clone https://github.com/AnarkeyV/worldcup-2026-ai-stats.git
cd worldcup-2026-ai-stats
```

---

## 🔐 Environment Setup

Create your local `.env` file from the example file.

### macOS / Linux

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

The `.env` file is ignored by Git and should never be committed.

The `.env.example` file is safe to commit because it only contains placeholders.

---

## 🧾 Environment Variables

Current `.env.example`:

```env
# App
APP_NAME=World Cup 2026 AI Stats
APP_ENV=development
APP_VERSION=1.4.3

# Database
POSTGRES_USER=worldcup
POSTGRES_PASSWORD=worldcup
POSTGRES_DB=worldcup
DATABASE_URL=postgresql+psycopg://worldcup:worldcup@postgres:5432/worldcup

# Dashboard
DASHBOARD_PORT=8501
BACKEND_API_URL=http://backend:8000

# Football API Provider
FOOTBALL_API_PROVIDER=api_football
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io
API_FOOTBALL_KEY=replace_me
API_FOOTBALL_WORLD_CUP_LEAGUE_ID=1
API_FOOTBALL_SEASON=2026

# Telegram
TELEGRAM_BOT_TOKEN=replace_me
TELEGRAM_CHAT_ID=replace_me

# Local Llama / Ollama
LLAMA_BASE_URL=http://127.0.0.1:11434
LLAMA_MODEL=llama3.2:1b
LLAMA_TIMEOUT_SECONDS=60

# Public URL
PUBLIC_DASHBOARD_URL=http://localhost:8000/dashboard
```

---

## 🐳 Run with Docker Compose

From the project root:

```bash
docker compose up --build
```

Detached mode:

```bash
docker compose up -d --build
```

Stop:

```bash
docker compose down
```

Stop and remove volumes:

```bash
docker compose down -v
```

Use `docker compose down -v` carefully because it removes the database, Prometheus, and Grafana volumes.

---

## 🌐 Access the Services

| Service | URL |
|---|---|
| Backend API | http://localhost:8000 |
| Backend Health Check | http://localhost:8000/health |
| API Docs | http://localhost:8000/docs |
| FastAPI Dashboard | http://localhost:8000/dashboard |
| Fixtures API | http://localhost:8000/fixtures |
| Standings API | http://localhost:8000/standings |
| Group Insights API | http://localhost:8000/insights/groups |
| Player Stats API | http://localhost:8000/players/stats |
| AI Summary API | http://localhost:8000/ai/fixtures/summary |
| Metrics API | http://localhost:8000/metrics |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Legacy Streamlit Dashboard | http://localhost:18501 |

---

## 🖥️ MacBook + Windows Laptop Workflow

The project can be developed on a MacBook while running Docker Compose on a Windows laptop.

Typical workflow:

```text
MacBook
    |
    +--> VS Code / Git / pytest / browser testing
    +--> SSH session into Windows laptop
            |
            +--> Docker Compose runtime
            +--> backend, dashboard, postgres, prometheus, grafana
```

Useful SSH forwarding example:

```bash
ssh -L 8000:localhost:8000 -L 9090:localhost:9090 -L 3000:localhost:3000 -L 18501:localhost:18501 <windows-user>@<windows-host>
```

Then open these on the MacBook browser:

```text
http://localhost:8000/docs
http://localhost:8000/dashboard
http://localhost:9090
http://localhost:3000
http://localhost:18501
```

---

## 🧪 Run Tests Locally

From the project root:

```bash
pytest -q
```

Or from the backend folder:

```bash
cd backend
pytest -q
```

Current expected result:

```text
114 passed
```

---

## 🏥 Health Check

```bash
curl http://localhost:8000/health
```

Example response:

```json
{
  "status": "healthy",
  "service": "backend",
  "version": "1.4.3"
}
```

---

## 📡 Core API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Root API information |
| GET | `/health` | Backend health check |
| GET | `/dashboard` | Static dashboard |
| GET | `/fixtures` | List fixtures |
| GET | `/fixtures/{fixture_id}` | Get one fixture |
| POST | `/fixtures/sync/sample` | Sync sample fixture data |
| POST | `/fixtures/sync/provider` | Sync provider fixture data |
| GET | `/standings` | Get group standings |
| GET | `/insights/groups` | Get group insights |
| GET | `/players/stats` | Get player statistics |
| POST | `/players/stats/sync/sample` | Sync sample player statistics |
| GET | `/ai/health` | Check local Llama/Ollama health |
| GET | `/ai/fixtures/summary` | Generate fixture summary |
| GET | `/metrics` | Prometheus metrics |
| GET | `/notifications/telegram/status` | Check Telegram readiness |
| POST | `/notifications/telegram/test` | Send Telegram test notification |

---

## ⚽ Fixture API Examples

### List Fixtures

```bash
curl http://localhost:8000/fixtures
```

### Filter by Group

```bash
curl "http://localhost:8000/fixtures?group_name=Group%20A"
```

### Filter by Status

```bash
curl "http://localhost:8000/fixtures?status=complete"
```

### Search by Team

```bash
curl "http://localhost:8000/fixtures?team=Mexico"
```

### Sync Sample Fixtures

```bash
curl -X POST http://localhost:8000/fixtures/sync/sample
```

---

## 🧮 Standings and Insights

### Standings

```bash
curl http://localhost:8000/standings
```

### Group Insights

```bash
curl http://localhost:8000/insights/groups
```

These endpoints power the dashboard standings table, insight cards, and standings-aware summaries.

---

## 👟 Player Statistics

### Sync Sample Player Statistics

```bash
curl -X POST http://localhost:8000/players/stats/sync/sample
```

### List Player Statistics

```bash
curl http://localhost:8000/players/stats
```

### Filter by Team

```bash
curl "http://localhost:8000/players/stats?team=Mexico"
```

### Sort by Goals

```bash
curl "http://localhost:8000/players/stats?sort_by=goals"
```

---

## 📣 Telegram Notifications

Telegram notifications are handled through:

```text
backend/app/services/telegram_notifier.py
```

Main functions:

```text
build_completed_fixture_message()
send_telegram_message()
send_completed_fixture_notifications()
```

The Telegram readiness endpoint is:

```http
GET /notifications/telegram/status
```

This endpoint safely reports whether Telegram credentials are configured without exposing the real bot token or chat ID.

Example response without credentials:

```json
{
  "channel": "telegram",
  "bot_token_configured": false,
  "chat_id_configured": false,
  "ready": false
}
```

Example response with local credentials configured:

```json
{
  "channel": "telegram",
  "bot_token_configured": true,
  "chat_id_configured": true,
  "ready": true
}
```

The test notification endpoint is:

```http
POST /notifications/telegram/test
```

This endpoint builds a sample completed-match message and attempts to send it using local Telegram credentials.

If credentials are missing, the endpoint returns a safe error response such as:

```json
{
  "detail": "TELEGRAM_BOT_TOKEN is not configured."
}
```

or:

```json
{
  "detail": "TELEGRAM_CHAT_ID is not configured."
}
```

If Telegram is configured but the Telegram API request fails, the application returns a controlled failure response instead of crashing.

Example Telegram message format:

```text
🏁 Match Completed

FIFA World Cup 2026
Group Stage

Mexico 2 - 0 South Africa

Venue: Estadio Azteca
```

Real Telegram bot tokens and chat IDs must only be stored in local `.env` files or deployment secrets.

Never commit Telegram credentials.

---

## 🤖 AI Summary Layer

The AI summary layer is currently deterministic for safer, factual dashboard output.

Current summary behavior:

- uses stored fixture data
- includes total fixtures
- includes completed fixtures
- includes upcoming fixtures
- includes standings context
- includes group insights context
- avoids making unsupported claims
- works even when local Llama is unavailable

Local Llama/Ollama health can be checked with:

```bash
curl http://localhost:8000/ai/health
```

Fixture summary endpoint:

```bash
curl http://localhost:8000/ai/fixtures/summary
```

---

## 📈 Prometheus Metrics

The backend exposes Prometheus metrics at:

```text
http://localhost:8000/metrics
```

Prometheus is available at:

```text
http://localhost:9090
```

Prometheus scrapes the backend service at:

```text
backend:8000/metrics
```

Current custom metrics include:

```text
worldcup_app_info
worldcup_http_requests_total
worldcup_http_request_duration_seconds
worldcup_fixture_sync_runs_total
worldcup_fixture_sync_created_total
worldcup_fixture_sync_updated_total
worldcup_fixture_sync_newly_completed_total
worldcup_player_stats_sync_runs_total
worldcup_player_stats_sync_created_total
worldcup_player_stats_sync_updated_total
worldcup_notification_results_total
worldcup_ai_summary_requests_total
```

---

## 📊 Grafana Dashboard

Grafana is available at:

```text
http://localhost:3000
```

The Grafana service is provisioned with:

- Prometheus datasource
- World Cup 2026 overview dashboard
- backend target status panel
- scrape sample panel
- scrape duration panel
- Python runtime panels
- backend memory panels
- backend CPU panel
- Python garbage collection panels
- backend metrics inventory panel

Provisioning files:

```text
monitoring/grafana/provisioning/datasources/prometheus.yml
monitoring/grafana/provisioning/dashboards/dashboards.yml
monitoring/grafana/dashboards/worldcup-overview.json
```

Default local Grafana login:

```text
Username: admin
Password: admin
```

The project also enables anonymous viewer access for local demo convenience.

---

## 🔐 Security Notes

- Never commit `.env`
- Never commit real API keys
- Never commit real Telegram bot tokens
- Never commit Telegram chat IDs
- Never paste real secrets into screenshots, README files, commits, or public issues
- Use `.env.example` only for safe placeholders
- Use deployment secrets for production-style environments
- The Telegram readiness endpoint only exposes boolean readiness flags

---

## 🧯 Troubleshooting Notes

### Windows Docker credential issue

If Docker image pulls fail through SSH with a credential helper error, pull the image directly from Windows PowerShell.

Example:

```powershell
docker pull grafana/grafana:11.4.0
```

### Windows port bind issue

On the Windows laptop, host ports `8501` and `8502` may be blocked or reserved.

The legacy Streamlit dashboard uses host port:

```text
18501
```

Open it at:

```text
http://localhost:18501
```

### Docker container name conflict

If Docker reports that a World Cup container name is already in use:

```powershell
docker compose down --remove-orphans
docker rm -f worldcup-backend worldcup-dashboard worldcup-postgres worldcup-prometheus worldcup-grafana
```

Then start again:

```powershell
docker compose up -d --build
```

Do not remove Docker volumes unless you intentionally want to reset stored data.

---

## 📸 Screenshots

Demo screenshots are stored outside the repository on the local development machine.

Current local screenshot evidence folders:

```text
~/documents/world-cup-ai-stats-screenshots/v1.4.0-demo
~/documents/world-cup-ai-stats-screenshots/v1.4.1-demo
~/documents/world-cup-ai-stats-screenshots/v1.4.2-demo
```

Recommended screenshot evidence by milestone:

### v1.4.0 — Monitoring and Observability Foundation

- backend health check
- API docs
- FastAPI dashboard
- Prometheus targets page
- Prometheus metrics query
- Docker Compose services running

### v1.4.1 — Grafana Dashboard Polish

- Grafana dashboard overview
- Docker Compose services with Grafana running
- Streamlit dashboard on port `18501`
- Prometheus graph page
- FastAPI docs
- backend dashboard

### v1.4.2 — Telegram API Live Integration Hardening

- Telegram status endpoint showing `ready: true`
- Telegram test endpoint success response
- Telegram bot receiving the test match notification
- FastAPI notification endpoints in API docs

Do not commit screenshots that expose secrets, tokens, chat IDs, private account details, or local-only credentials.

Suggested repository folder for future public-safe screenshots:

```text
docs/images/
```

---

## 📚 Documentation

Additional project documentation:

```text
docs/architecture.md
docs/changelog.md
docs/roadmap.md
```

---

## 🧾 Release History

### v1.4.3 — Documentation and Demo Evidence Cleanup

Completed:

- Updated README version badge and current milestone
- Updated service URLs for Grafana and Streamlit dashboard access
- Updated Telegram documentation with readiness endpoint and live testing notes
- Updated observability documentation to reflect Prometheus and Grafana
- Added screenshot evidence folder references
- Updated changelog and roadmap to reflect current project state
- Bumped release metadata to `1.4.3`

---

### v1.4.2 — Telegram API Live Integration Hardening

Completed:

- Added Telegram readiness endpoint
- Added safe boolean credential readiness reporting
- Added empty Telegram message validation
- Added Telegram HTTP status error handling
- Added Telegram request/network error handling
- Added Telegram rejected-message handling
- Added `TelegramNotificationError`
- Updated fixture sync notification handling for failed Telegram API calls
- Expanded Telegram service tests
- Expanded notification route tests
- Verified real Telegram Bot API message delivery locally
- Full backend test suite passing: `114 passed`

---

### v1.4.1 — Grafana Dashboard Polish

Completed:

- Added Grafana service to Docker Compose
- Added Grafana provisioning for Prometheus datasource
- Added provisioned World Cup overview dashboard
- Added backend target status panel
- Added scrape sample and scrape duration panels
- Added Python runtime metrics panels
- Added backend memory and CPU panels
- Added Python garbage collection panels
- Added backend metrics inventory panel
- Updated local dashboard access to use host port `18501`
- Verified Grafana locally through Docker Compose
- Verified Prometheus target health
- Captured v1.4.1 demo screenshots

---

### v1.4.0 — Monitoring and Observability Foundation

Completed:

- Added `prometheus-client` dependency
- Added `backend/app/services/metrics_service.py`
- Added `backend/app/routes/metrics.py`
- Added `GET /metrics` endpoint
- Added HTTP request count metrics
- Added HTTP request duration metrics
- Added fixture sync run metrics
- Added fixture sync created/updated/newly-completed metrics
- Added player stats sync metrics
- Added notification result metrics
- Added AI summary request metrics
- Added `/metrics` link to the root API response
- Added Prometheus service to `docker-compose.yml`
- Added `monitoring/prometheus.yml`
- Added persistent `worldcup_prometheus_data` volume
- Added metrics endpoint tests
- Added monitoring configuration tests
- Validated backend Docker image build
- Validated dashboard Docker image build
- Validated Docker Compose configuration
- Full backend test suite passing: `105 passed`

---

## 📊 Version History

| Version | Description | Status |
|---|---|---|
| v0.1.0 | Project foundation with Docker, FastAPI, Streamlit, PostgreSQL, pytest, and CI | Completed |
| v0.1.1 | README and documentation polish | Completed |
| v0.2.0 | Football API integration foundation with fixture database, sample sync, dashboard table, and endpoint tests | Completed |
| v0.3.0 | Real football API provider layer, provider client, fixture sync service, provider sync endpoint, and mocked tests | Completed |
| v0.4.0 | Match completion detection during fixture sync with response fields and tests | Completed |
| v0.5.0 | Telegram notification service, test endpoint, completed fixture notification helper, and sync wiring | Completed |
| v0.6.0 | Interactive dashboard with fixture cards, summary stats, static assets, dashboard route, filtering UI, and tests | Completed |
| v0.7.0 | API-level fixture filters, dashboard query integration, team search, group/status filters, and expanded tests | Completed |
| v0.8.0 | Local Llama/Ollama summary agent with AI endpoints and dashboard summary button | Completed |
| v1.0.0 | AI summary quality, deterministic summaries, and dashboard polish | Completed |
| v1.1.0 | Group standings engine, standings API, dashboard standings table, and standings-aware AI summary | Completed |
| v1.1.1 | README and project documentation refresh | Completed |
| v1.1.2 | Version and container workflow cleanup | Completed |
| v1.2.0 | Team insights and group analytics | Completed |
| v1.3.0 | Player-level statistics foundation | Completed |
| v1.4.0 | Monitoring and observability foundation with Prometheus metrics and Docker Compose monitoring service | Completed |
| v1.4.1 | Grafana dashboard polish with provisioned Prometheus datasource and dashboard panels | Completed |
| v1.4.2 | Telegram API live integration hardening with readiness endpoint and real bot delivery validation | Completed |
| v1.4.3 | Documentation and demo evidence cleanup for README, changelog, roadmap, ports, and screenshots | Completed |
| v1.5.0 | Portfolio release polish | Planned |

---

## 🧭 Roadmap Summary

Next planned milestones:

- **v1.5.0 — Portfolio Release Polish**
- **v1.6.0 — Real Match Data Sync Improvement**
- **v1.7.0 — AI Insights Upgrade**
- **v1.8.0 — Portfolio Demo Polish**

See the full roadmap in:

```text
docs/roadmap.md
```

---

## 📌 Project Status

Current status:

```text
v1.4.3 — Documentation and Demo Evidence Cleanup
```

The backend now supports fixture sync, fixture filtering, completed-match detection, Telegram notification workflows, real Telegram Bot API delivery testing, group standings, dashboard standings, group insights, dashboard insight cards, player statistics, dashboard player stat cards, Prometheus metrics, Docker Compose Prometheus monitoring, provisioned Grafana dashboards, deterministic AI summaries, standings-aware and insights-aware tournament summaries, and Local Llama health checks.

Sample fixtures and sample player statistics remain available as safe fallbacks for local development, public GitHub users, and testing without provider, Telegram, or external AI credentials.
