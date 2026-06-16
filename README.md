# ⚽ World Cup 2026 AI Stats Dashboard

![FastAPI](https://img.shields.io/badge/backend-FastAPI-green)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue)
![Streamlit](https://img.shields.io/badge/dashboard-Streamlit-red)
![Docker](https://img.shields.io/badge/container-Docker-blue)
![Python](https://img.shields.io/badge/python-3.14-yellow)
![Version](https://img.shields.io/badge/version-v0.5.0-purple)

A self-hosted, containerized, AI-assisted World Cup 2026 match tracking platform built with **FastAPI**, **PostgreSQL**, **Streamlit**, **Docker Compose**, and future integrations for **Telegram notifications**, **local Llama/Ollama summaries**, and football analytics.

The project is intentionally being built in public, milestone by milestone, to show backend development, API integration, database design, testing, DevOps fundamentals, and future AI-assisted match analysis.

---

## 📌 Current Version

**v0.5.0 — Telegram Notifications**

The backend now includes Telegram notification support for completed World Cup fixtures.

This milestone builds directly on the `v0.4.0` match completion detector. When fixture sync detects newly completed matches, the backend can prepare Telegram messages and attempt to send them using configured Telegram credentials.

The implementation is safe by default:

* if no newly completed fixtures are detected, notifications are skipped
* if Telegram credentials are missing, sync still succeeds
* missing Telegram credentials return a clear skipped notification result
* test notification endpoint is available for manual testing
* no real Telegram bot token or chat ID is committed

---

## ✅ Current Backend Capabilities

* FastAPI backend service
* PostgreSQL-backed fixture model
* Sample World Cup fixture data
* Manual sample fixture sync endpoint
* Real provider sync endpoint
* API-Football provider client
* Provider abstraction layer
* Fixture sync service with create/update logic
* Newly completed fixture detection
* Telegram message formatter
* Telegram send helper with safe credential checks
* Telegram completed-fixture notification helper
* Safe Telegram test notification endpoint
* Sync responses that expose notification status
* Mocked provider tests
* Service tests for match completion detection
* Telegram notifier tests
* Route tests for fixture sync and notification behavior
* Streamlit dashboard foundation
* Docker Compose local environment
* GitHub Actions CI
* Local pytest test suite

---

## 🧠 Why I Built This

This project is part of my DevOps and Cloud Support learning journey.

The idea is to build something realistic instead of only following tutorials. A football tournament dashboard gives me a way to practice backend and DevOps concerns such as:

* API design
* database modeling
* external provider integration
* idempotent data sync
* change detection during sync
* notification workflows
* safe secret handling
* Docker-based local development
* CI testing
* future AI-assisted summaries

The World Cup is also a good use case because match data changes over time. Fixtures start as scheduled, later become live or completed, and eventually trigger downstream events such as notifications, summaries, and analysis.

---

## 🎯 Project Goal

The goal is to build a self-hosted World Cup 2026 statistics platform that can:

1. Store World Cup fixture data.
2. Sync fixture data from sample data or a real football API provider.
3. Display fixtures in a dashboard.
4. Detect completed matches.
5. Send match notifications.
6. Generate AI-assisted match summaries.
7. Expand into player-level and team-level analytics.
8. Demonstrate practical DevOps, backend, database, notification, and AI integration skills.

---

## 🧱 Current Architecture

```text
User / Browser
    |
    v
Streamlit Dashboard
    |
    v
FastAPI Backend
    |
    +--> /health
    +--> /fixtures
    +--> /fixtures/{fixture_id}
    +--> /fixtures/sync/sample
    +--> /fixtures/sync/provider
    +--> /notifications/telegram/test
    |
    v
Fixture Sync Service
    |
    +--> Create/update fixture records
    +--> Detect newly completed fixtures
    |
    +--> Notification Helper
    |       |
    |       +--> Telegram Message Builder
    |       +--> Telegram Send Function
    |
    +--> Sample Fixtures
    |
    +--> API-Football Provider Client
    |
    v
PostgreSQL Database
```

---

## 🔁 Current Data Flow

### Sample Sync Flow

```text
POST /fixtures/sync/sample
    |
    v
SAMPLE_FIXTURES
    |
    v
sync_fixtures()
    |
    +--> create new fixtures
    +--> update existing fixtures
    +--> detect newly completed fixtures
    |
    v
notify_newly_completed_fixtures()
    |
    +--> if no newly completed fixtures: skip
    +--> if Telegram missing credentials: skip safely
    +--> if Telegram configured: send notifications
    |
    v
API response with sync + notification summary
```

### Provider Sync Flow

```text
POST /fixtures/sync/provider
    |
    v
ApiFootballProvider
    |
    v
API-Football / API-Sports
    |
    v
Normalized fixture dictionaries
    |
    v
sync_fixtures()
    |
    +--> create new fixtures
    +--> update existing fixtures
    +--> detect newly completed fixtures
    |
    v
notify_newly_completed_fixtures()
    |
    v
API response with sync + notification summary
```

The provider sync flow requires a valid local API-Football / API-Sports key to fetch live provider data.

---

## 🔔 Match Completion Detection

The sync service detects newly completed matches.

A fixture is considered newly completed when:

```text
previous status was not completed
AND
new synced status is completed
```

Completed statuses currently supported:

```text
complete
FT
AET
PEN
```

This supports:

* local sample fixture status: `complete`
* common football provider full-time status: `FT`
* extra-time completed status: `AET`
* penalty completed status: `PEN`

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

The test notification endpoint is:

```http
POST /notifications/telegram/test
```

This endpoint builds a sample completed-match message and attempts to send it using local Telegram credentials.

If credentials are missing, the endpoint returns:

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

Example Telegram message format:

```text
🏁 Match Completed

FIFA World Cup 2026
Group Stage

Mexico 2 - 0 South Africa

Venue: Estadio Azteca
```

---

## 📊 Fixture Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "service": "backend",
  "version": "0.5.0"
}
```

---

### List Fixtures

```http
GET /fixtures
```

Returns all stored fixtures ordered by kickoff time.

---

### Get Fixture by ID

```http
GET /fixtures/{fixture_id}
```

Returns one fixture by internal database ID.

---

### Sync Sample Fixtures

```http
POST /fixtures/sync/sample
```

Loads sample World Cup fixture data into the database.

The sync is idempotent. Running it multiple times updates existing records instead of creating duplicates.

Example first sync response with missing Telegram credentials:

```json
{
  "message": "Sample fixtures synced successfully",
  "created": 4,
  "updated": 0,
  "total_sample_fixtures": 4,
  "newly_completed_count": 2,
  "newly_completed": [
    "sample-mex-rsa-2026-06-11",
    "sample-usa-par-2026-06-12"
  ],
  "notifications": {
    "status": "skipped",
    "reason": "TELEGRAM_BOT_TOKEN is not configured.",
    "sent": 0
  }
}
```

Example second sync response:

```json
{
  "message": "Sample fixtures synced successfully",
  "created": 0,
  "updated": 4,
  "total_sample_fixtures": 4,
  "newly_completed_count": 0,
  "newly_completed": [],
  "notifications": {
    "status": "skipped",
    "reason": "No newly completed fixtures",
    "sent": 0
  }
}
```

---

### Sync Provider Fixtures

```http
POST /fixtures/sync/provider
```

Fetches World Cup fixtures from the configured provider and saves them into the database.

Current provider:

```text
api_football
```

This endpoint requires a valid API key in `.env`:

```env
API_FOOTBALL_KEY=your_real_api_key_here
```

If the key is missing or still set to `replace_me`, the endpoint returns:

```json
{
  "detail": "API_FOOTBALL_KEY is not configured."
}
```

Expected successful response when a valid provider key is configured:

```json
{
  "message": "Provider fixtures synced successfully",
  "provider": "api_football",
  "created": 72,
  "updated": 0,
  "total_provider_fixtures": 72,
  "newly_completed_count": 0,
  "newly_completed": [],
  "notifications": {
    "status": "skipped",
    "reason": "No newly completed fixtures",
    "sent": 0
  }
}
```

The exact fixture count depends on the provider response.

---

## 🛠️ Tech Stack

| Area | Technology |
|---|---|
| Backend API | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Dashboard | Streamlit |
| Containerization | Docker Compose |
| Testing | pytest |
| HTTP Client | httpx |
| Settings | pydantic-settings |
| CI | GitHub Actions |
| Notifications | Telegram Bot API |
| Future Local AI | Ollama / Llama |
| Future Monitoring | Prometheus / Grafana |

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
│   │   │   └── fixture.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── api_football.py
│   │   │   └── base.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── fixtures.py
│   │   │   └── notifications.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── fixture_sync_service.py
│   │   │   ├── sample_data.py
│   │   │   └── telegram_notifier.py
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_api_football_provider.py
│   │   ├── test_fixture_sync_service.py
│   │   ├── test_fixtures.py
│   │   ├── test_health.py
│   │   ├── test_notifications.py
│   │   └── test_telegram_notifier.py
│   ├── pytest.ini
│   └── requirements.txt
├── dashboard/
│   └── app.py
├── docs/
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

* Git
* Docker Desktop
* Python 3.14 or compatible Python 3 version
* VS Code or another code editor

Optional:

* API-Football / API-Sports account for real provider syncing
* Telegram bot token and chat ID for real Telegram notification testing
* Postman or curl for endpoint testing

---

## 📦 Clone the Repository

```bash
git clone https://github.com/AnarkeyV/worldcup-2026-ai-stats.git
cd worldcup-2026-ai-stats
```

---

## 🔐 Environment Setup

Create your local `.env` file from the example file:

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
APP_VERSION=0.5.0

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

# LLM
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2:1b

# Public URL
PUBLIC_DASHBOARD_URL=http://localhost:8501
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

Use `docker compose down -v` carefully because it removes the database volume.

---

## 🌐 Access the Services

| Service | URL |
|---|---|
| Backend API | http://localhost:8000 |
| Backend Health Check | http://localhost:8000/health |
| API Docs | http://localhost:8000/docs |
| Dashboard | http://localhost:8501 |

---

## 🧪 Run Tests Locally

From the project root:

```bash
cd backend
pytest -v
```

Current expected result:

```text
18 passed
```

Warnings may appear depending on the local Python and package versions. Current warnings are not blocking the test suite.

---

## 🧪 Test Coverage Areas

Current tests cover:

* backend health check
* empty fixture list before sync
* sample fixture sync
* fixture list after sync
* single fixture retrieval
* missing fixture 404 response
* idempotent sample fixture sync behavior
* API-Football provider normalization using a mocked response
* fixture sync service create behavior
* fixture sync service update behavior
* newly completed existing fixture detection
* already completed fixture non-duplication
* sample sync response completion fields
* provider sync endpoint behavior when API key is missing
* Telegram message formatting
* Telegram missing credential handling
* completed fixture notification helper
* safe Telegram test notification endpoint

---

## ⚙️ GitHub Actions CI

The project includes GitHub Actions CI for backend tests.

Typical CI behavior:

```text
push / pull request
    |
    v
install dependencies
    |
    v
run pytest
```

The CI pipeline is intended to catch backend regressions before merging changes into `main`.

---

## 🔒 Security Notes

* `.env` is ignored by Git.
* `.env.example` contains placeholders only.
* API keys and Telegram secrets must be stored locally or in secure deployment secrets.
* Never commit real provider keys.
* Never commit real Telegram bot tokens or chat IDs.
* Never paste real secrets into screenshots, README files, commits, or public issues.
* The provider sync endpoint handles missing API keys with a clear error response.
* Telegram notification sending handles missing credentials safely.
* Future deployment should use platform secrets instead of plain `.env` files.

---

## 🧭 Roadmap

### v0.1.0 — Project Foundation

Completed:

* FastAPI backend
* Streamlit dashboard folder
* Docker Compose foundation
* PostgreSQL service
* GitHub Actions CI
* Basic documentation

---

### v0.1.1 — README and Documentation Polish

Completed:

* Improved README structure
* Added project purpose
* Added roadmap
* Added setup notes
* Added documentation index

---

### v0.2.0 — Football API Integration Foundation

Completed:

* PostgreSQL-backed fixture model
* Sample World Cup fixture data
* Manual sample fixture sync endpoint
* Fixture list endpoint
* Single fixture retrieval endpoint
* Streamlit fixture table
* Endpoint tests

---

### v0.3.0 — Real Football API Provider Integration

Completed:

* Provider abstraction layer
* API-Football provider client
* Football API environment configuration
* Safe `.env.example` provider documentation
* Provider response normalization
* Fixture sync service
* Idempotent create/update fixture logic
* Sample sync refactored to use sync service
* Provider sync endpoint
* Mocked provider unit test
* Provider endpoint no-key test
* Full backend test suite passing

---

### v0.4.0 — Match Completion Detector

Completed:

* Detect newly completed fixtures during sync
* Support completed statuses: `complete`, `FT`, `AET`, `PEN`
* Avoid duplicate newly completed detection for already completed fixtures
* Expose newly completed fixture IDs in sample sync response
* Expose newly completed fixture IDs in provider sync response
* Service-level tests for completion detection
* Route-level tests for sync response fields
* Full backend test suite passing

---

### v0.5.0 — Telegram Notifications

Current status: backend implementation in progress.

Completed:

* Telegram settings added
* Telegram notifier service
* Completed fixture Telegram message formatter
* Safe Telegram send function
* Completed fixture notification helper
* Safe Telegram test endpoint
* Telegram notification wiring into fixture sync responses
* Notification skip behavior when no newly completed fixtures exist
* Notification skip behavior when Telegram credentials are missing
* Service-level Telegram tests
* Route-level notification tests
* Full backend test suite passing

Still pending:

* Update app version from `0.4.0` to `0.5.0`
* Update `VERSION`
* Update `.env.example`
* Confirm `/health` returns `0.5.0`
* Merge v0.5.0 into `main`

---

### v0.6.0 — Interactive Dashboard

Planned:

* Fixture filtering
* Group filtering
* Status filtering
* Match detail view
* Provider/source status display
* Notification status display

---

### v0.7.0 — Local Llama Summary Agent

Planned:

* Ollama integration
* Generate short match summaries
* Generate daily World Cup summaries
* Use completed match trigger as summary input
* Keep local-first AI processing option

---

### v0.8.0 — Player-Level Statistics

Planned:

* Player statistics model
* Goals, assists, cards, minutes
* Team/player views
* Provider mapping for player data

---

### v0.9.0 — Monitoring and Observability

Planned:

* Prometheus metrics
* Grafana dashboard
* API health metrics
* Provider sync success/failure metrics
* Telegram notification success/failure metrics
* Basic alerting

---

### v1.0.0 — Portfolio Release

Planned:

* Stable local deployment
* Complete README
* Screenshots
* Demo video
* Architecture diagram
* Portfolio-ready release tag

---

## 📊 Version History

| Version | Description | Status |
|---|---|---|
| v0.1.0 | Project foundation with Docker, FastAPI, Streamlit, PostgreSQL, pytest, and CI | Completed |
| v0.1.1 | README and documentation polish | Completed |
| v0.2.0 | Football API integration foundation with fixture database, sample sync, dashboard table, and endpoint tests | Completed |
| v0.3.0 | Real football API provider layer, provider client, fixture sync service, provider sync endpoint, and mocked tests | Completed |
| v0.4.0 | Match completion detection during fixture sync with response fields and tests | Completed |
| v0.5.0 | Telegram notification service, test endpoint, completed fixture notification helper, and sync wiring | In Progress |
| v0.6.0 | Interactive dashboard improvements | Planned |
| v0.7.0 | Local Llama summary agent | Planned |
| v0.8.0 | Player-level statistics | Planned |
| v0.9.0 | Monitoring and observability | Planned |
| v1.0.0 | Portfolio-ready release | Planned |

---

## 🧪 Manual API Testing

After starting Docker Compose, try:

### Health Check

```bash
curl http://localhost:8000/health
```

### List Fixtures

```bash
curl http://localhost:8000/fixtures
```

### Sync Sample Fixtures

```bash
curl -X POST http://localhost:8000/fixtures/sync/sample
```

### Test Telegram Notification

```bash
curl -X POST http://localhost:8000/notifications/telegram/test
```

Without Telegram credentials, this should return:

```json
{
  "detail": "TELEGRAM_BOT_TOKEN is not configured."
}
```

### Sync Provider Fixtures

```bash
curl -X POST http://localhost:8000/fixtures/sync/provider
```

Without a valid provider API key, this should return:

```json
{
  "detail": "API_FOOTBALL_KEY is not configured."
}
```

---

## 🖥️ Development Setup Notes

For backend-only local testing:

### macOS / Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

### Windows PowerShell

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

---

## 📸 Screenshots

Screenshots can be added later for:

* backend health check
* API docs
* sample fixture sync
* fixture list endpoint
* Streamlit dashboard
* provider sync response
* newly completed sync response
* Telegram test endpoint response
* GitHub Actions passing run

Suggested folder:

```text
docs/images/
```

---

## 🧠 AI Usage Plan

This project is designed to eventually use AI in a controlled and explainable way.

Planned AI usage:

* summarize completed matches
* create daily World Cup recap messages
* explain key match events
* generate short dashboard insights
* help format Telegram alerts

The AI layer should not replace source football data.

The intended design is:

```text
Structured provider data
    |
    v
Backend validation and storage
    |
    v
Completion detector
    |
    v
Telegram notification trigger
    |
    v
Controlled prompt/template
    |
    v
Local or external LLM summary
    |
    v
Dashboard or notification output
```

---

## 🚫 What This Project Is Not

This project is not:

* a betting prediction system
* a gambling tool
* a replacement for official FIFA data
* a commercial sports data platform
* a real-time production-grade live-score service yet

The system is designed to use structured football data from a proper API provider and process it through controlled, auditable workflows.

---

## 📚 Documentation

Planned documentation:

* architecture notes
* API design notes
* provider integration notes
* match completion detector notes
* Telegram notification notes
* environment setup guide
* dashboard usage guide
* future AI summary design

---

## 🧹 Stop the Project

Stop containers:

```bash
docker compose down
```

Stop and remove volumes:

```bash
docker compose down -v
```

Remove unused Docker resources if needed:

```bash
docker system prune
```

Use prune commands carefully.

---

## 👤 Author

**Khairul Rizal**

GitHub:

```text
https://github.com/AnarkeyV
```

---

## 📌 Project Status

Current status:

```text
v0.5.0 — Telegram Notifications
```

The backend now supports safe Telegram notification behavior for newly completed fixtures.

Sample fixtures remain available as a safe fallback for local development, public GitHub users, and testing without provider or Telegram credentials.

Next recommended step:

```text
Update project version values to 0.5.0 and confirm the health check/test suite.
```
