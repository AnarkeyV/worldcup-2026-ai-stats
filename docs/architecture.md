# Architecture

## Overview

World Cup 2026 AI Stats v1.11.0 is a self-hosted football analytics platform built around a FastAPI backend, PostgreSQL, provider-backed match detail, a static browser dashboard, local AI summaries, Telegram notifications, and Prometheus/Grafana observability.

The canonical user interface is the FastAPI-served dashboard:

```text
GET /dashboard
```

The architecture is local-first:

- MacBook Pro for development, tests, Git, and SSH control
- Windows laptop for Docker runtime, Ollama, and public dashboard hosting
- Cloudflare Tunnel for mobile access
- environment variables for provider and Telegram credentials

---

## High-Level Architecture

```text
                         +----------------------------+
                         |        Browser / Phone     |
                         |  Public or local dashboard |
                         +-------------+--------------+
                                       |
                                       v
                         +----------------------------+
                         | Cloudflare Tunnel (optional)|
                         +-------------+--------------+
                                       |
                                       v
+------------------+      +----------------------------+      +----------------------+
| Zafronix Provider|----->| FastAPI Backend            |----->| PostgreSQL           |
| fixture + detail |      | - routes                   |      | fixtures             |
+------------------+      | - dashboard                |      | match_details        |
                          | - services                 |      +----------------------+
+------------------+      | - metrics                  |
| Ollama on Windows|<---->| - local AI client          |      +----------------------+
| llama3.2:1b      |      +-------------+--------------+----->| Prometheus           |
+------------------+                    |                     +----------+-----------+
                                        |                                |
+------------------+                    v                                v
| Telegram Bot API |<---------------- Notification routes          +-------------+
+------------------+                                               | Grafana     |
                                                                   +-------------+
```

---

## Runtime Components

| Component | Responsibility |
|---|---|
| FastAPI backend | API routes, dashboard assets, provider orchestration, summaries, standings, metrics |
| PostgreSQL | Fixture and match-detail persistence |
| Static dashboard | Responsive HTML, CSS, and JavaScript served by FastAPI |
| Zafronix | Provider-backed fixture and match-detail source |
| Ollama | Optional local LLM health and summary generation |
| Telegram Bot API | Optional status and test notifications |
| Prometheus | Metrics collection |
| Grafana | Metrics visualization |
| Cloudflare Tunnel | Optional public/mobile access |
| Docker Compose | Windows runtime orchestration |

---

## Data Model

### Fixture

The fixture record stores the stable match-level information needed for filtering, standings, and basic display:

```text
external ID
competition
stage
group
home team and code
away team and code
kickoff time
venue
status
home score
away score
timestamps
```

### MatchDetail

A separate `match_details` record is associated one-to-one with a fixture when the provider supplies richer data.

Stored detail includes:

```text
provider and provider match ID
goals
cards
substitutions
formations
lineups
team statistics
referee
weather
timestamps
```

Keeping rich detail separate lets the application preserve core fixture functionality even when a provider detail payload is missing or incomplete.

---

## Main API Surface

### Application and Observability

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/` | Project status and route links |
| `GET` | `/health` | Backend health and application version |
| `GET` | `/dashboard` | Static dashboard |
| `GET` | `/docs` | FastAPI interactive docs |
| `GET` | `/metrics` | Prometheus metrics |

### Fixtures

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/fixtures` | List/filter fixtures |
| `GET` | `/fixtures/{fixture_id}` | Get a fixture |
| `GET` | `/fixtures/{fixture_id}/detail` | Get fixture plus stored detail |
| `POST` | `/fixtures/sync/sample` | Sync sample fixtures |
| `POST` | `/fixtures/sync/provider` | Sync configured provider |
| `GET` | `/fixtures/sync/status` | Get latest in-process sync status |

### Standings, Insights, and Players

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/standings` | Calculate group standings |
| `GET` | `/insights/groups` | General group analytics |
| `GET` | `/players/stats` | Existing sample-stat API |
| `POST` | `/players/stats/sync/sample` | Seed sample player stats |
| `GET` | `/players/leaders` | Provider-backed scorer and card leaders |
| `GET` | `/ai/insights` | Structured insights plus Group Race |

### AI

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/ai/health` | Local AI readiness |
| `GET` | `/ai/fixtures/summary` | Tournament summary |
| `GET` | `/ai/fixtures/{fixture_id}/summary` | Fixture summary |
| `GET` | `/ai/latest-completed/summary` | Provider-backed latest result |

### Notifications

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/notifications/telegram/status` | Telegram readiness |
| `POST` | `/notifications/telegram/test` | Telegram test message |

---

## Main Data Flows

### Provider Fixture and Detail Sync

```text
POST /fixtures/sync/provider
        |
        v
configured provider adapter
        |
        v
normalized fixture payload + optional match_detail
        |
        v
fixture sync service
        |
        +--> upsert Fixture
        |
        +--> upsert MatchDetail
        |
        v
PostgreSQL
        |
        v
dashboard, standings, leaders, summaries, metrics
```

### Match Detail View

```text
Browser selects fixture
        |
        v
GET /fixtures/{fixture_id}/detail
        |
        v
Fixture + MatchDetail response
        |
        v
Overview / Timeline / Stats / Lineups tabs
```

### Provider Leaderboards

```text
Completed fixtures + stored MatchDetail events
        |
        v
provider_leaderboard_service
        |
        +--> goals grouped by player
        +--> yellow cards grouped by player
        +--> red cards grouped by player
        |
        v
GET /players/leaders
        |
        v
Dashboard Player Leaders
```

Assist rankings are not inferred unless assist events exist in the stored provider payload.

### Group Race

```text
Completed fixtures
        |
        v
standings service
        |
        v
ranked teams per group
        |
        v
top two positions per group
        |
        v
GET /ai/insights
        |
        v
Structured AI Insights Group Race board
```

### Local AI and Deterministic Fallback

```text
fixture context
        |
        v
Local Llama client -> Ollama
        |
        +--> valid summary -> return live output
        |
        +--> unavailable/contradictory output -> deterministic fallback
```

Structured AI Insights, Group Race, player leaders, and latest-result data do not require Ollama.

---

## Dashboard Architecture

The static dashboard uses:

```text
backend/app/static/dashboard.html
backend/app/static/dashboard.css
backend/app/static/dashboard.js
```

Major sections:

```text
Overview
Provider Sync Runtime
AI Fixture Summary
Latest Completed Match
Structured AI Insights
Group Race
Filters
Group Insights
Player Leaders
Group Standings
Status-first Fixture Browser
Rich Match Detail
```

The dashboard has sticky Quick Links navigation and responsive layouts for desktop and smaller screens.

---

## Observability

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
Grafana
```

The system records:

- HTTP request metrics
- application version metrics
- fixture-sync status and duration
- fetched, created, updated, and newly completed fixture counts
- dashboard-visible runtime sync state

---

## Configuration and Secrets

Configuration is environment-driven.

Primary files:

```text
.env.example
.env
backend/app/config.py
VERSION
```

Version consistency tests compare:

```text
VERSION
APP_VERSION in .env.example
default app_version in backend/app/config.py
```

Secrets must remain local:

```text
Zafronix key
API-Football key
Telegram token
Telegram chat ID
Cloudflare credentials
database credentials
```

---

## Testing and Release Verification

The v1.11.0 verification baseline is:

```text
184 passed
```

Coverage includes:

- fixtures and provider sync
- rich match-detail persistence
- AI summaries and deterministic fallbacks
- Group Race
- provider leaderboards
- dashboard static assets and logic markers
- standings, group insights, player stats, notifications, metrics, and release workflow

---

## Known Constraints

- The system is self-hosted and does not implement production authentication.
- Provider data quality determines available event detail.
- Assist leaders are unavailable when the provider does not supply assist events.
- Local Llama depends on Ollama availability on the Windows host.
- The public dashboard is dependent on the Windows runtime and Cloudflare Tunnel remaining online.
- Sync runtime state is intentionally lightweight; future work can persist historical sync runs.
