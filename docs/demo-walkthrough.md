# Demo Walkthrough

## Purpose

This walkthrough demonstrates **World Cup 2026 AI Stats v1.11.0** during a portfolio review, technical interview, or self-hosted runtime demo.

The main story is simple:

> Provider data is synced into a self-hosted FastAPI/PostgreSQL system, transformed into match detail and standings, surfaced through a mobile-friendly dashboard, enriched by local AI and deterministic fallbacks, and observed with Prometheus and Grafana.

---

## Demo Prerequisites

Before the demo:

1. Start the Windows Docker runtime.
2. Confirm the backend is healthy.
3. Confirm the public Cloudflare dashboard opens.
4. Do not run provider sync or rich-detail backfill during the demo unless it is explicitly part of the scenario.
5. Keep secrets out of screenshots, shell history, and screen sharing.

Windows PowerShell:

```powershell
cd "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats"

docker compose up -d --build
docker compose ps

curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/ai/health
curl.exe http://localhost:8000/players/leaders
curl.exe http://localhost:8000/ai/insights?limit=5
```

Expected release verification baseline:

```text
184 automated tests passed
```

---

## Suggested 10-Minute Demo Flow

### 1. Start with the Project Story

Open the README or public dashboard.

Explain:

- The project is a self-hosted football intelligence dashboard for World Cup 2026.
- Development runs on a MacBook; the Windows laptop hosts the Docker runtime.
- Cloudflare Tunnel makes the dashboard available on mobile.
- The system combines provider data, PostgreSQL, local AI, Telegram, Prometheus, and Grafana.

Open:

```text
https://wc2026.khairulrizal.qzz.io/dashboard
```

### 2. Show Runtime Health and API Documentation

Open:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

Explain that FastAPI exposes both interactive documentation and a health endpoint.

### 3. Show Structured AI Insights and Group Race

Use **AI Insights** in Quick Links.

Highlight:

- deterministic, fallback-safe insights
- Group Race board
- current top two teams in every populated group
- the ranking uses completed-fixture standings, not a generated prediction

Optional API check:

```powershell
$aiInsights = Invoke-RestMethod -Uri "http://localhost:8000/ai/insights?limit=5"

$aiInsights.group_race.teams_per_group
$aiInsights.metadata.group_race_group_count
```

Explain that the Group Race is designed as a qualification-picture view, rather than a generic top-scoring list.

### 4. Show Provider-Backed Player Leaders

Use **Players** in Quick Links.

Highlight:

- top scorers
- yellow-card leaders
- red-card leaders
- provider coverage statement
- no generic sample data presented as live data
- assist leaders are clearly unavailable if the provider does not supply assist events

Optional API check:

```powershell
curl.exe http://localhost:8000/players/leaders
```

### 5. Show Latest Completed Match

Use **AI Summary** in Quick Links.

Highlight:

- local AI health badge
- tournament summary button
- provider-backed latest completed result
- stored scorer data
- major incident priority when red cards are present

Optional API check:

```powershell
curl.exe http://localhost:8000/ai/latest-completed/summary
```

### 6. Show Rich Match Detail

Use **Fixtures** in Quick Links.

1. Select **Completed**.
2. Choose a group.
3. Open a completed fixture.
4. Show the match detail panel.

Walk through:

- Overview
- Timeline
- Stats
- Lineups
- referee and weather context
- fixture-level summary button

Explain that detail data is stored independently from the core fixture row, so the dashboard can remain usable even when a fixture has no rich detail yet.

### 7. Show Sync and Observability

Use **Sync** in Quick Links.

Highlight:

- source and provider
- last run and last successful sync
- fetched, created, updated, and newly completed counts
- error field

Then show:

```text
http://localhost:8000/metrics
http://localhost:9090
http://localhost:3000
```

Explain that the project includes runtime-level visibility, not just a user interface.

### 8. Explain Local AI and Fallback Safety

Use **AI Summary**.

Explain:

- Ollama runs locally on the Windows host.
- The configured model is `llama3.2:1b`.
- If local AI is unavailable or returns a contradictory result, the system returns deterministic factual fallback text.
- Structured AI Insights and Group Race do not require Ollama.

### 9. Explain Telegram and Mobile Access

Mention:

- Telegram status and test endpoints exist.
- Messages can contain the dashboard URL.
- Cloudflare Tunnel makes that link usable from a phone.
- Tokens and chat IDs are environment-driven and never committed.

---

## Optional Technical Deep Dive

For a backend-focused audience, show these routes:

```text
GET /fixtures
GET /fixtures/{fixture_id}/detail
GET /standings
GET /insights/groups
GET /players/leaders
GET /ai/insights
GET /ai/latest-completed/summary
GET /fixtures/sync/status
GET /ai/health
GET /metrics
```

For a test-focused audience:

```bash
pytest -q
```

For a deployment-focused audience:

```powershell
docker compose ps
```

---

## Safety Notes

- Do not display `.env`.
- Do not paste provider keys, Telegram tokens, or Cloudflare credentials.
- Avoid provider sync in a stable runtime demo unless you intend to change the data.
- A Windows terminal can render accented names incorrectly; use the browser output as the visual source of truth.
- Do not claim assist data exists when the provider response does not supply it.

---

## Recommended Evidence to Capture

- public dashboard on desktop
- public dashboard on mobile
- Group Race board
- player leaders with data coverage note
- latest completed-match card
- rich match timeline with cards and goals
- AI Online health badge
- provider sync runtime panel
- `/docs`
- Prometheus targets
- Grafana dashboard
- Docker Compose services healthy
- test-suite result showing `184 passed`
