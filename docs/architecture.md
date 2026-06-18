# Architecture

## Overview

World Cup 2026 AI Stats Dashboard is a containerized football analytics platform built around a FastAPI backend, PostgreSQL database, dashboard layer, local AI summary workflow, Telegram notification integration, and Prometheus/Grafana observability stack.

This architecture document reflects the current **v1.7.0 — Provider Sync Observability & Runtime Demo** release.

The project is designed as a local-first portfolio system that can be explained clearly during interviews, recruiter reviews, and technical walkthroughs.

---

## Current Architecture - v1.7.0

```text
+--------------------------+
| User / Reviewer          |
| Browser / API Client     |
+------------+-------------+
             |
             v
+--------------------------+        +--------------------------+
| Streamlit Dashboard      |        | Backend Static Dashboard |
| Host: localhost:18501    |        | Route: /dashboard        |
| Container: dashboard     |        | Served by FastAPI        |
+------------+-------------+        +------------+-------------+
             |                                   |
             +-------------------+---------------+
                                 |
                                 v
+----------------------------------------------------------------+
| FastAPI Backend                                                |
| Container: worldcup-backend                                    |
| Host: localhost:8000                                           |
|                                                                |
| Responsibilities:                                              |
| - API routes                                                   |
| - sample and provider fixture sync                             |
| - standings calculation                                        |
| - group insights                                               |
| - player statistics                                            |
| - local AI summary orchestration                               |
| - Telegram notification orchestration                          |
| - Prometheus metrics                                           |
+--------------------------+-------------------------------------+
                           |
              +------------+-------------+
              |                          |
              v                          v
+--------------------------+   +-------------------------------+
| PostgreSQL               |   | Local Llama / Ollama          |
| Container: postgres      |   | Host service, optional        |
| Host: localhost:5432     |   | Default: localhost:11434      |
+--------------------------+   +-------------------------------+

+--------------------------+   +-------------------------------+
| Prometheus               |-->| Grafana                       |
| Container: prometheus    |   | Container: grafana            |
| Host: localhost:9090     |   | Host: localhost:3000          |
+--------------------------+   +-------------------------------+

External integrations:
- API-Football provider, optional
- Telegram Bot API, optional
```

---

## Runtime Services

The main Docker Compose stack contains five runtime services.

| Service | Container | Purpose | Host Port |
|---|---|---|---|
| Backend | `worldcup-backend` | FastAPI API and static dashboard | `8000` |
| Dashboard | `worldcup-dashboard` | Streamlit dashboard | `18501` |
| PostgreSQL | `worldcup-postgres` | Persistent database | `5432` |
| Prometheus | `worldcup-prometheus` | Metrics scraping | `9090` |
| Grafana | `worldcup-grafana` | Metrics visualization | `3000` |

The dashboard container maps host port `18501` to container port `8501` to avoid common Windows/macOS conflicts with port `8501`.

---

## Current API Surface

### Built-in Documentation Routes

```text
/openapi.json
/docs
/docs/oauth2-redirect
/redoc
```

### Static Mount

```text
/static
```

### Application Routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/` | Root project status |
| `GET` | `/health` | Backend health check |
| `GET` | `/dashboard` | Static dashboard page |
| `GET` | `/metrics` | Prometheus metrics |

### Fixture Routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/fixtures` | List and filter fixtures |
| `GET` | `/fixtures/{fixture_id}` | Get fixture by ID |
| `POST` | `/fixtures/sync/sample` | Sync sample fixture data |
| `POST` | `/fixtures/sync/provider` | Sync provider-backed fixture data |

### Standings and Insights Routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/standings` | List calculated standings |
| `GET` | `/insights/groups` | List group insights |

### Player Statistics Routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/players/stats` | List player statistics |
| `POST` | `/players/stats/sync/sample` | Sync sample player statistics |

### AI Routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/ai/health` | Check AI summary layer readiness |
| `GET` | `/ai/fixtures/summary` | Generate fixture summary |
| `GET` | `/ai/fixtures/{fixture_id}/summary` | Generate fixture-specific summary |

### Notification Routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/notifications/telegram/status` | Check Telegram configuration status |
| `POST` | `/notifications/telegram/test` | Send Telegram test notification |

---

## Backend Structure

```text
backend/
├── app/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models/
│   ├── providers/
│   ├── routes/
│   │   ├── ai.py
│   │   ├── dashboard.py
│   │   ├── fixtures.py
│   │   ├── insights.py
│   │   ├── metrics.py
│   │   ├── notifications.py
│   │   ├── players.py
│   │   └── standings.py
│   ├── services/
│   │   ├── fixture_sync_service.py
│   │   ├── insights_service.py
│   │   ├── local_llama_client.py
│   │   ├── metrics_service.py
│   │   ├── player_stats_sample_data.py
│   │   ├── player_stats_service.py
│   │   ├── sample_data.py
│   │   ├── standings_service.py
│   │   └── telegram_notifier.py
│   └── static/
│       ├── dashboard.css
│       ├── dashboard.html
│       └── dashboard.js
├── tests/
├── Dockerfile
├── pytest.ini
└── requirements.txt
```

---

## Data Flow

### Fixture Sync Flow

```text
API caller
   |
   v
POST /fixtures/sync/sample
or
POST /fixtures/sync/provider
   |
   v
Fixture sync route
   |
   v
Fixture sync service
   |
   v
Sample data or provider adapter
   |
   v
Database write/update
   |
   v
Fixtures available to routes, dashboard, standings, insights, metrics
```

---

## Provider Sync Flow

```text
API caller
   |
   v
POST /fixtures/sync/provider
   |
   v
Provider configuration
   |
   v
API-Football provider adapter
   |
   v
External provider response
   |
   v
Normalized fixture data
   |
   v
Status normalization, team-code fallback, invalid-row skipping
   |
   v
Fixture sync service
   |
   v
Database persistence
```

Provider configuration is controlled through environment variables:

```env
FOOTBALL_API_PROVIDER=api_football
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io
API_FOOTBALL_KEY=replace_me
API_FOOTBALL_WORLD_CUP_LEAGUE_ID=1
API_FOOTBALL_SEASON=2026
```

In v1.6.0, provider sync adds a stronger normalization layer before database persistence:

- API-Football status values such as `NS`, `FT`, `AET`, and `PEN` are converted into dashboard-friendly status values such as `scheduled` and `complete`.
- Missing provider team codes are filled using known overrides or safe derived fallbacks.
- Incomplete provider rows are skipped when required fields such as fixture ID, kickoff time, home team, or away team are missing.
- Provider request failures and invalid payloads are wrapped into clear provider errors.
- `/fixtures/sync/provider` returns `502` for provider-side failures, `400` for missing API key configuration, and `503` for database failures.


---

## Standings Flow

```text
Completed fixtures
   |
   v
Standings service
   |
   v
Points, goals, goal difference, W/D/L
   |
   v
GET /standings
   |
   v
Dashboard and API consumers
```

---

## Insights Flow

```text
Fixtures + standings
   |
   v
Insights service
   |
   v
Group-level analytics
   |
   v
GET /insights/groups
   |
   v
Dashboard and API consumers
```

---

## Player Statistics Flow

```text
Sample player stats sync
   |
   v
Player stats service
   |
   v
Stored player-level statistics
   |
   v
GET /players/stats
   |
   v
Dashboard, API consumers, portfolio demo
```

---

## AI Summary Flow

```text
Fixture data
   |
   v
AI route
   |
   v
Local Llama client
   |
   v
Ollama / local model
   |
   v
Generated summary or safe fallback response
```

Environment variables:

```env
LLAMA_BASE_URL=http://127.0.0.1:11434
LLAMA_MODEL=llama3.2:1b
LLAMA_TIMEOUT_SECONDS=60
```

The AI layer is intentionally local-first so it can be demonstrated without sending data to a cloud LLM provider.

---

## Telegram Notification Flow

```text
Notification route
   |
   v
Telegram notifier service
   |
   v
Telegram Bot API
   |
   v
Configured chat
```

Environment variables:

```env
TELEGRAM_BOT_TOKEN=replace_me
TELEGRAM_CHAT_ID=replace_me
PUBLIC_DASHBOARD_URL=http://localhost:8000/dashboard
```

The notification layer is optional. The app should still run when Telegram is not configured.

---

## Observability Flow

```text
FastAPI backend
   |
   v
GET /metrics
   |
   v
Prometheus
   |
   v
Grafana datasource
   |
   v
Provisioned Grafana dashboard
```

Monitoring files:

```text
monitoring/prometheus.yml
monitoring/grafana/dashboards/worldcup-overview.json
monitoring/grafana/provisioning/dashboards/dashboards.yml
monitoring/grafana/provisioning/datasources/prometheus.yml
```

The observability stack demonstrates:

- metrics exposure
- scrape configuration
- dashboard provisioning
- version-aware app metrics
- local monitoring demo readiness

---

## Dashboard Architecture

The project currently includes two dashboard-facing layers.

### Backend Static Dashboard

Served by FastAPI:

```text
GET /dashboard
```

Static assets:

```text
backend/app/static/dashboard.html
backend/app/static/dashboard.css
backend/app/static/dashboard.js
```

This is useful for a simple browser-based demo from the backend service.

### Streamlit Dashboard

Served by the `dashboard` Docker Compose service:

```text
http://localhost:18501
```

Files:

```text
dashboard/app.py
dashboard/Dockerfile
dashboard/requirements.txt
```

This is useful for a more dashboard-like portfolio view.

---

## Database Architecture

The project uses PostgreSQL through Docker Compose.

```text
Service: postgres
Container: worldcup-postgres
Database: worldcup
User: worldcup
Host port: 5432
```

Runtime connection string:

```env
DATABASE_URL=postgresql+psycopg://worldcup:worldcup@postgres:5432/worldcup
```

The database is backed by a Docker volume:

```text
worldcup_postgres_data
```

This preserves data across container restarts unless volumes are removed.

---

## Configuration Architecture

Configuration is managed through environment variables.

Primary files:

```text
.env.example
.env
backend/app/config.py
VERSION
```

Version consistency is protected by tests that compare:

- `VERSION`
- `.env.example` `APP_VERSION`
- `backend/app/config.py` default `app_version`

This reduces the chance of publishing a release with mismatched metadata.

---

## Test Architecture

The project uses pytest as its test runner.

Current baseline:

```text
138 passed
```

Test coverage areas include:

- release workflow
- health route
- fixture routes
- fixture sync service
- provider adapter
- dashboard route
- AI routes
- local Llama client
- standings routes
- standings service
- insights routes
- insights service
- player stats routes
- player stats service
- metrics
- monitoring config
- Telegram notifier
- Telegram notification routes

Test files:

```text
backend/tests/test_ai_routes.py
backend/tests/test_api_football_provider.py
backend/tests/test_dashboard.py
backend/tests/test_fixture_sync_service.py
backend/tests/test_fixtures.py
backend/tests/test_health.py
backend/tests/test_insights_routes.py
backend/tests/test_insights_service.py
backend/tests/test_local_llama_client.py
backend/tests/test_metrics.py
backend/tests/test_monitoring_config.py
backend/tests/test_notifications.py
backend/tests/test_player_stats_routes.py
backend/tests/test_player_stats_service.py
backend/tests/test_release_workflow.py
backend/tests/test_standings_routes.py
backend/tests/test_standings_service.py
backend/tests/test_telegram_notifier.py
```

---

## CI Architecture

GitHub Actions is used for continuous integration.

Primary workflow:

```text
.github/workflows/ci.yml
```

The CI workflow is expected to validate the project through automated test execution.

---

## Local Development Architecture

The user workflow is:

| Machine | Role |
|---|---|
| MacBook | Main development and control machine |
| VS Code | Main editor |
| Windows laptop | Docker/runtime/demo host |
| SSH | Optional remote control from MacBook into Windows PowerShell |

This means the project should remain:

- easy to edit locally on macOS
- easy to run on Windows Docker Desktop
- clear to verify through Docker Compose
- simple to explain during demos

---

## Security Principles

The project follows these security principles:

1. Do not commit real secrets.
2. Keep `.env.example` safe and generic.
3. Store local secrets in `.env`.
4. Use environment variables for API keys and Telegram credentials.
5. Avoid hardcoded tokens in source code.
6. Treat local Grafana credentials as demo-only.
7. Use safe fallback behavior when optional integrations are unavailable.

---

## Current Limitations

The current v1.7.0 release is portfolio-ready with a stronger provider sync layer and clearer runtime observability, but it is still local-first.

Known limitations:

- It is not a production deployment.
- Grafana credentials are local demo credentials.
- Telegram delivery requires valid user-provided credentials.
- Provider sync requires a valid API-Football key and depends on provider availability.
- Local AI summaries require Ollama to be installed and running.
- Traffic is not protected by HTTPS in the default local Docker Compose setup.
- There is no production authentication layer.
- There is no cloud deployment configuration in the main milestone scope.

---

## Future Architecture Opportunities

Potential future improvements:

### Completed in v1.6.0 — Real Match Data Sync Improvement

- Improved provider sync reliability.
- Added clearer provider error reporting.
- Added real-world provider payload validation and incomplete-row skipping.
- Added status normalization and team-code fallback before database persistence.
- Added route-level provider sync tests for success and failure paths.

### v1.7.0 — AI Insights Upgrade

- Improve summary quality.
- Add standings-aware AI insights.
- Add team and player context to generated summaries.
- Add more structured prompts and fallback behavior.

### v1.8.0 — Portfolio Demo Polish

- Add curated demo seed data.
- Add committed screenshots if desired.
- Add a guided demo script.
- Add optional video/demo evidence references.

---

## Milestone Summary

| Version | Architecture Theme |
|---|---|
| v0.1.0 | Project foundation |
| v0.2.0 | Fixture and API foundation |
| v0.3.0 | Provider integration |
| v0.4.0 | Match completion logic |
| v0.5.0 | Telegram notifications |
| v0.6.0 | Interactive dashboard |
| v0.7.0 | API filters |
| v0.8.0 | Local Llama summaries |
| v1.0.0 | AI quality and dashboard polish |
| v1.1.0 | Standings engine |
| v1.2.0 | Team insights |
| v1.3.0 | Player statistics |
| v1.4.0 | Monitoring foundation |
| v1.4.1 | Grafana polish |
| v1.4.2 | Telegram live hardening |
| v1.4.3 | Documentation and evidence cleanup |
| v1.5.0 | Portfolio release polish |
| v1.6.0 | Real match data sync improvement |
