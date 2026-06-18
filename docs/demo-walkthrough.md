# Demo Walkthrough

## Purpose

This walkthrough explains how to demonstrate the World Cup 2026 AI Stats Dashboard project during a portfolio review, interview, or technical discussion.

The demo is designed for the current **v1.5.0 — Portfolio Release Polish** release.

---

## Recommended Demo Setup

Use the normal two-machine workflow:

| Machine | Purpose |
|---|---|
| MacBook | Main development/control machine |
| VS Code on MacBook | Editing and Git workflow |
| Windows laptop | Docker/runtime/demo host |
| SSH from MacBook to Windows PowerShell | Optional runtime checks |

The demo can also be run fully on the MacBook if Docker Desktop is available.

---

## Pre-Demo Checklist

Before starting the demo:

```bash
git status
git branch --show-current
cat VERSION
python -m pytest
```

Expected test result:

```text
114 passed
```

Confirm `.env` exists:

```bash
ls -la .env
```

If missing:

```bash
cp .env.example .env
```

Start the stack:

```bash
docker compose up -d --build
```

Confirm containers:

```bash
docker compose ps
```

Expected services:

```text
worldcup-backend
worldcup-dashboard
worldcup-postgres
worldcup-prometheus
worldcup-grafana
```

---

## Demo URLs

| Service | URL |
|---|---|
| Backend root | http://localhost:8000 |
| Health check | http://localhost:8000/health |
| API docs | http://localhost:8000/docs |
| Static dashboard | http://localhost:8000/dashboard |
| Streamlit dashboard | http://localhost:18501 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

Grafana local credentials:

```text
Username: admin
Password: admin
```

---

## Demo Flow

## 1. Start with the README

Open the GitHub repository or local README.

Explain:

```text
This is a World Cup 2026 analytics project built as a DevOps/backend portfolio project.
It includes FastAPI, PostgreSQL, Docker Compose, dashboards, local AI summaries,
Telegram notifications, Prometheus metrics, Grafana dashboards, and automated tests.
```

Point out:

- version badge
- test badge
- tech stack
- architecture section
- API route summary
- monitoring section
- release history

---

## 2. Show the Test Baseline

Run:

```bash
python -m pytest
```

Say:

```text
Before showing the runtime demo, I normally verify the release baseline.
For v1.5.0, the current suite has 114 passing tests.
```

This demonstrates release discipline and confidence.

---

## 3. Start Docker Compose

Run:

```bash
docker compose up -d --build
docker compose ps
```

Explain:

```text
The local runtime uses Docker Compose with backend, dashboard, PostgreSQL,
Prometheus, and Grafana services.
```

---

## 4. Show Backend Health

Open:

```text
http://localhost:8000/health
```

Expected idea:

```json
{
  "status": "healthy",
  "service": "backend",
  "version": "1.5.0"
}
```

Explain:

```text
The health endpoint is useful for quick runtime validation and also confirms the release version.
```

---

## 5. Show FastAPI Docs

Open:

```text
http://localhost:8000/docs
```

Explain:

```text
FastAPI automatically exposes interactive API documentation.
This makes it easy to inspect and test the available endpoints.
```

Point out:

- fixtures
- standings
- insights
- player stats
- AI
- Telegram notifications
- metrics

---

## 6. Sync Sample Fixtures

Run:

```bash
curl -X POST http://localhost:8000/fixtures/sync/sample
```

Then:

```bash
curl http://localhost:8000/fixtures
```

Explain:

```text
This creates or updates sample World Cup fixtures so the rest of the system has data to work with.
```

---

## 7. Show Standings

Open or run:

```bash
curl http://localhost:8000/standings
```

Explain:

```text
The standings service calculates group table information from fixture results.
This includes points, wins, draws, losses, goals, and goal difference.
```

---

## 8. Show Group Insights

Open or run:

```bash
curl http://localhost:8000/insights/groups
```

Explain:

```text
The insights layer turns fixture and standings data into group-level analytics.
```

---

## 9. Show Player Statistics

Run:

```bash
curl -X POST http://localhost:8000/players/stats/sync/sample
curl http://localhost:8000/players/stats
```

Explain:

```text
This adds a player-level analytics layer on top of the team and fixture data.
```

---

## 10. Show Dashboard

Open:

```text
http://localhost:8000/dashboard
```

Also open:

```text
http://localhost:18501
```

Explain:

```text
The project includes both a backend-served static dashboard and a separate dashboard container.
This gives multiple ways to demonstrate the system visually.
```

---

## 11. Show Prometheus

Open:

```text
http://localhost:9090
```

Useful Prometheus checks:

```text
up
```

Explain:

```text
Prometheus scrapes the backend metrics endpoint and gives visibility into service health.
```

---

## 12. Show Grafana

Open:

```text
http://localhost:3000
```

Explain:

```text
Grafana is provisioned through files in the repository.
This means the monitoring dashboard is reproducible when the stack starts.
```

Point out:

- Prometheus datasource
- provisioned dashboard
- local observability workflow

---

## 13. Show Telegram Readiness

Open or run:

```bash
curl http://localhost:8000/notifications/telegram/status
```

Explain:

```text
Telegram integration is optional and controlled through environment variables.
The status endpoint helps verify whether the bot token and chat ID are configured.
```

If credentials are configured, you can test:

```bash
curl -X POST http://localhost:8000/notifications/telegram/test
```

---

## 14. Explain AI Summary Layer

Open or run:

```bash
curl http://localhost:8000/ai/health
```

Explain:

```text
The AI layer is local-first and uses Ollama/Llama.
If Ollama is running, it can generate fixture summaries.
If it is unavailable, the backend should handle that safely.
```

Optional summary endpoint:

```bash
curl http://localhost:8000/ai/fixtures/summary
```

---

## 15. End with Architecture

Open:

```text
docs/architecture.md
```

Explain:

```text
The architecture document shows how the backend, database, dashboard,
AI layer, notification layer, and monitoring stack fit together.
```

This is a strong ending because it moves from demo to system design discussion.

---

## Short Interview Script

Use this if you need a short explanation:

```text
This project is a World Cup 2026 analytics dashboard built with FastAPI, PostgreSQL,
Docker Compose, Prometheus, Grafana, Telegram notifications, and local AI summaries.

I built it milestone by milestone. It started as a simple backend and grew into a
containerized, monitored, tested, and documented system.

The current v1.5.0 release focuses on portfolio polish. The app has 114 passing tests,
a Docker Compose runtime, API documentation, dashboard views, optional Telegram delivery,
optional local Llama summaries, and a provisioned Grafana monitoring dashboard.
```

---

## Cleanup After Demo

Stop the stack:

```bash
docker compose down
```

If you want to remove volumes:

```bash
docker compose down -v
```

Check status:

```bash
docker compose ps
```

---

## Screenshot Checklist

Recommended screenshots for portfolio evidence:

- README top section
- `python -m pytest` showing `114 passed`
- Docker Compose containers running
- `/health`
- `/docs`
- `/fixtures`
- `/standings`
- `/insights/groups`
- `/players/stats`
- static dashboard
- Streamlit dashboard
- Prometheus targets
- Grafana dashboard
- Telegram status endpoint

Suggested local folder:

```text
~/documents/world-cup-ai-stats-screenshots/v1.5.0-portfolio-release
```

---

## Common Demo Problems

### Port 18501 does not open

Check dashboard logs:

```bash
docker compose logs dashboard
```

Confirm the service is running:

```bash
docker compose ps
```

### Backend does not start

Check logs:

```bash
docker compose logs backend
```

Check database:

```bash
docker compose logs postgres
```

### Grafana dashboard missing

Restart Grafana:

```bash
docker compose restart grafana
```

Check provisioning files:

```bash
find monitoring/grafana -type f | sort
```

### AI endpoint unavailable

Check if Ollama is running:

```bash
ollama list
```

If not running, explain that AI is optional and local-first.

### Telegram test fails

Check `.env`:

```bash
grep -n "TELEGRAM" .env
```

Do not show real secrets during a live demo.

---

## Final Demo Message

End with:

```text
The main value of this project is that it combines application development,
DevOps runtime, observability, AI integration, notifications, testing, and documentation
into one practical portfolio project.
```
