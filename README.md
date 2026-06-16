# ⚽ World Cup 2026 AI Stats Dashboard

![FastAPI](https://img.shields.io/badge/backend-FastAPI-green)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue)
![Streamlit](https://img.shields.io/badge/dashboard-Streamlit-red)
![Docker](https://img.shields.io/badge/container-Docker-blue)
![Python](https://img.shields.io/badge/python-3.14-yellow)
![Version](https://img.shields.io/badge/version-v0.3.0-purple)

A self-hosted, containerized, AI-assisted World Cup 2026 match tracking platform built with **FastAPI**, **PostgreSQL**, **Streamlit**, **Docker Compose**, and future integrations for **Telegram notifications**, **local Llama/Ollama summaries**, and football analytics.

The project is intentionally being built in public, milestone by milestone, to show backend development, API integration, database design, testing, DevOps fundamentals, and future AI-assisted match analysis.

---

## 📌 Current Version

**v0.3.0 — Real Football API Provider Integration**

The backend now includes a real football data provider layer using an API-Football provider client, while still keeping sample fixture sync available for local development and testing.

### Current Backend Capabilities

* FastAPI backend service
* PostgreSQL-backed fixture model
* Sample World Cup fixture data
* Manual sample fixture sync endpoint
* Real provider sync endpoint
* API-Football provider client
* Provider abstraction layer
* Fixture sync service with create/update logic
* Mocked provider tests
* Route tests for fixture sync behavior
* Streamlit dashboard foundation
* Docker Compose local environment
* GitHub Actions CI
* Local pytest test suite

### Current Integration Status

The application can now support both:

* sample fixture data for development and demo use
* real provider fixture data through the provider sync endpoint

Live real-data syncing requires a valid API-Football / API-Sports key to be added locally in `.env`.

No API key is committed to Git.

---

## 🧠 Why I Built This

This project is part of my DevOps and Cloud Support learning journey.

The idea is to build something that feels realistic instead of only following tutorials. A football tournament dashboard gives me a way to practice real backend concerns such as:

* API design
* database modeling
* external provider integration
* idempotent data sync
* Docker-based local development
* CI testing
* environment variable handling
* secure API key management
* future notifications and automation
* future AI-assisted summaries

The World Cup is also a good use case because match data changes over time. Fixtures start as scheduled, later become live or completed, and eventually trigger downstream events such as standings updates, alerts, summaries, and analysis.

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
8. Demonstrate practical DevOps, backend, database, and AI integration skills.

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
    |
    v
Fixture Sync Service
    |
    +--> Sample Fixtures
    |
    +--> API-Football Provider Client
    |
    v
PostgreSQL Database
```

### Current Data Flow

```text
Sample Sync Flow
----------------
POST /fixtures/sync/sample
    |
    v
SAMPLE_FIXTURES
    |
    v
sync_fixtures()
    |
    v
PostgreSQL fixtures table


Provider Sync Flow
------------------
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
    v
PostgreSQL fixtures table
```

The provider sync flow is ready in code, but requires a valid local API key to fetch live provider data.

---

## 🔮 Planned Future Architecture

```text
Football Data API
    |
    v
Provider Client Layer
    |
    v
FastAPI Backend
    |
    +--> Fixture Sync Service
    +--> Match Completion Detector
    +--> Notification Service
    +--> AI Summary Service
    |
    v
PostgreSQL Database
    |
    v
Streamlit Dashboard
    |
    v
User
```

Future services may include:

* match completion detector
* Telegram notification service
* Ollama / local Llama summary generation
* player-level statistics ingestion
* standings calculation
* provider health/status reporting
* monitoring and observability

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
| Future Notifications | Telegram Bot API |
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
│   │   │   └── fixtures.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── fixture_sync_service.py
│   │   │   └── sample_data.py
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
│   │   └── test_health.py
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

These steps are intended for local development.

---

## ✅ Prerequisites

Install the following:

* Git
* Docker Desktop
* Python 3.14 or compatible Python 3 version
* VS Code or another code editor

Optional but useful:

* API-Football / API-Sports account for real provider syncing
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

## 🐳 Run with Docker Compose

From the project root:

```bash
docker compose up --build
```

To run in detached mode:

```bash
docker compose up -d --build
```

To stop the project:

```bash
docker compose down
```

To stop and remove volumes:

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
  "version": "0.3.0"
}
```

---

### List Fixtures

```http
GET /fixtures
```

Returns all stored fixtures ordered by kickoff time.

Example response:

```json
{
  "count": 4,
  "fixtures": []
}
```

---

### Get Fixture by ID

```http
GET /fixtures/{fixture_id}
```

Returns one fixture by internal database ID.

Example:

```http
GET /fixtures/1
```

---

### Sync Sample Fixtures

```http
POST /fixtures/sync/sample
```

Loads sample World Cup fixture data into the database.

The sync is idempotent. Running it multiple times updates existing records instead of creating duplicates.

Example response:

```json
{
  "message": "Sample fixtures synced successfully",
  "created": 4,
  "updated": 0,
  "total_sample_fixtures": 4
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

If the key is missing or still set to `replace_me`, the endpoint returns a clear error:

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
  "total_provider_fixtures": 72
}
```

The exact count depends on the provider response.

---

## 🧪 Run Tests Locally

From the project root:

```bash
cd backend
pytest -v
```

Current expected result:

```text
11 passed
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
* provider sync endpoint behavior when API key is missing

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

## 🧾 Environment Variables

Current `.env.example`:

```env
# App
APP_NAME=World Cup 2026 AI Stats
APP_ENV=development
APP_VERSION=0.3.0

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

## 🔒 Security Notes

* `.env` is ignored by Git.
* `.env.example` contains placeholders only.
* API keys must be stored locally or in secure deployment secrets.
* Never commit real provider keys.
* Never paste real API keys into screenshots, README files, commits, or public issues.
* The provider sync endpoint handles missing API keys with a clear error response.
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

Current status: backend implementation completed, live provider sync requires a valid local API key.

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

Still pending / future improvement:

* Obtain valid API-Football / API-Sports key
* Perform live provider smoke test
* Confirm final provider response mapping against real data
* Add dashboard provider/source status indicator

---

### v0.4.0 — Match Completion Detector

Planned:

* Detect newly completed matches
* Track previous match status
* Avoid duplicate notifications
* Prepare completed match payloads for downstream services

---

### v0.5.0 — Telegram Notifications

Planned:

* Telegram bot integration
* Send completed match notifications
* Include scoreline and match metadata
* Add local notification test mode

---

### v0.6.0 — Interactive Dashboard

Planned:

* Fixture filtering
* Group filtering
* Status filtering
* Match detail view
* Provider/source status display

---

### v0.7.0 — Local Llama Summary Agent

Planned:

* Ollama integration
* Generate short match summaries
* Generate daily World Cup summaries
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
| v0.3.0 | Real football API provider layer, provider client, fixture sync service, provider sync endpoint, and mocked tests | In Progress |
| v0.4.0 | Match completion detector | Planned |
| v0.5.0 | Telegram notifications | Planned |
| v0.6.0 | Interactive dashboard improvements | Planned |
| v0.7.0 | Local Llama summary agent | Planned |
| v0.8.0 | Player-level statistics | Planned |
| v0.9.0 | Monitoring and observability | Planned |
| v1.0.0 | Portfolio-ready release | Planned |

---

## 🧪 Current Health Check

Run:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "backend",
  "version": "0.3.0"
}
```

---

## 🧪 Manual API Testing

After starting Docker Compose, try:

### List Fixtures

```bash
curl http://localhost:8000/fixtures
```

### Sync Sample Fixtures

```bash
curl -X POST http://localhost:8000/fixtures/sync/sample
```

### List Fixtures Again

```bash
curl http://localhost:8000/fixtures
```

### Sync Provider Fixtures

```bash
curl -X POST http://localhost:8000/fixtures/sync/provider
```

Without a valid API key, this should return:

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
* environment setup guide
* dashboard usage guide
* future AI summary design
* notification workflow notes

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
v0.3.0 — Real Football API Provider Integration
```

The backend now includes a provider abstraction, API-Football client, fixture sync service, and provider sync endpoint.

Sample fixtures remain available as a safe fallback for local development, public GitHub users, and testing without an API key.

Next recommended step:

```text
Obtain a valid API-Football / API-Sports key and perform a live provider smoke test.
```
