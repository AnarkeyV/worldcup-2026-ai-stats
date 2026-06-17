# ⚽ World Cup 2026 AI Stats Dashboard

![FastAPI](https://img.shields.io/badge/backend-FastAPI-green)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-blue)
![Dashboard](https://img.shields.io/badge/dashboard-FastAPI%20Static%20Dashboard-skyblue)
![Docker](https://img.shields.io/badge/container-Docker-blue)
![Python](https://img.shields.io/badge/python-3.14-yellow)
![Version](https://img.shields.io/badge/version-v1.1.2-purple)
![Tests](https://img.shields.io/badge/tests-57%20passed-brightgreen)

A self-hosted, containerized, AI-assisted World Cup 2026 match tracking and insights platform built with **FastAPI**, **SQLAlchemy**, **PostgreSQL-ready database configuration**, **Docker Compose**, a **static dashboard**, and a **local-first Llama/Ollama AI summary workflow**.

This project is intentionally being built in public, milestone by milestone, to demonstrate backend development, API integration, database design, testing, DevOps fundamentals, notification workflows, dashboard development, deterministic AI-assisted summaries, and local-first AI integration.

---

## 📌 Current Version

**v1.1.2 — Version and Container Workflow Cleanup**

This documentation milestone updates the project README after the completed **v1.1.0 Group Standings Engine** milestone.

The application now supports:

- fixture syncing
- fixture filtering
- match completion detection
- Telegram notification workflows
- interactive dashboard cards
- dashboard group standings
- `/standings` API endpoint
- deterministic AI summaries
- standings-aware tournament summaries using `rules_based_v2`
- local Llama/Ollama health checks
- full backend test coverage with **57 passing tests**

---

## ✅ Current Backend Capabilities

- FastAPI backend service
- SQLAlchemy fixture model
- PostgreSQL-ready database configuration
- Sample World Cup fixture data
- Manual sample fixture sync endpoint
- Real provider sync endpoint
- API-Football provider client
- Provider abstraction layer
- Fixture sync service with idempotent create/update logic
- Newly completed fixture detection
- Telegram message formatter
- Telegram send helper with safe credential checks
- Telegram completed-fixture notification helper
- Safe Telegram test notification endpoint
- Sync responses that expose notification status
- API-level fixture filters:
  - group filter
  - status filter
  - team/team-code search
- Group standings calculation service
- `/standings` endpoint
- `/standings?group_name=Group A` filtering
- Static FastAPI dashboard at `/dashboard`
- Dashboard fixture cards
- Dashboard summary stats
- Dashboard group/status/team filters
- Dashboard group standings table
- Dashboard AI summary panel
- Local Llama/Ollama client
- Local Llama health endpoint
- Deterministic AI tournament summary endpoint
- Deterministic single-fixture summary endpoint
- AI summary upgraded to `rules_based_v2`
- Tournament summary includes current group leaders based on completed fixtures
- Mocked provider tests
- Service tests for match completion detection
- Service tests for standings calculation
- Telegram notifier tests
- Route tests for fixture sync and notification behavior
- Standings API route tests
- Dashboard tests
- Local Llama client tests
- AI route tests
- Docker Compose local environment
- GitHub Actions CI
- Local pytest test suite

---

## 🧠 Why I Built This

This project is part of my DevOps and Cloud Support learning journey.

The idea is to build something realistic instead of only following tutorials. A football tournament dashboard gives me a way to practice backend and DevOps concerns such as:

- API design
- database modeling
- external provider integration
- idempotent data sync
- change detection during sync
- notification workflows
- safe secret handling
- Docker-based local development
- CI testing
- deterministic backend logic
- local-first AI integration
- dashboard integration with backend APIs

The World Cup is also a good use case because match data changes over time. Fixtures start as scheduled, later become live or completed, then trigger downstream workflows such as notifications, standings updates, summaries, and dashboard insights.

---

## 🎯 Project Goal

The goal is to build a self-hosted World Cup 2026 statistics platform that can:

1. Store World Cup fixture data.
2. Sync fixture data from sample data or a real football API provider.
3. Display fixtures in a dashboard.
4. Filter fixtures through API query parameters and dashboard controls.
5. Detect completed matches.
6. Send match notifications.
7. Calculate group standings from completed fixtures.
8. Generate deterministic AI-assisted match and tournament summaries.
9. Keep a local Llama/Ollama health check integrated for future local AI workflows.
10. Expand into player-level, team-level, monitoring, and deployment features.
11. Demonstrate practical DevOps, backend, database, notification, dashboard, and AI integration skills.

---

## 🧱 Current Architecture

```text
User / Browser
    |
    v
FastAPI Static Dashboard
    |
    +--> /dashboard
    +--> /static/dashboard.css
    +--> /static/dashboard.js
    |
    v
FastAPI Backend
    |
    +--> /
    +--> /health
    +--> /fixtures
    +--> /fixtures/{fixture_id}
    +--> /fixtures/sync/sample
    +--> /fixtures/sync/provider
    +--> /standings
    +--> /standings?group_name=Group A
    +--> /notifications/telegram/test
    +--> /ai/health
    +--> /ai/fixtures/summary
    +--> /ai/fixtures/{fixture_id}/summary
    |
    v
Services
    |
    +--> Fixture Sync Service
    |       |
    |       +--> Create/update fixture records
    |       +--> Detect newly completed fixtures
    |
    +--> Standings Service
    |       |
    |       +--> Read completed fixture results
    |       +--> Calculate P/W/D/L/GF/GA/GD/Pts
    |       +--> Sort standings by group, points, goal difference, goals for, team
    |
    +--> Notification Helper
    |       |
    |       +--> Telegram Message Builder
    |       +--> Telegram Send Function
    |
    +--> AI Summary Logic
    |       |
    |       +--> Deterministic fixture summary
    |       +--> Deterministic tournament summary
    |       +--> Group leader insight from standings
    |       +--> Local Llama health check
    |
    +--> Sample Fixtures
    |
    +--> API-Football Provider Client
    |
    v
Database
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

The provider sync flow requires a valid local API-Football / API-Sports key to fetch provider data.

### Standings Flow

```text
GET /standings
    |
    v
Read stored fixtures
    |
    v
Filter to completed fixtures with scores
    |
    v
Calculate standings rows
    |
    +--> played
    +--> wins
    +--> draws
    +--> losses
    +--> goals for
    +--> goals against
    +--> goal difference
    +--> points
    |
    v
Return sorted standings table
```

### Dashboard Standings Flow

```text
Browser opens /dashboard
    |
    v
dashboard.js loads fixtures from /fixtures
    |
    v
dashboard.js loads standings from /standings
    |
    v
Render:
    +--> summary cards
    +--> AI summary panel
    +--> filters
    +--> group standings table
    +--> fixture cards
```

### Deterministic AI Summary Flow

```text
GET /ai/fixtures/summary
    |
    v
Read fixtures from database
    |
    v
Build deterministic tournament summary
    |
    +--> completed fixture count
    +--> first completed result summaries
    +--> live fixture count if any
    +--> upcoming fixture count if any
    +--> group leaders from standings engine
    |
    v
Return rules_based_v2 summary
```

### Local Llama Health Flow

```text
GET /ai/health
    |
    v
LocalLlamaClient
    |
    v
Ollama API /api/tags
    |
    v
Return availability, configured model, and available models
```

The dashboard still checks Local Llama/Ollama health, but the tournament and single-fixture summaries are currently deterministic and do not depend on Llama generation.

---

## 🔔 Match Completion Detection

The sync service detects newly completed matches.

A fixture is considered newly completed when:

```text
previous status was not completed
AND
new synced status is completed
```

Completed statuses currently supported by the sync flow include:

```text
complete
FT
AET
PEN
```

The standings service also supports common completed labels such as:

```text
complete
completed
finished
final
ft
full-time
full_time
match finished
```

This supports both local sample data and common football provider status formats.

---

## 📊 Group Standings Engine

The group standings engine is handled through:

```text
backend/app/services/standings_service.py
```

It calculates standings from completed fixtures only.

Each row includes:

```text
group_name
team
team_code
played
wins
draws
losses
goals_for
goals_against
goal_difference
points
```

Sorting order:

```text
group name ascending
points descending
goal difference descending
goals for descending
team name ascending
```

The standings API route is:

```text
backend/app/routes/standings.py
```

Supported endpoints:

```http
GET /standings
GET /standings?group_name=Group A
```

Example response:

```json
{
  "count": 2,
  "filters": {
    "group_name": "Group A"
  },
  "standings": [
    {
      "group_name": "Group A",
      "team": "Mexico",
      "team_code": "MEX",
      "played": 1,
      "wins": 1,
      "draws": 0,
      "losses": 0,
      "goals_for": 2,
      "goals_against": 0,
      "goal_difference": 2,
      "points": 3
    },
    {
      "group_name": "Group A",
      "team": "South Africa",
      "team_code": "RSA",
      "played": 1,
      "wins": 0,
      "draws": 0,
      "losses": 1,
      "goals_for": 0,
      "goals_against": 2,
      "goal_difference": -2,
      "points": 0
    }
  ]
}
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

Example Telegram message format:

```text
🏁 Match Completed

FIFA World Cup 2026
Group Stage

Mexico 2 - 0 South Africa

Venue: Estadio Azteca
```

---

## 🤖 AI Summary Layer

The AI summary layer is currently deterministic for safer, factual dashboard output.

Current summary model label:

```text
rules_based_v2
```

The route still lives under `/ai` because it is the dashboard's AI/insight layer, but the tournament summary does not call Llama generation at the moment.

This decision avoids a previous issue where the model could accidentally describe completed fixtures as upcoming.

Current deterministic summary capabilities:

- completed fixture count
- completed match result summaries
- scheduled fixture count
- live fixture count
- upcoming fixture summaries
- group leader summary based on completed fixtures
- factual single-fixture summaries
- no invented scores for scheduled fixtures

Example tournament summary response:

```json
{
  "fixture_count": 4,
  "provider": "deterministic_tournament_summary",
  "model": "rules_based_v2",
  "summary": "- 4 fixtures have been completed.\n- Mexico defeated South Africa 2-0 in Group A. The match is complete after kicking off on 12 Jun 2026, 3:00 AM SGT at Estadio Azteca. Final whistle time is not available in the current fixture data.\n- United States defeated Paraguay 4-1 in Group D. The match is complete after kicking off on 13 Jun 2026, 9:00 AM SGT at SoFi Stadium. Final whistle time is not available in the current fixture data.\n- Current group leaders based on completed fixtures include Mexico (Group A, 3 pts, +2 GD), United States (Group D, 3 pts, +3 GD), France (Group I, 3 pts, +2 GD), and Argentina (Group J, 3 pts, +3 GD)."
}
```

---

## 🤖 Local Llama / Ollama Health Check

The local Llama client is handled through:

```text
backend/app/services/local_llama_client.py
```

The current implementation uses Python standard library HTTP calls to communicate with Ollama.

Default settings:

```text
LLAMA_BASE_URL=http://127.0.0.1:11434
LLAMA_MODEL=llama3.2:1b
LLAMA_TIMEOUT_SECONDS=60
```

In my local setup:

- MacBook runs the FastAPI backend.
- Windows laptop runs Ollama.
- SSH tunnel forwards MacBook `127.0.0.1:11434` to Windows `127.0.0.1:11434`.
- FastAPI checks the local Ollama API as if it were running locally.

Example SSH tunnel:

```bash
ssh -L 11434:127.0.0.1:11434 <windows-user>@<windows-ip>
```

Example Ollama model used:

```text
llama3.2:1b
```

The Llama integration is currently used for health checking and future local AI expansion. Deterministic rules-based summaries are used for current production-like dashboard summaries.

---

## 📊 API Endpoints

### Root

```http
GET /
```

Example response:

```json
{
  "message": "World Cup 2026 AI Stats API",
  "status": "running",
  "version": "1.1.2",
  "dashboard": "/dashboard",
  "fixtures": "/fixtures",
  "standings": "/standings",
  "ai_summary": "/ai/fixtures/summary"
}
```

---

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "service": "backend",
  "version": "1.1.2"
}
```

---

### List Fixtures

```http
GET /fixtures
```

Returns stored fixtures ordered by kickoff time.

Supports optional filters:

```http
GET /fixtures?group_name=Group A
GET /fixtures?status=complete
GET /fixtures?team=Mexico
GET /fixtures?group_name=Group A&status=complete
```

Example response shape:

```json
{
  "count": 1,
  "filters": {
    "group_name": "Group A",
    "status": "complete",
    "team": null
  },
  "fixtures": []
}
```

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
  "newly_completed_count": 4,
  "newly_completed": [
    "sample-mex-rsa-2026-06-11",
    "sample-usa-par-2026-06-12",
    "sample-fra-sen-2026-06-16",
    "sample-arg-dza-2026-06-16"
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

### List Standings

```http
GET /standings
```

Returns standings calculated from completed fixtures.

Example response shape:

```json
{
  "count": 8,
  "filters": {
    "group_name": null
  },
  "standings": []
}
```

---

### List Standings by Group

```http
GET /standings?group_name=Group A
```

Returns standings for one group only.

---

## 🤖 AI Endpoints

### AI Health Check

```http
GET /ai/health
```

Checks whether the configured local Llama/Ollama endpoint is reachable.

Example response:

```json
{
  "available": true,
  "provider": "local_llama",
  "base_url": "http://127.0.0.1:11434",
  "configured_model": "llama3.2:1b",
  "models": [
    "llama3.2:1b"
  ]
}
```

---

### Generate Tournament Summary

```http
GET /ai/fixtures/summary
```

Generates a short deterministic tournament summary for stored fixtures.

Example response:

```json
{
  "fixture_count": 4,
  "provider": "deterministic_tournament_summary",
  "model": "rules_based_v2",
  "summary": "- 4 fixtures have been completed.\n- Mexico defeated South Africa 2-0 in Group A.\n- Current group leaders based on completed fixtures include Mexico (Group A, 3 pts, +2 GD)."
}
```

---

### Generate Single Fixture Summary

```http
GET /ai/fixtures/{fixture_id}/summary
```

Generates a short deterministic summary for a single stored fixture.

Example response:

```json
{
  "fixture_id": 1,
  "provider": "deterministic_fixture_summary",
  "model": "rules_based_v2",
  "summary": "Mexico defeated South Africa 2-0 in Group A. The match is complete after kicking off on 12 Jun 2026, 3:00 AM SGT at Estadio Azteca. Final whistle time is not available in the current fixture data."
}
```

---

## 🛠️ Tech Stack

| Area | Technology |
|---|---|
| Backend API | FastAPI |
| Database | PostgreSQL-ready configuration |
| ORM | SQLAlchemy |
| Dashboard | FastAPI static HTML/CSS/JS |
| Containerization | Docker Compose |
| Testing | pytest |
| HTTP Client | httpx, urllib standard library |
| Settings | pydantic-settings |
| CI | GitHub Actions |
| Notifications | Telegram Bot API |
| Local AI Health | Ollama / Llama |
| Deterministic Summaries | Rules-based Python service logic |
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
│   │   │   ├── ai.py
│   │   │   ├── dashboard.py
│   │   │   ├── fixtures.py
│   │   │   ├── notifications.py
│   │   │   └── standings.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── fixture_sync_service.py
│   │   │   ├── local_llama_client.py
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
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_ai_routes.py
│   │   ├── test_api_football_provider.py
│   │   ├── test_dashboard.py
│   │   ├── test_fixture_sync_service.py
│   │   ├── test_fixtures.py
│   │   ├── test_health.py
│   │   ├── test_local_llama_client.py
│   │   ├── test_notifications.py
│   │   ├── test_standings_routes.py
│   │   ├── test_standings_service.py
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
APP_VERSION=1.1.2

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

Use `docker compose down -v` carefully because it removes the database volume.

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
| AI Summary API | http://localhost:8000/ai/fixtures/summary |
| Legacy Streamlit Dashboard | http://localhost:8501 |

---

## 🧪 Run Tests Locally

From the project root:

```bash
cd backend
pytest -q
```

Current expected result:

```text
57 passed
```

Warnings may appear depending on the local Python and package versions. Current warnings are not blocking the test suite.

---

## 🧪 Test Coverage Areas

Current tests cover:

- backend health check
- empty fixture list before sync
- sample fixture sync
- fixture list after sync
- fixture filters by group/status/team/team code
- single fixture retrieval
- missing fixture 404 response
- idempotent sample fixture sync behavior
- API-Football provider normalization using a mocked response
- fixture sync service create behavior
- fixture sync service update behavior
- newly completed existing fixture detection
- already completed fixture non-duplication
- sample sync response completion fields
- provider sync endpoint behavior when API key is missing
- Telegram message formatting
- Telegram missing credential handling
- completed fixture notification helper
- safe Telegram test notification endpoint
- standings service calculation
- standings sorting
- standings group filtering
- standings route empty response
- standings route sample-sync response
- standings route group filter
- dashboard page loading
- dashboard static CSS loading
- dashboard static JS loading
- dashboard AI summary UI references
- dashboard group standings UI references
- local Llama client behavior
- AI health route
- deterministic tournament summary route
- deterministic single-fixture summary route
- standings-aware AI summary output
- scheduled fixture summary factual safety

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

- `.env` is ignored by Git.
- `.env.example` contains placeholders only.
- API keys, Telegram secrets, and deployment secrets must be stored locally or in secure deployment secrets.
- Never commit real provider keys.
- Never commit real Telegram bot tokens or chat IDs.
- Never paste real secrets into screenshots, README files, commits, or public issues.
- The provider sync endpoint handles missing API keys with a clear error response.
- Telegram notification sending handles missing credentials safely.
- The local Llama integration should run on trusted local infrastructure.
- Future deployment should use platform secrets instead of plain `.env` files.

---

## 🧭 Roadmap

### v0.1.0 — Project Foundation

Completed:

- FastAPI backend
- Streamlit dashboard folder
- Docker Compose foundation
- PostgreSQL service
- GitHub Actions CI
- Basic documentation

---

### v0.1.1 — README and Documentation Polish

Completed:

- Improved README structure
- Added project purpose
- Added roadmap
- Added setup notes
- Added documentation index

---

### v0.2.0 — Football API Integration Foundation

Completed:

- PostgreSQL-backed fixture model
- Sample World Cup fixture data
- Manual sample fixture sync endpoint
- Fixture list endpoint
- Single fixture retrieval endpoint
- Streamlit fixture table
- Endpoint tests

---

### v0.3.0 — Real Football API Provider Integration

Completed:

- Provider abstraction layer
- API-Football provider client
- Football API environment configuration
- Safe `.env.example` provider documentation
- Provider response normalization
- Fixture sync service
- Idempotent create/update fixture logic
- Sample sync refactored to use sync service
- Provider sync endpoint
- Mocked provider unit test
- Provider endpoint no-key test
- Full backend test suite passing

---

### v0.4.0 — Match Completion Detector

Completed:

- Detect newly completed fixtures during sync
- Support completed statuses: `complete`, `FT`, `AET`, `PEN`
- Avoid duplicate newly completed detection for already completed fixtures
- Expose newly completed fixture IDs in sample sync response
- Expose newly completed fixture IDs in provider sync response
- Service-level tests for completion detection
- Route-level tests for sync response fields
- Full backend test suite passing

---

### v0.5.0 — Telegram Notifications

Completed:

- Telegram settings added
- Telegram notifier service
- Completed fixture Telegram message formatter
- Safe Telegram send function
- Completed fixture notification helper
- Safe Telegram test endpoint
- Telegram notification wiring into fixture sync responses
- Notification skip behavior when no newly completed fixtures exist
- Notification skip behavior when Telegram credentials are missing
- Service-level Telegram tests
- Route-level notification tests
- Full backend test suite passing

---

### v0.6.0 — Interactive Dashboard

Completed:

- Static dashboard route
- Dashboard HTML/CSS/JS
- Fixture summary cards
- Fixture card grid
- Dashboard static asset serving
- Dashboard route tests
- Full backend test suite passing

---

### v0.7.0 — API Filters + Dashboard Polish

Completed:

- API-level fixture filters
- Group filter query parameter
- Status filter query parameter
- Team/team-code search query parameter
- Dashboard query integration
- Team search input
- Group/status dropdown filters
- Visible results count
- Filter reset behavior
- Expanded route tests
- Full backend test suite passing

---

### v0.8.0 — Local Llama Summary Agent

Completed:

- Local Llama/Ollama settings
- Local Llama client service
- AI health endpoint
- AI fixture summary endpoint
- AI single-fixture summary endpoint
- Controlled prompt template for fixture summaries
- Dashboard AI summary panel
- Generate AI Summary button
- Loading and error states in dashboard
- Tests for Local Llama client
- Tests for AI routes
- Dashboard tests updated
- Full backend test suite passing

---

### v1.0.0 — AI Summary Quality and Dashboard Polish

Completed:

- Reworked tournament summary behavior toward deterministic output
- Improved factual safety for completed and scheduled fixtures
- Kept Local Llama health check integrated
- Improved dashboard AI summary behavior
- Strengthened route and dashboard tests
- Full backend test suite passing: `45 passed`

---

### v1.1.0 — Group Standings Engine

Completed:

- Group standings calculation service
- Points, played, wins, draws, losses, goals for, goals against, goal difference
- Standings sorting rules
- `/standings` API endpoint
- `/standings?group_name=Group A` filter
- Dashboard Group Standings section
- Standings table rendering in dashboard JavaScript
- Standings table styling
- AI tournament summary upgraded to `rules_based_v2`
- AI summary now includes current group leaders
- Full backend test suite passing: `57 passed`

---

### v1.1.2 — Version and Container Workflow Cleanup

Completed:

- Refresh README version badges
- Update current feature list
- Document standings engine
- Document rules-based AI summary behavior
- Update API endpoint documentation
- Update project structure
- Update test count
- Update roadmap and project status

---

### v1.2.0 — Team Insights and Group Analytics

Planned:

- Group-level summary endpoint
- Team form summary from completed fixtures
- Best attack / best defence insights
- Dashboard group insight cards
- AI summary improvements using analytics signals

---

### v1.3.0 — Player-Level Statistics

Planned:

- Player statistics model
- Goals, assists, cards, minutes
- Team/player views
- Provider mapping for player data

---

### v1.4.0 — Monitoring and Observability

Planned:

- Prometheus metrics
- Grafana dashboard
- API health metrics
- Provider sync success/failure metrics
- Telegram notification success/failure metrics
- Basic alerting

---

### v1.5.0 — Portfolio Release Polish

Planned:

- Stable local deployment instructions
- Screenshots
- Demo video
- Architecture diagram
- Portfolio-ready release tag

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
| v1.1.1 | README and project documentation refresh | In progress |
| v1.1.2 | Version and container workflow cleanup | Completed |
| v1.2.0 | Team insights and group analytics | Planned |
| v1.3.0 | Player-level statistics | Planned |
| v1.4.0 | Monitoring and observability | Planned |
| v1.5.0 | Portfolio release polish | Planned |

---

## 🧪 Manual API Testing

After starting the backend, try:

### Health Check

```bash
curl http://localhost:8000/health
```

### List Fixtures

```bash
curl http://localhost:8000/fixtures
```

### List Fixtures with Filters

```bash
curl "http://localhost:8000/fixtures?team=Mexico"
curl "http://localhost:8000/fixtures?group_name=Group%20A"
curl "http://localhost:8000/fixtures?status=complete"
```

### Sync Sample Fixtures

```bash
curl -X POST http://localhost:8000/fixtures/sync/sample
```

### List Standings

```bash
curl http://localhost:8000/standings
```

### List Standings by Group

```bash
curl "http://localhost:8000/standings?group_name=Group%20A"
```

### AI Health Check

```bash
curl http://localhost:8000/ai/health
```

### AI Tournament Summary

```bash
curl http://localhost:8000/ai/fixtures/summary
```

### AI Single Fixture Summary

```bash
curl http://localhost:8000/ai/fixtures/1/summary
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
pytest -q
```

### Windows PowerShell

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

---

## 🧠 Local Llama Development Notes

For a local Ollama model on the same machine:

```bash
ollama pull llama3.2:1b
ollama list
```

For MacBook development with Ollama running on a Windows laptop:

```bash
ssh -L 11434:127.0.0.1:11434 <windows-user>@<windows-ip>
```

Then test from the MacBook:

```bash
curl http://127.0.0.1:11434/api/tags
```

Start the FastAPI backend locally from the `backend` folder:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

Test the AI endpoints:

```bash
curl http://127.0.0.1:8000/ai/health
curl http://127.0.0.1:8000/ai/fixtures/summary
```

---

## 📸 Screenshots

Screenshots can be added later for:

- backend health check
- API docs
- sample fixture sync
- fixture list endpoint
- filtered fixture list endpoint
- standings endpoint
- standings group filter endpoint
- dashboard fixture cards
- dashboard group standings table
- dashboard AI summary panel
- provider sync response
- newly completed sync response
- Telegram test endpoint response
- GitHub Actions passing run

Suggested folder:

```text
docs/images/
```

---

## 🧠 AI Usage Plan

This project includes a local AI integration path and a deterministic summary layer.

Current AI/insight usage:

- check local Llama/Ollama health
- summarize stored fixture data with rules-based logic
- summarize completed and scheduled matches factually
- include group leaders in tournament summaries
- display generated summary in the FastAPI dashboard

Future AI usage:

- summarize completed matches automatically
- create daily World Cup recap messages
- explain key match events from structured provider data
- generate short dashboard insights
- help format Telegram alerts
- optionally route specific workflows back through local Llama once factual guardrails are stronger

The AI layer should not replace source football data.

The intended design is:

```text
Structured provider data
    |
    v
Backend validation and storage
    |
    v
Deterministic analytics and guardrails
    |
    v
Optional local Llama/Ollama summary layer
    |
    v
Dashboard output
```

---

## 🚫 What This Project Is Not

This project is not:

- a betting prediction system
- a gambling tool
- a replacement for official FIFA data
- a commercial sports data platform
- a real-time production-grade live-score service yet

The system is designed to use structured football data from a proper API provider and process it through controlled, auditable workflows.

---

## 📚 Documentation

Planned documentation:

- architecture notes
- API design notes
- provider integration notes
- match completion detector notes
- standings engine notes
- Telegram notification notes
- environment setup guide
- dashboard usage guide
- local Llama summary design
- future monitoring design

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
v1.1.2 — Version and Container Workflow Cleanup
```

The backend now supports fixture sync, fixture filtering, completed-match detection, Telegram notification workflows, group standings, dashboard standings, deterministic AI summaries, standings-aware tournament summaries, and Local Llama health checks.

Sample fixtures remain available as a safe fallback for local development, public GitHub users, and testing without provider, Telegram, or external AI credentials.
