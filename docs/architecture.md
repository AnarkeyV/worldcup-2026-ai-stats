# Architecture

## Overview

World Cup 2026 AI Stats Dashboard is designed as a Docker-first, self-hosted application.

The long-term goal is to track World Cup 2026 matches, detect when matches finish, collect team and player statistics, generate AI-assisted summaries through a local Llama model, and send Telegram notifications with dashboard links.

The project is being built progressively so each milestone remains testable and understandable.

---

## Current Architecture - v0.2.0

```text
User Browser
    ↓
Streamlit Dashboard
    ↓
FastAPI Backend
    ↓
SQLAlchemy
    ↓
PostgreSQL Database
```

Current services:

```text
worldcup-dashboard
worldcup-backend
worldcup-postgres
```

---

## Current Data Flow

```text
User clicks "Sync Sample Fixtures"
    ↓
Streamlit sends POST request
    ↓
FastAPI receives /fixtures/sync/sample
    ↓
Sample fixture data is loaded
    ↓
SQLAlchemy inserts or updates records
    ↓
PostgreSQL stores fixture data
    ↓
Dashboard fetches /fixtures
    ↓
Fixture table is displayed
```

---

## Current API Routes

### Health Check

```text
GET /health
```

Returns backend health and version information.

Example response:

```json
{
  "status": "healthy",
  "service": "backend",
  "version": "0.2.0"
}
```

### List Fixtures

```text
GET /fixtures
```

Returns all stored fixtures ordered by kickoff time.

Example response structure:

```json
{
  "count": 4,
  "fixtures": []
}
```

### Get Fixture by ID

```text
GET /fixtures/{fixture_id}
```

Returns one fixture by internal database ID.

If the fixture does not exist, the API returns:

```json
{
  "detail": "Fixture not found"
}
```

### Sync Sample Fixtures

```text
POST /fixtures/sync/sample
```

Loads sample World Cup fixture data into the database.

The sync is idempotent. Running it multiple times updates existing records instead of creating duplicates.

Example response:

```json
{
  "message": "Sample fixtures synced successfully",
  "created": 0,
  "updated": 4,
  "total_sample_fixtures": 4
}
```

---

## Current Database Model

### Fixture

The current fixture model stores:

- External fixture ID
- Competition
- Stage
- Group
- Home team
- Away team
- Team codes
- Kickoff time
- Venue
- Match status
- Home score
- Away score
- Created timestamp
- Updated timestamp

At this stage, datetime fields are stored as strings to keep the API integration foundation simple.

This may be normalized later once the real football data provider is selected and the exact provider response format is confirmed.

---

## Current Backend Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── fixture.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── fixtures.py
│   │
│   └── services/
│       ├── __init__.py
│       └── sample_data.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_fixtures.py
│   └── test_health.py
│
├── Dockerfile
├── pytest.ini
└── requirements.txt
```

---

## Current Dashboard Structure

```text
dashboard/
├── app.py
├── Dockerfile
└── requirements.txt
```

The current dashboard provides:

- Backend health check
- Sample fixture sync button
- Fixture table
- Basic milestone description

---

## Current Infrastructure Structure

```text
infra/
└── docker-compose.yml
```

The current Docker Compose setup runs:

- FastAPI backend
- Streamlit dashboard
- PostgreSQL database

---

## Test Architecture

The application uses different databases depending on context.

### Local Docker Runtime

```text
FastAPI
    ↓
SQLAlchemy
    ↓
PostgreSQL
```

The Docker runtime uses PostgreSQL through Docker Compose.

Database URL:

```text
postgresql+psycopg://worldcup:worldcup@postgres:5432/worldcup
```

### Local and CI Tests

```text
Pytest
    ↓
FastAPI TestClient
    ↓
Dependency Override
    ↓
In-Memory SQLite
```

The test suite uses an in-memory SQLite database.

This means tests do not require:

- Docker
- PostgreSQL
- Running containers
- External API access

This keeps GitHub Actions simple and makes the project easier for other users to clone and test.

---

## Test Coverage - v0.2.0

Current tests cover:

- Backend health check
- Empty fixture list before sync
- Sample fixture sync
- Fixture list after sync
- Single fixture retrieval
- Missing fixture 404 response
- Idempotent fixture sync behavior

Current expected test result:

```text
7 passed
```

---

## Current Docker Runtime

```text
Docker Compose
    ↓
worldcup-postgres
worldcup-backend
worldcup-dashboard
```

Current exposed ports:

| Service | Port | Purpose |
|---|---:|---|
| Backend | 8000 | FastAPI API |
| Dashboard | 8501 | Streamlit dashboard |
| PostgreSQL | 5432 | Local database access |

---

## Current Environment Configuration

Environment variables are defined in:

```text
.env.example
```

Local users create their own private `.env` file:

```bash
cp .env.example .env
```

The `.env` file must not be committed to GitHub.

Current important variables:

```text
APP_NAME
APP_ENV
APP_VERSION
DATABASE_URL
BACKEND_API_URL
FOOTBALL_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
OLLAMA_BASE_URL
OLLAMA_MODEL
PUBLIC_DASHBOARD_URL
```

---

## Future Architecture

```text
Football Data API
    ↓
Scheduled Worker
    ↓
PostgreSQL Database
    ↓
Match Completion Detector
    ↓
Stats Processor
    ↓
Local Llama Summary Agent
    ↓
Telegram Notification
    ↓
Mobile-Friendly Dashboard Link
```

Future services may include:

```text
backend
dashboard
worker
postgres
ollama
prometheus
grafana
cloudflared
```

---

## Future Real Football API Flow

Planned for the next milestone:

```text
User or Worker triggers fixture sync
    ↓
FastAPI calls Football API provider
    ↓
Provider response is validated
    ↓
Provider data is normalized
    ↓
Fixture records are inserted or updated
    ↓
Dashboard displays real fixture data
```

The sample fixture system will remain useful as:

- Demo mode
- Fallback mode
- Local development mode
- Public GitHub onboarding mode

---

## Future Match Completion Flow

```text
Scheduled Worker runs every few minutes
    ↓
Worker checks stored scheduled/live matches
    ↓
Football API returns updated match status
    ↓
System detects completed match
    ↓
Final stats are fetched
    ↓
Match report record is created
    ↓
Telegram notification is sent
    ↓
Dashboard link is included
```

The system should avoid duplicate reports by tracking whether a completed match has already been processed.

---

## Future AI Summary Flow

```text
Finished Match Data
    ↓
Structured Stats JSON
    ↓
Local Llama Summary Prompt
    ↓
Generated Match Summary
    ↓
Saved Report
    ↓
Dashboard and Telegram Link
```

The LLM will be used for controlled summarisation only.

It will not be responsible for fetching data, browsing websites, or making open-ended decisions.

---

## AI Agent Design Principle

The future AI layer will not be an open-ended autonomous agent.

The planned design is a restricted workflow agent.

The LLM will not have:

- Shell access
- Browser access
- File edit access
- Secret access
- Open-ended tool access

It will only receive structured match data and return a readable summary.

This keeps the project safer, easier to debug, and easier to explain publicly.

---

## Future Notification Architecture

Initial notification provider:

```text
Telegram Bot API
```

Planned notification flow:

```text
Match completed
    ↓
Report generated
    ↓
Dashboard URL created
    ↓
Telegram message sent
```

Example future message:

```text
🏁 Match Finished: Mexico 2 - 0 South Africa

📊 Team stats ready
⭐ Player breakdown ready
🤖 AI summary ready

Open dashboard:
https://example.com/matches/sample-mex-rsa-2026-06-11
```

WhatsApp may be considered later, but Telegram is preferred first because it is simpler for development and easier to integrate into a public portfolio project.

---

## Future Public Access Architecture

The intended public access layer is Cloudflare Tunnel.

Planned public route:

```text
User Browser
    ↓
Cloudflare Tunnel
    ↓
Streamlit Dashboard
    ↓
FastAPI Backend
```

The dashboard may be public, but internal services should remain private.

Do not expose publicly:

- PostgreSQL
- Ollama
- Prometheus
- Internal worker services
- `.env` files
- API keys
- Telegram tokens

---

## Future Production-Like Deployment

The intended home-lab deployment will run on a lightweight always-on machine.

The development workflow is:

```text
MacBook
    ↓
VS Code / Terminal
    ↓
GitHub
    ↓
Dockerized Deployment
    ↓
Windows Laptop or Any Docker-Capable Host
```

The project should remain portable across:

- macOS
- Windows
- Linux

The public repository should not depend on the author's personal machine layout.

---

## Security Principles

This project is designed for a public GitHub repository.

Security principles:

- No secrets committed to GitHub
- `.env` remains local only
- `.env.example` contains placeholders only
- Football API keys are stored in environment variables
- Telegram bot tokens are stored in environment variables
- Cloudflare tunnel tokens are stored outside the repo
- PostgreSQL should not be publicly exposed
- Ollama should not be publicly exposed
- Internal workers should not be publicly exposed
- Public dashboard routes should be intentionally limited
- AI agent workflows should be controlled and allowlisted

---

## Current Limitations

As of `v0.2.0`:

- Real football API integration is not added yet
- Match completion detection is not added yet
- Telegram notifications are not added yet
- Llama summaries are not added yet
- Player-level statistics are not added yet
- Monitoring is not added yet
- Public Cloudflare access is not added yet

This version focuses on the fixture database, API, dashboard, and test foundation.

---

## Milestone Summary

### v0.1.0

Project foundation:

- FastAPI backend
- Streamlit dashboard
- PostgreSQL container
- Docker Compose
- Health check
- Basic CI

### v0.1.1

Documentation polish:

- Capstone-style README
- Personal project story
- Setup notes
- Security notes
- Roadmap

### v0.2.0

Football API integration foundation:

- SQLAlchemy database layer
- Fixture model
- Sample fixture data
- Fixture API routes
- Dashboard fixture table
- SQLite test database
- Fixture endpoint test coverage

---

## Next Architecture Milestone

The next planned milestone is:

```text
v0.3.0 — Real Football API Provider Integration
```

The focus will be:

- Selecting a football data API provider
- Creating a provider client service
- Fetching real World Cup fixture data
- Normalizing provider responses
- Keeping sample data as a fallback/demo mode
