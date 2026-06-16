# ⚽ World Cup 2026 AI Stats Dashboard

![Project Status](https://img.shields.io/badge/status-active%20development-blue)
![Version](https://img.shields.io/badge/version-v0.2.0-orange)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-green)
![Streamlit](https://img.shields.io/badge/dashboard-Streamlit-red)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue)
![Docker](https://img.shields.io/badge/containerized-Docker-blue)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-black)

A self-hosted, containerized, AI-assisted World Cup 2026 match tracking platform built with **FastAPI**, **PostgreSQL**, **Streamlit**, **Docker Compose**, and future integration with **Telegram notifications** and a local **Llama model**.

---

## 📌 Current Version

```text
v0.2.0 — Football API Integration Foundation
```

This version establishes the football data foundation of the project.

At this stage, the project includes:

* FastAPI backend service
* Streamlit dashboard
* PostgreSQL database container
* Docker Compose setup
* Environment variable template
* Backend health check endpoint
* SQLAlchemy database layer
* PostgreSQL-backed fixture model
* Sample World Cup fixture data
* Manual sample fixture sync endpoint
* Fixture listing endpoint
* Fixture detail endpoint
* Streamlit fixture table
* SQLite-based test database
* Fixture endpoint test coverage
* GitHub Actions CI workflow
* Semantic versioning from the first milestone

The project now includes a working fixture database foundation using sample World Cup data.

Real football API integration, finished-match detection, Telegram alerts, player statistics, and local LLM summaries will be added progressively in later versions.

---

## 🧠 Why I Built This

This project started from a simple personal idea:

I wanted a way to follow the World Cup without constantly jumping between live score apps, websites, match pages, and social media updates.

Instead of only seeing the final score, I wanted a system that could detect when a match had finished, send me a message, and give me a link to a dashboard where I could see:

* Match result
* Team statistics
* Player-level breakdowns
* Match timeline
* AI-generated summary
* Key takeaways from the game

But this project is also more than just a football dashboard.

It is part of my journey into **DevOps, Cloud Support, automation, and AI-assisted engineering**.

Coming from a hospitality background, I wanted to build something practical and real-world while applying the technical skills I have been developing:

* Containerization
* Backend API design
* Database integration
* Background workers
* CI/CD
* Secure secret management
* Public dashboard deployment
* Monitoring and observability
* Local LLM experimentation
* Documentation for public GitHub users

The goal is to build something useful, but also to showcase how a modest home-lab style setup can still support a clean, secure, and professional DevOps project.

---

## 🎯 Project Goal

The final goal is to create a self-hosted system that can:

1. Track World Cup 2026 matches.
2. Detect when a match has finished.
3. Fetch final match statistics.
4. Store team and player data in a database.
5. Generate AI-assisted match summaries using a local Llama model.
6. Send a Telegram notification with a dashboard link.
7. Allow the dashboard to be accessed from anywhere.
8. Provide a mobile-friendly interface for quick match review.

---

## 🧱 Current Architecture

Current `v0.2.0` architecture:

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

Current data flow:

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

## 🔮 Planned Future Architecture

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

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Dashboard | Streamlit |
| Database | PostgreSQL |
| ORM / Database Layer | SQLAlchemy |
| Test Database | SQLite |
| Containerization | Docker, Docker Compose |
| Testing | Pytest |
| CI/CD | GitHub Actions |
| Configuration | Environment variables |
| Future AI Layer | Ollama + Llama 1B |
| Future Notifications | Telegram Bot API |
| Future Public Access | Cloudflare Tunnel |
| Future Monitoring | Prometheus + Grafana |

---

## 📁 Project Structure

```text
worldcup-2026-ai-stats/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── fixture.py
│   │   │
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── fixtures.py
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       └── sample_data.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_fixtures.py
│   │   └── test_health.py
│   │
│   ├── Dockerfile
│   ├── pytest.ini
│   └── requirements.txt
│
├── dashboard/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── docs/
│   ├── architecture.md
│   ├── changelog.md
│   └── roadmap.md
│
├── infra/
│   └── docker-compose.yml
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
├── README.md
└── VERSION
```

---

## 🚀 Getting Started

This project is designed to be Docker-first and cross-platform.

It should run on:

* macOS
* Windows
* Linux

The only main requirement is Docker.

---

## ✅ Prerequisites

Install the following:

* Git
* Docker Desktop or Docker Engine
* Docker Compose

Optional for development:

* Python 3.12+
* VS Code
* VS Code Remote SSH extension

---

## 📦 Clone the Repository

```bash
git clone https://github.com/AnarkeyV/worldcup-2026-ai-stats.git
cd worldcup-2026-ai-stats
```

---

## 🔐 Environment Setup

Create your local `.env` file from the example file:

```bash
cp .env.example .env
```

For Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

The `.env` file is ignored by Git and should never be committed.

The `.env.example` file is safe to commit because it only contains placeholders.

---

## 🐳 Run with Docker Compose

From the project root:

```bash
docker compose -f infra/docker-compose.yml up -d --build
```

Check running containers:

```bash
docker compose -f infra/docker-compose.yml ps
```

Expected services:

```text
worldcup-backend
worldcup-dashboard
worldcup-postgres
```

---

## 🌐 Access the Services

Backend health check:

```text
http://localhost:8000/health
```

Dashboard:

```text
http://localhost:8501
```

Expected backend health response:

```json
{
  "status": "healthy",
  "service": "backend",
  "version": "0.2.0"
}
```

---

## 📊 Fixture Endpoints

### List Fixtures

```text
GET /fixtures
```

Returns all stored fixtures ordered by kickoff time.

### Get Fixture by ID

```text
GET /fixtures/{fixture_id}
```

Returns one fixture by internal database ID.

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

## 🧪 Run Tests Locally

From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

For Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

Expected result:

```text
7 passed
```

The test suite uses an in-memory SQLite database, so tests do not require Docker or PostgreSQL to be running.

---

## ⚙️ GitHub Actions CI

This project uses GitHub Actions to run backend tests automatically.

The workflow runs on:

* Push to `main`
* Push to `feature/**` branches
* Pull requests into `main`

Current CI job:

```text
Backend Tests
```

The workflow installs Python dependencies and runs:

```bash
pytest
```

Current test coverage includes:

* Backend health check
* Empty fixture list before sync
* Sample fixture sync
* Fixture list after sync
* Single fixture retrieval
* Missing fixture 404 response
* Idempotent fixture sync behavior

---

## 🧾 Environment Variables

Current `.env.example`:

```env
# App
APP_NAME=World Cup 2026 AI Stats
APP_ENV=development
APP_VERSION=0.2.0

# Database
POSTGRES_USER=worldcup
POSTGRES_PASSWORD=worldcup
POSTGRES_DB=worldcup
DATABASE_URL=postgresql+psycopg://worldcup:worldcup@postgres:5432/worldcup

# Dashboard
DASHBOARD_PORT=8501
BACKEND_API_URL=http://backend:8000

# Football API
FOOTBALL_API_KEY=replace_me
FOOTBALL_API_BASE_URL=https://example.com

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

Because this is a public GitHub repository, secret handling is important.

This project follows these rules:

* `.env` is ignored by Git.
* `.env.example` contains placeholders only.
* API keys must be stored locally or in secure deployment secrets.
* Telegram bot tokens must never be committed.
* Cloudflare tunnel tokens must never be committed.
* Database volumes and local data files must not be committed.
* The local LLM service should not be exposed publicly.
* Internal services such as PostgreSQL, Prometheus, Ollama, and workers should remain private.

Future security improvements:

* Cloudflare Access for protected routes
* Rate limiting
* Dependabot
* Pre-commit secret scanning
* Container image scanning
* Non-root container users
* Production hardening guide

---

## 🧭 Roadmap

### v0.1.0 — Project Foundation

Status: Completed

* Docker Compose setup
* FastAPI backend
* Streamlit dashboard placeholder
* PostgreSQL container
* Backend health check
* Basic pytest test
* GitHub Actions CI
* Version file
* Initial documentation

### v0.1.1 — README and Documentation Polish

Status: Completed

* Capstone-style README
* Personal project story
* Project goals
* Tech stack section
* Roadmap section
* Security notes
* Development setup notes

### v0.2.0 — Football API Integration Foundation

Status: Completed

* SQLAlchemy database layer
* PostgreSQL-backed fixture model
* Sample World Cup fixture data
* Manual sample fixture sync endpoint
* Fixture listing endpoint
* Fixture detail endpoint
* Streamlit fixture table
* SQLite-based test database
* Fixture endpoint test coverage

### v0.3.0 — Real Football API Provider Integration

Status: Planned

* Select football data API provider
* Add provider client service
* Fetch real World Cup fixtures
* Normalize provider responses into the internal fixture model
* Keep sample data as a fallback/demo mode
* Add tests with mocked provider responses
* Update dashboard to show provider/source status

### v0.4.0 — Match Completion Detector

Status: Planned

* Add background worker
* Detect finished matches
* Fetch final match statistics
* Prevent duplicate match processing
* Store final match records

### v0.5.0 — Telegram Notifications

Status: Planned

* Add Telegram bot integration
* Send notification when a match finishes
* Include dashboard link in message
* Add notification status tracking

### v0.6.0 — Interactive Dashboard

Status: Planned

* Finished matches page
* Match detail page
* Team statistics comparison
* Mobile-friendly layout
* Match timeline display

### v0.7.0 — Local Llama Summary Agent

Status: Planned

* Add Ollama integration
* Use local Llama 1B model
* Generate AI-assisted match summaries
* Add fallback when LLM is unavailable
* Store generated summaries in database

### v0.8.0 — Player-Level Statistics

Status: Planned

* Player statistics table
* Team filters
* Player detail page
* Top performers section
* Player comparison view

### v0.9.0 — Monitoring and Observability

Status: Planned

* Prometheus metrics
* Grafana dashboard
* Service health checks
* Failure alerts
* Monitoring documentation

### v1.0.0 — Portfolio Release

Status: Planned

* Full working match tracker
* Public dashboard access
* Telegram notification flow
* AI summary generation
* Complete documentation
* Screenshots
* Deployment guide
* Security guide

---

## 📊 Version History

| Version | Description | Status |
|---|---|---|
| v0.1.0 | Project foundation with Docker, FastAPI, Streamlit, PostgreSQL, pytest, and CI | Completed |
| v0.1.1 | Documentation polish and capstone-style README | Completed |
| v0.2.0 | Football API integration foundation with fixture database, sample sync, dashboard table, and endpoint tests | Completed |
| v0.3.0 | Real football API provider integration | Planned |
| v0.4.0 | Finished-match detection | Planned |
| v0.5.0 | Telegram notifications | Planned |
| v0.6.0 | Interactive dashboard | Planned |
| v0.7.0 | Local Llama summary agent | Planned |
| v0.8.0 | Player-level stats | Planned |
| v0.9.0 | Monitoring and observability | Planned |
| v1.0.0 | Stable portfolio release | Planned |

---

## 🧪 Current Health Check

Current backend endpoint:

```text
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "service": "backend",
  "version": "0.2.0"
}
```

This confirms that the backend service is running correctly.

---

## 🖥️ Development Setup Notes

This project is being developed from a MacBook, with the option to deploy later onto a Windows laptop as a home-lab server.

The intended workflow is:

```text
MacBook
    ↓
VS Code / Terminal
    ↓
GitHub
    ↓
Dockerized deployment
    ↓
Windows laptop or any Docker-capable host
```

The project is designed so that users do not need to match my personal setup.

Anyone should be able to run it locally as long as they have Docker installed.

---

## 📸 Screenshots

Screenshots will be added as the dashboard develops.

Planned screenshots:

* Backend health check
* Streamlit dashboard home page
* Match list page
* Match detail page
* Team stats comparison
* Player stats page
* Telegram notification example
* Grafana monitoring dashboard

---

## 🧠 AI Usage Plan

The local Llama model will not be responsible for fetching data or making uncontrolled decisions.

Instead, the AI layer will be used for controlled summarisation.

Planned flow:

```text
Finished Match Data
    ↓
Structured Stats JSON
    ↓
Local Llama Model
    ↓
Readable Match Summary
    ↓
Saved Report
    ↓
Dashboard + Telegram Link
```

The model will receive structured match statistics and generate concise summaries such as:

* Match overview
* Key turning points
* Team performance summary
* Standout players
* Tactical observations

The AI component will be designed with safety and resource limits in mind because the intended deployment target is modest home-lab hardware.

---

## 🚫 What This Project Is Not

This project is not intended to be:

* A betting tool
* A gambling prediction system
* A replacement for official FIFA data
* A scraper of copyrighted match pages
* A fully autonomous open-ended AI agent

The system is designed to use structured football data from a proper API provider and process it through controlled, auditable workflows.

---

## 📚 Documentation

Additional documentation lives in the `docs/` directory:

```text
docs/
├── architecture.md
├── changelog.md
└── roadmap.md
```

Future documentation will include:

* Deployment guide
* Security guide
* API design notes
* Monitoring guide
* Local LLM setup guide
* Troubleshooting guide

---

## 🧹 Stop the Project

To stop running containers:

```bash
docker compose -f infra/docker-compose.yml down
```

To stop containers and remove local database volume:

```bash
docker compose -f infra/docker-compose.yml down -v
```

Only use `-v` if you are okay deleting local PostgreSQL data.

---

## 👤 Author

**Khairul Rizal**

DevOps and Cloud Support learner building practical projects around automation, infrastructure, observability, and AI-assisted tooling.

GitHub: [AnarkeyV](https://github.com/AnarkeyV)

---

## 📌 Project Status

This project is currently in active development.

Current release:

```text
v0.2.0 — Football API Integration Foundation
```

Next planned milestone:

```text
v0.3.0 — Real Football API Provider Integration
```

The foundation is now able to store and display sample World Cup fixtures. The next step is to connect a real football data provider while keeping sample data available as a fallback for local development and public GitHub users.
