# ⚽ World Cup 2026 AI Stats Dashboard

![Version](https://img.shields.io/badge/version-v1.6.0-purple)
![Tests](https://img.shields.io/badge/tests-123%20passed-brightgreen)
![Backend](https://img.shields.io/badge/backend-FastAPI-blue)
![Dashboard](https://img.shields.io/badge/dashboard-Streamlit%20%2B%20Static%20UI-orange)
![Database](https://img.shields.io/badge/database-PostgreSQL-blue)
![Monitoring](https://img.shields.io/badge/monitoring-Prometheus%20%2B%20Grafana-red)
![AI](https://img.shields.io/badge/AI-Local%20Llama%20%2F%20Ollama-green)
![Notifications](https://img.shields.io/badge/notifications-Telegram-lightblue)

## 📌 Current Version

**v1.6.0 — Real Match Data Sync Improvement**

World Cup 2026 AI Stats Dashboard is a portfolio-grade football analytics platform built around the FIFA World Cup 2026 use case.

The project combines:

- FastAPI backend services
- PostgreSQL persistence
- fixture synchronization
- standings calculation
- team and group insights
- player statistics
- local AI summaries through Ollama / Llama
- Telegram notification workflows
- Prometheus metrics
- Grafana dashboards
- Docker Compose runtime orchestration
- automated pytest coverage

The current release improves real provider fixture synchronization so API-Football data is normalized, safer to ingest, and easier to explain during portfolio and technical reviews.

---

## 🎯 Project Purpose

This project was created as a practical DevOps and backend engineering portfolio project.

Instead of only showing a basic API, the project demonstrates how a real application can grow milestone by milestone from a small backend into a monitored, containerized, documented, and demo-ready system.

The theme is the **FIFA World Cup 2026**, but the engineering ideas are broader:

- API design
- database-backed services
- provider integration
- test-driven milestone delivery
- local development workflow
- Docker runtime workflow
- monitoring and observability
- notification integration
- AI-assisted summaries
- release documentation
- portfolio storytelling

---

## 🧭 Project Goals

The project is designed to show that I can:

1. Build and structure a backend application using FastAPI.
2. Model football fixtures, standings, insights, and player statistics.
3. Use PostgreSQL as a persistent runtime database.
4. Containerize services using Docker and Docker Compose.
5. Integrate provider-based football data sync logic.
6. Add AI-generated summaries using a local LLM workflow.
7. Send Telegram notifications safely using configurable credentials.
8. Expose Prometheus metrics for runtime monitoring.
9. Provision Grafana dashboards through Docker-mounted configuration.
10. Maintain release quality through automated tests and documentation.
11. Explain the system clearly to non-technical and technical reviewers.

---

## 🧱 Architecture Overview

At a high level, the system runs as a multi-service Docker Compose application.

```text
+--------------------+
| User / Reviewer    |
+---------+----------+
          |
          v
+--------------------+          +--------------------+
| Streamlit Dashboard|          | Static Dashboard   |
| localhost:18501    |          | /dashboard         |
+---------+----------+          +---------+----------+
          |                               |
          +---------------+---------------+
                          |
                          v
+---------------------------------------------------+
| FastAPI Backend                                  |
| localhost:8000                                  |
|                                                   |
| Routes:                                           |
| /fixtures, /standings, /insights/groups           |
| /players/stats, /ai/*, /notifications/*           |
| /metrics, /health, /dashboard                     |
+----------------------+----------------------------+
                       |
          +------------+-------------+
          |                          |
          v                          v
+--------------------+     +-------------------------+
| PostgreSQL         |     | Local Llama / Ollama    |
| localhost:5432     |     | localhost:11434         |
+--------------------+     +-------------------------+
          |
          v
+--------------------+     +-------------------------+
| Prometheus         | --> | Grafana                 |
| localhost:9090     |     | localhost:3000          |
+--------------------+     +-------------------------+

Telegram Bot API is used for optional notification delivery.
External football API provider configuration is supported through environment variables.
```

---

## 🔄 Data and Notification Flow

### Sample Fixture Sync Flow

```text
User / Dashboard
      |
      v
POST /fixtures/sync/sample
      |
      v
Sample data service
      |
      v
PostgreSQL fixtures table
      |
      v
Fixtures, standings, insights, dashboard, metrics
```

### Provider Fixture Sync Flow

```text
User / Dashboard
      |
      v
POST /fixtures/sync/provider
      |
      v
API-Football provider adapter
      |
      v
External provider response
      |
      v
Normalized fixture records
      |
      v
Status cleanup, team-code fallback, and invalid-row skipping
      |
      v
PostgreSQL
```

### Telegram Notification Flow

```text
Match / test notification event
      |
      v
Notification route or service
      |
      v
Telegram notifier
      |
      v
Telegram Bot API
      |
      v
Configured chat
```

### Observability Flow

```text
FastAPI backend
      |
      v
/metrics endpoint
      |
      v
Prometheus scrape
      |
      v
Grafana provisioned dashboard
```

---

## 🧩 Main Features

### Fixtures

The fixtures module supports:

- listing fixtures
- filtering by group
- filtering by match status
- searching by team
- fetching a fixture by ID
- syncing sample fixture data
- syncing provider-backed fixture data

Key endpoints:

```text
GET  /fixtures
GET  /fixtures/{fixture_id}
POST /fixtures/sync/sample
POST /fixtures/sync/provider
```

---

### Standings

The standings module calculates group table information from fixture results.

It supports:

- group ranking
- points calculation
- goals for and against
- goal difference
- wins, draws, and losses

Key endpoint:

```text
GET /standings
```

---

### Group Insights

The insights module provides analytics-style summaries for World Cup groups.

It supports:

- group-level summaries
- completed fixture counts
- standings-linked insight data
- dashboard-ready analytics output

Key endpoint:

```text
GET /insights/groups
```

---

### Player Statistics

The player statistics module adds player-level data to the project.

It supports:

- syncing sample player statistics
- listing player stats
- filtering by team
- sorting by goals and other stats

Key endpoints:

```text
POST /players/stats/sync/sample
GET  /players/stats
```

---

### AI Summary Layer

The AI layer uses a local Llama/Ollama workflow for summary generation.

It supports:

- AI health checks
- fixture summary generation
- fixture-specific summary generation
- safer fallback behavior when the local model is unavailable

Key endpoints:

```text
GET /ai/health
GET /ai/fixtures/summary
GET /ai/fixtures/{fixture_id}/summary
```

---

### Telegram Notifications

The Telegram layer supports live notification readiness and test delivery.

It supports:

- checking whether Telegram credentials are configured
- sending a test Telegram notification
- safe configuration through environment variables
- no hardcoded secrets

Key endpoints:

```text
GET  /notifications/telegram/status
POST /notifications/telegram/test
```

---

### Monitoring and Observability

The monitoring layer includes:

- FastAPI `/metrics` endpoint
- Prometheus scrape configuration
- Grafana datasource provisioning
- Grafana dashboard provisioning
- application info metric with version and environment labels

Key endpoint:

```text
GET /metrics
```

Monitoring files:

```text
monitoring/prometheus.yml
monitoring/grafana/dashboards/worldcup-overview.json
monitoring/grafana/provisioning/dashboards/dashboards.yml
monitoring/grafana/provisioning/datasources/prometheus.yml
```

---

## 🛠️ Tech Stack

| Area | Technology |
|---|---|
| Backend API | FastAPI |
| Backend Server | Uvicorn |
| Database | PostgreSQL |
| Database Driver | psycopg |
| Dashboard | Streamlit and static HTML/CSS/JS |
| AI Layer | Local Llama through Ollama |
| Notifications | Telegram Bot API |
| Metrics | Prometheus client |
| Monitoring | Prometheus |
| Visualization | Grafana |
| Runtime | Docker Compose |
| Testing | pytest |
| CI | GitHub Actions |
| Language | Python |

---

## 📁 Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── providers/
│   │   ├── routes/
│   │   │   ├── ai.py
│   │   │   ├── dashboard.py
│   │   │   ├── fixtures.py
│   │   │   ├── insights.py
│   │   │   ├── metrics.py
│   │   │   ├── notifications.py
│   │   │   ├── players.py
│   │   │   └── standings.py
│   │   ├── services/
│   │   │   ├── fixture_sync_service.py
│   │   │   ├── insights_service.py
│   │   │   ├── local_llama_client.py
│   │   │   ├── metrics_service.py
│   │   │   ├── player_stats_service.py
│   │   │   ├── sample_data.py
│   │   │   ├── standings_service.py
│   │   │   └── telegram_notifier.py
│   │   └── static/
│   │       ├── dashboard.css
│   │       ├── dashboard.html
│   │       └── dashboard.js
│   ├── tests/
│   ├── Dockerfile
│   ├── pytest.ini
│   └── requirements.txt
├── dashboard/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── docs/
│   ├── architecture.md
│   ├── changelog.md
│   ├── demo-walkthrough.md
│   ├── portfolio-release.md
│   └── roadmap.md
├── infra/
│   └── docker-compose.yml
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
│       ├── dashboards/
│       │   └── worldcup-overview.json
│       └── provisioning/
├── docker-compose.yml
├── README.md
└── VERSION
```

---

## 🚀 Getting Started

### Prerequisites

Install these tools before running the project:

- Git
- Python 3.14 or a compatible Python 3 version
- Docker Desktop
- Docker Compose
- VS Code
- Optional: Ollama for local AI summaries
- Optional: Telegram bot token and chat ID for live notifications

---

## 📦 Clone the Repository

```bash
git clone <your-repository-url>
cd worldcup-2026-ai-stats
```

---

## 🔐 Environment Setup

Create your local `.env` file from the example:

### macOS / Linux

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

Then edit `.env` as needed.

---

## 🧾 Environment Variables

```env
# App
APP_NAME=World Cup 2026 AI Stats
APP_ENV=development
APP_VERSION=1.6.0

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

Never commit real API keys, Telegram bot tokens, chat IDs, or production secrets.

---

## 🐳 Run with Docker Compose

Build and start the full local stack:

```bash
docker compose up -d --build
```

Check containers:

```bash
docker compose ps
```

View backend logs:

```bash
docker compose logs -f backend
```

Stop the stack:

```bash
docker compose down
```

Stop the stack and remove volumes:

```bash
docker compose down -v
```

---

## 🌐 Access the Services

| Service | URL |
|---|---|
| FastAPI backend | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Backend static dashboard | http://localhost:8000/dashboard |
| Streamlit dashboard | http://localhost:18501 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

Grafana local credentials:

```text
Username: admin
Password: admin
```

The Docker Compose file maps the Streamlit dashboard from container port `8501` to host port `18501` to avoid common local port conflicts.

---

## 🖥️ MacBook + Windows Laptop Workflow

This project is developed using a two-machine workflow:

| Machine | Role |
|---|---|
| MacBook | Main development and control machine |
| VS Code on MacBook | Main editor |
| Windows laptop | Docker/runtime/demo host |
| SSH from MacBook to Windows PowerShell | Optional Docker Compose checks |

Typical workflow:

1. Edit project files on the MacBook using VS Code.
2. Commit changes through Git.
3. Run local tests on the MacBook.
4. SSH into the Windows laptop if Docker runtime verification is needed.
5. Run Docker Compose on the Windows laptop for demo checks.
6. Use browser access to verify backend, dashboard, Prometheus, and Grafana.

Example SSH-style flow:

```bash
ssh <windows-user>@<windows-host>
```

Then inside Windows PowerShell:

```powershell
cd path\to\worldcup-2026-ai-stats
docker compose up -d --build
docker compose ps
```

---

## 🧪 Run Tests Locally

Run the full test suite from the project root:

```bash
python -m pytest
```

Current release baseline:

```text
114 passed
```

The test suite covers:

- health route
- release workflow/version consistency
- fixture routes
- fixture sync service
- API football provider adapter
- dashboard routes
- AI routes
- local Llama client
- standings routes and service
- insights routes and service
- player stats routes and service
- metrics
- monitoring configuration
- Telegram notifier
- Telegram notification routes

---

## 🏥 Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "backend",
  "version": "1.6.0"
}
```

---

## 📡 Registered API Routes

```text
GET  /
GET  /health

GET  /dashboard
GET  /metrics

GET  /fixtures
GET  /fixtures/{fixture_id}
POST /fixtures/sync/sample
POST /fixtures/sync/provider

GET  /standings

GET  /insights/groups

GET  /players/stats
POST /players/stats/sync/sample

GET  /ai/health
GET  /ai/fixtures/summary
GET  /ai/fixtures/{fixture_id}/summary

GET  /notifications/telegram/status
POST /notifications/telegram/test
```

Interactive API docs are available at:

```text
http://localhost:8000/docs
```

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
curl "http://localhost:8000/fixtures?status=completed"
```

### Search by Team

```bash
curl "http://localhost:8000/fixtures?team=Mexico"
```

### Sync Sample Fixtures

```bash
curl -X POST http://localhost:8000/fixtures/sync/sample
```

### Sync Provider Fixtures

```bash
curl -X POST http://localhost:8000/fixtures/sync/provider
```

Provider sync requires a valid provider configuration and API key. In v1.6.0, provider payloads are normalized before database sync, including status cleanup, team-code fallback, incomplete fixture skipping, and clearer provider failure responses.

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
curl "http://localhost:8000/players/stats?team=Argentina"
```

### Sort by Goals

```bash
curl "http://localhost:8000/players/stats?sort_by=goals"
```

---

## 📣 Telegram Notifications

Telegram notification support is optional and controlled through environment variables.

Check notification readiness:

```bash
curl http://localhost:8000/notifications/telegram/status
```

Send a test notification:

```bash
curl -X POST http://localhost:8000/notifications/telegram/test
```

Environment variables:

```env
TELEGRAM_BOT_TOKEN=replace_me
TELEGRAM_CHAT_ID=replace_me
PUBLIC_DASHBOARD_URL=http://localhost:8000/dashboard
```

Security notes:

- Do not commit real Telegram credentials.
- Use `.env` for local secrets.
- Keep `.env.example` safe and generic.
- Rotate tokens if they are accidentally exposed.

---

## 🤖 AI Summary Layer

The AI summary layer is built for local-first experimentation.

It uses:

```env
LLAMA_BASE_URL=http://127.0.0.1:11434
LLAMA_MODEL=llama3.2:1b
LLAMA_TIMEOUT_SECONDS=60
```

Check AI readiness:

```bash
curl http://localhost:8000/ai/health
```

Generate fixture summary:

```bash
curl http://localhost:8000/ai/fixtures/summary
```

Generate summary for a specific fixture:

```bash
curl http://localhost:8000/ai/fixtures/1/summary
```

If Ollama is not running, the backend should fail safely instead of breaking the full application.

---

## 📈 Prometheus Metrics

The backend exposes Prometheus metrics at:

```text
http://localhost:8000/metrics
```

Prometheus runs at:

```text
http://localhost:9090
```

The Prometheus configuration is stored at:

```text
monitoring/prometheus.yml
```

The monitoring layer is useful for demonstrating:

- backend uptime
- request volume
- request latency
- HTTP status patterns
- application version labels
- runtime observability readiness

---

## 📊 Grafana Dashboard

Grafana runs at:

```text
http://localhost:3000
```

Grafana is provisioned through files under:

```text
monitoring/grafana/provisioning/datasources/prometheus.yml
monitoring/grafana/provisioning/dashboards/dashboards.yml
monitoring/grafana/dashboards/worldcup-overview.json
```

The dashboard is configured through Docker Compose with:

```text
GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/var/lib/grafana/dashboards/worldcup-overview.json
```

This makes the local monitoring demo easier to open and explain.

---

## 🔐 Security Notes

This project is intended as a local portfolio/demo system.

Important security practices:

- Real secrets should only live in `.env`.
- `.env.example` should contain placeholders only.
- Telegram credentials must not be committed.
- API provider keys must not be committed.
- Local Grafana credentials are demo credentials only.
- Production deployment would require stronger secrets management, HTTPS, authentication, and network restrictions.

---

## 🧯 Troubleshooting Notes

### Docker container name conflict

If a container already exists:

```bash
docker compose down
docker rm -f worldcup-backend worldcup-dashboard worldcup-postgres worldcup-prometheus worldcup-grafana
docker compose up -d --build
```

### Windows port bind issue

If port `8501` is blocked or reserved on Windows, this project uses host port `18501` for the Streamlit dashboard:

```text
localhost:18501 -> container:8501
```

### Docker credential issue on Windows

If Docker has credential helper issues on Windows, restart Docker Desktop and confirm that Docker commands work from PowerShell:

```powershell
docker version
docker compose version
docker compose ps
```

### Backend cannot connect to database

Check container status:

```bash
docker compose ps
docker compose logs postgres
docker compose logs backend
```

Confirm the `DATABASE_URL` points to the Docker service name:

```env
DATABASE_URL=postgresql+psycopg://worldcup:worldcup@postgres:5432/worldcup
```

### Grafana dashboard does not appear

Restart Grafana:

```bash
docker compose restart grafana
```

Check logs:

```bash
docker compose logs grafana
```

Confirm provisioning files exist:

```bash
find monitoring/grafana -type f | sort
```

---

## 📸 Demo Evidence

No screenshot images are currently committed in the repository.

For portfolio and presentation evidence, screenshots can be stored locally using folders such as:

```text
~/documents/world-cup-ai-stats-screenshots/v1.4.1-demo
~/documents/world-cup-ai-stats-screenshots/v1.4.2-demo
~/documents/world-cup-ai-stats-screenshots/v1.6.0-real-match-data-sync
```

Recommended screenshots for v1.6.0:

- GitHub README top section
- FastAPI `/docs`
- backend `/health`
- backend `/dashboard`
- Streamlit dashboard
- Prometheus targets
- Grafana dashboard
- Telegram readiness endpoint
- pytest `123 passed`

Avoid adding broken image references to the README unless screenshots are committed into the repo.

---

## 📚 Documentation

| Document | Purpose |
|---|---|
| `README.md` | Main portfolio landing page |
| `docs/architecture.md` | Current v1.6.0 architecture |
| `docs/changelog.md` | Release history |
| `docs/roadmap.md` | Completed and planned milestones |
| `docs/portfolio-release.md` | Portfolio-facing release summary |
| `docs/demo-walkthrough.md` | Interview/demo walkthrough |

---

## 🧾 Release History

### v1.6.0 — Real Match Data Sync Improvement

- Improved API-Football provider normalization for real fixture payloads.
- Added provider status cleanup, including scheduled, live, complete, postponed, cancelled, and abandoned states.
- Added team-code fallback logic so provider records remain compatible with the fixture database model.
- Added incomplete provider fixture skipping to avoid unsafe `external_id` and required-field issues.
- Added provider error handling for request failures, invalid JSON, and invalid provider payloads.
- Hardened fixture sync completion detection with case-insensitive status handling.
- Added route-level provider sync tests for mocked provider success and provider failure behavior.
- Bumped release metadata to `1.6.0`.
- Expanded full test baseline: `123 passed`.

### v1.5.0 — Portfolio Release Polish

- Refreshed README as the main GitHub and portfolio landing page.
- Updated architecture documentation to reflect the current backend, dashboard, AI, Telegram, metrics, Prometheus, and Grafana stack.
- Added a portfolio release summary.
- Added a demo walkthrough for interviews and recruiter review.
- Updated roadmap and changelog for release readiness.
- Bumped release metadata to `1.5.0`.
- Preserved full test baseline: `114 passed`.

### v1.4.3 — Documentation and Demo Evidence Cleanup

- Updated README version references and milestone status.
- Cleaned documentation around demo evidence, ports, and screenshots.
- Updated changelog and roadmap.
- Bumped release metadata to `1.4.3`.

### v1.4.2 — Telegram API Live Integration Hardening

- Added Telegram readiness/status checks.
- Hardened Telegram live delivery behavior.
- Improved notification safety and test coverage.
- Bumped release metadata to `1.4.2`.

### v1.4.1 — Grafana Dashboard Polish

- Improved Grafana dashboard provisioning.
- Added Prometheus datasource provisioning.
- Polished local monitoring demo workflow.
- Captured monitoring demo evidence.

### v1.4.0 — Monitoring and Observability Foundation

- Added Prometheus metrics endpoint.
- Added Prometheus service.
- Added Grafana service.
- Added monitoring configuration tests.

### Earlier milestones

The project also includes earlier milestones for:

- project foundation
- fixture API
- provider integration
- match completion detection
- Telegram notifications
- interactive dashboard
- API filters
- local Llama summaries
- standings engine
- team insights
- player statistics

See `docs/changelog.md` and `docs/roadmap.md` for the full milestone history.

---

## 📊 Version History

| Version | Summary | Status |
|---|---|---|
| v0.1.0 | Project foundation | Completed |
| v0.1.1 | README and documentation polish | Completed |
| v0.2.0 | Football API integration foundation | Completed |
| v0.3.0 | Real football API provider layer | Completed |
| v0.4.0 | Match completion detection | Completed |
| v0.5.0 | Telegram notifications | Completed |
| v0.6.0 | Interactive dashboard | Completed |
| v0.7.0 | API-level fixture filters | Completed |
| v0.8.0 | Local Llama summary agent | Completed |
| v1.0.0 | AI summary quality and dashboard polish | Completed |
| v1.1.0 | Group standings engine | Completed |
| v1.1.1 | README and documentation refresh | Completed |
| v1.1.2 | Version and container workflow cleanup | Completed |
| v1.2.0 | Team insights and group analytics | Completed |
| v1.3.0 | Player-level statistics foundation | Completed |
| v1.4.0 | Monitoring and observability foundation | Completed |
| v1.4.1 | Grafana dashboard polish | Completed |
| v1.4.2 | Telegram API live integration hardening | Completed |
| v1.4.3 | Documentation and demo evidence cleanup | Completed |
| v1.5.0 | Portfolio release polish | Completed |
| v1.6.0 | Real match data sync improvement | Completed |

---

## 🧭 Roadmap Summary

Recommended future milestones:

| Version | Theme |
|---|---|
| v1.7.0 | AI insights upgrade |
| v1.8.0 | Portfolio demo polish |

The next major technical step is likely richer AI insight generation that can use standings, team context, player statistics, and completed fixture data more intelligently.

---

## 📌 Project Status

```text
Current version: v1.6.0 — Real Match Data Sync Improvement
Current test baseline: 123 passed
Runtime: Docker Compose local stack
Main demo services: FastAPI, dashboard, PostgreSQL, Prometheus, Grafana
Optional integrations: API-Football, Telegram, Ollama / Local Llama
```

This project is now positioned as a portfolio-ready DevOps/backend/observability showcase with a stronger real provider data-sync layer.
