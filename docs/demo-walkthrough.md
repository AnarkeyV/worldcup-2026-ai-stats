# Demo Walkthrough

## Purpose

This walkthrough demonstrates **World Cup 2026 AI Stats v1.17.1** during a portfolio review, technical interview, or self-hosted runtime demo.

The main story is simple:

> Provider data is stored in a self-hosted FastAPI/PostgreSQL system, transformed conservatively into a match story, surfaced through a mobile-friendly dashboard, enriched by local AI and deterministic fallbacks, and observed with Prometheus and Grafana.

The important qualifier is equally simple:

> The dashboard shows only stored provider facts that pass its local contracts. It does not turn missing data into a chart, fabricate an event, or scrape video sites.

---

## Demo Prerequisites

Before the demo:

1. Use the already approved Windows Docker runtime; do not build, restart, sync, or alter it only to prepare this walkthrough.
2. Run the read-only runtime status checker and confirm no critical issue is reported.
3. Confirm the public Cloudflare dashboard opens.
4. Do not run provider sync, data backfill, or Telegram test messages during the demo unless that is explicitly the demo scenario.
5. Keep secrets out of screenshots, shell history, and screen sharing.

Windows PowerShell read-only checks:

```powershell
cd "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats"

.\scripts\windows\get-worldcup-runtime-status.ps1
curl.exe http://localhost:8000/fixtures/sync/status
curl.exe http://localhost:8000/players/leaders
curl.exe http://localhost:8000/ai/insights?limit=5
```

Expected source-release verification baseline:

```text
241 automated tests passed
```

---

## Suggested 10-Minute Demo Flow

### 1. Start with the Project Story

Open the README or public dashboard:

```text
https://wc2026.khairulrizal.qzz.io/dashboard
```

Explain:

- The project is a self-hosted World Cup 2026 intelligence dashboard.
- Development happens on a MacBook; the Windows laptop hosts the Docker runtime.
- Cloudflare Tunnel makes the dashboard usable from a phone.
- The system combines provider data, PostgreSQL, local AI, Telegram, Prometheus, and Grafana.
- v1.17.1 keeps the factual match-story design and makes the Windows operating boundary more explicit: Docker recovery is bounded, while Cloudflared and Ollama are inspected rather than automatically changed.

### 2. Show Runtime Health and API Documentation

Open:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

Explain that FastAPI exposes interactive documentation and a health endpoint, while the dashboard remains a separate user-facing view. For an operator-focused audience, show the read-only runtime status script result instead of restarting or reconfiguring anything during the demo.

### 3. Start at Matchday

Use **Matchday** in Quick Links.

Highlight:

- latest live/completed/upcoming context is derived from stored fixture records
- the Data health badge is a local-read coverage signal
- the visual cards and bars do not create a prediction or trigger a provider call

### 4. Show a Completed Match Story

Use **Fixtures** in Quick Links.

1. Select **Completed**.
2. Choose a group.
3. Open a completed fixture.
4. Start with the **Story** tab.

Walk through:

- final score and fixture context
- score progression when the stored goal list matches the final stored score
- key-event sequence for goals, cards, substitutions, and stoppage time
- provider name and stored-detail refresh timestamp
- partial or unavailable states as proof that the system does not invent data

Explain that a score progression is deliberately withheld when the stored goals cannot safely reconcile with the final score.

### 5. Show Stats and Lineups Carefully

Open **Stats** and **Lineups**.

Highlight:

- the statistics view uses only values supplied for both teams
- absent values are not displayed as fake zeroes
- no possession trend, shot map, xG timeline, or momentum chart is claimed unless a provider genuinely supplies the needed event-level data
- the lineup view remains useful even if some event or stat fields are missing

### 6. Show Official Highlights / Watch Safely

Return to **Story**.

Explain:

- Official Watch uses a locally validated outbound-link policy.
- A direct match card appears only after an operator has manually verified a match-specific official link.
- Links open in a new tab; no video is embedded in the dashboard.
- The initial trusted sources are FIFA web, exact FIFA YouTube video URLs, and meWATCH.
- When no verified match-specific link is available, the dashboard says so and can offer clearly labelled FIFA/meWATCH coverage-hub fallbacks.
- Availability may be delayed or territory-dependent, particularly for Singapore-specific meWATCH access.

Do not describe the fallback hub as a match-specific highlight unless it actually is one.

### 7. Show Provider-Backed Player Leaders and Group Race

Use **Players** and **Insights** in Quick Links.

Highlight:

- top scorers, yellow-card leaders, and red-card leaders are derived from stored provider events
- assist leaders remain unavailable if no assist events are supplied
- Group Race shows the current top two teams in each populated group from completed-fixture standings
- these views are deterministic summaries, not generated predictions

### 8. Show Sync and Observability

Use **Sync** in Quick Links.

Highlight:

- source and provider
- last run and last successful sync
- fetched, created, updated, and newly completed counts
- fixed-time schedule and next run when the scheduler is enabled
- no action is taken just by viewing the page

Then show, if relevant:

```text
http://localhost:8000/metrics
http://localhost:9090
http://localhost:3000
```

### 9. Explain Local AI and Fallback Safety

Use **AI Summary**.

Explain:

- Ollama runs locally on the Windows host through a user-level background launcher.
- The configured model is `llama3.2:1b`.
- The Windows runtime status checker verifies both host Ollama and the backend AI view without starting or stopping the model.
- If local AI is unavailable or returns contradictory output, the system returns deterministic factual fallback text.
- Structured AI Insights, Group Race, player leaders, and match story do not require Ollama.

### 10. Explain Mobile Access and Telegram Boundaries

Mention:

- Cloudflare Tunnel makes the dashboard link usable from a phone.
- Telegram status and test endpoints exist, but messages are not sent just by loading the dashboard.
- Scheduled provider syncs and scheduled digests remain separately configured.
- Tokens and chat IDs are environment-driven and never committed.

---

## Optional Technical Deep Dive

For a backend-focused audience, show these read-only routes:

```text
GET /fixtures
GET /fixtures/{fixture_id}/detail
GET /fixtures/{fixture_id}/story
GET /fixtures/data-quality
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
cd backend
source .venv/bin/activate
pytest -q
```

For a deployment-focused audience, show only the current state unless deployment work is explicitly approved:

```powershell
docker compose ps
```

---

## Safety Notes

- Do not display `.env`.
- Do not paste provider keys, Telegram tokens, or Cloudflare credentials.
- Avoid provider sync in a stable runtime demo unless you intend to change data.
- Do not claim a stored empty event array proves no event occurred.
- Do not claim a score progression is live or complete when the system marked it unavailable.
- Do not call a fallback coverage hub a match-specific highlight.
- Do not claim assist data exists when the provider response does not supply it.
- A Windows terminal can render accented names incorrectly; use browser output as the visual source of truth.

---

## Recommended Evidence to Capture

- public dashboard on desktop
- public dashboard on mobile
- Story tab with score progression, key events, and provider provenance
- Story unavailable or partial state to demonstrate data honesty
- Official Watch delayed or region-dependent state
- provider-backed player leaders with data-coverage note
- Group Race board
- local AI health badge and deterministic fallback explanation
- provider sync runtime panel and fixed-time schedule status
- `/docs`
- Prometheus targets
- Grafana dashboard
- Docker Compose services healthy
- test-suite result showing `241 passed`
- read-only Windows runtime status summary showing matching local/public version
