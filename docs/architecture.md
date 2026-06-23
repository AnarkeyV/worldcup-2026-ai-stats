# Architecture

## Overview

World Cup 2026 AI Stats is a self-hosted football analytics platform built around a FastAPI backend, PostgreSQL, provider-backed match detail, a static browser dashboard, local AI summaries, Telegram notifications, and Prometheus/Grafana observability.

The current release is **v1.14.0**. It adds a read-only tournament-wide Match Data Coverage view over locally stored fixture and match-detail records, while preserving the project's local-first and no-live-lookup boundaries.

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
| PostgreSQL | Fixture, match-detail, and persisted sync-run state |
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

The v1.13.0 event-integrity work deliberately does not add a new database table or migration. It operates on the existing stored JSON-style event arrays.

---

## Canonical Provider Event Integrity

The shared `provider_event_integrity` service is used at three boundaries:

```text
provider payload
        |
        v
Zafronix detail normalization
        |
        v
match-detail persistence
        |
        v
stored MatchDetail event arrays
        |
        +--> provider leaderboards
        |
        +--> latest completed-result summary
        |
        +--> match-detail dashboard timeline
```

### Canonical event rules

For goals, cards, and substitutions, the service:

- accepts only supported object shapes
- trims safe string fields
- accepts only supported sides: `home` or `away`
- requires the meaningful participant fields for that event type
- normalizes event minutes without inventing a value
- removes exact duplicates after normalization
- orders timed events chronologically
- retains valid untimed events after timed events

The implementation does not infer assists, player identities, teams, event minutes, score reconciliation, or unprovided event facts.

### Read-time protection

Provider leaderboards and latest-result summaries canonicalize stored event arrays again when reading them. This makes those reader paths resilient to older or malformed persisted event arrays without mutating history as a side effect.

Current-record correction behaviour remains simple:

```text
later approved provider refresh
        |
        v
replace existing stored match-detail event arrays
```

Historical event-correction/version storage, provider event IDs, and event-level audit history are deferred to a future milestone.

---

## Stored Detail Coverage Contract

`GET /fixtures/{fixture_id}/detail` is read-only and returns:

```text
fixture
detail_available
detail
stored_event_coverage
```

`stored_event_coverage` is a factual description of the local record:

| State | Meaning |
|---|---|
| `unavailable` | No stored `MatchDetail` record exists. No live provider lookup was attempted. |
| `recorded` | The last stored provider payload contains one or more events of that type. |
| `no_stored_events` | A stored detail record exists, but the last payload contains zero events of that type. This does not prove none occurred in the match. |

The contract includes separate coverage for:

```text
goals
cards
substitutions
```

It also exposes the stored provider name and stored-detail refresh timestamp. The endpoint does not call an external provider on read.

---

## Match Data Quality Contract

`GET /fixtures/data-quality` provides a local aggregate for the selected fixture scope.

Optional filters:

```text
group_name
team
missing_detail_limit
```

The endpoint returns:

```text
filters
summary
event_coverage
missing_detail_fixture_count
missing_detail_limit
missing_detail_fixtures
message
```

`summary` distinguishes:

| State | Meaning |
|---|---|
| `unavailable` | The selected scope contains no completed fixtures, so stored-detail coverage cannot be calculated. |
| `partial` | At least one completed fixture has stored detail and at least one does not. |
| `complete` | Every completed fixture in scope has stored detail. |

The aggregate counts stored detail only for completed fixtures. It also reports goal, card, and substitution coverage as counts of fixtures with recorded events, fixtures with an empty stored event array, fixtures without stored detail, and total stored events.

The missing-detail list is bounded for dashboard follow-up. This is a local-read quality signal: it does not trigger provider sync, backfill missing records, infer events, validate provider completeness, or mutate stored history.

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
| `GET` | `/fixtures/data-quality` | Get aggregate local stored-detail coverage |
| `GET` | `/fixtures/{fixture_id}` | Get a fixture |
| `GET` | `/fixtures/{fixture_id}/detail` | Get fixture, stored detail, and stored event coverage |
| `POST` | `/fixtures/sync/sample` | Sync sample fixtures |
| `POST` | `/fixtures/sync/provider` | Sync configured provider |
| `GET` | `/fixtures/sync/status` | Get latest persisted sync status |
| `GET` | `/fixtures/sync/history` | Get recent persisted sync-run history |

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
| `GET` | `/ai/insights` | Deterministic structured insights |

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
normalized fixture payload + canonical optional match_detail events
        |
        v
fixture sync service
        |
        +--> upsert Fixture
        |
        +--> upsert MatchDetail with canonical event arrays
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
Fixture + stored MatchDetail + stored_event_coverage
        |
        v
Overview / Timeline / Stats / Lineups tabs
```

The Overview tab shows a compact stored-detail coverage block before the provider-backed facts. It is a transparent representation of local stored data, not a live match lookup.

### Match Data Quality View

```text
Browser dashboard panel
        |
        v
GET /fixtures/data-quality
        |
        v
Filtered local Fixture rows + local MatchDetail rows
        |
        v
Completed-fixture coverage, event coverage, bounded missing-detail list
        |
        v
Match Data Coverage panel and fixture follow-up links
```

This flow remains read-only. It does not request provider data, trigger sync, or write to the database.

### Provider Leaderboards

```text
Completed fixtures + stored MatchDetail events
        |
        v
canonical provider event reader
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

Structured AI Insights, Group Race, player leaders, latest-result data, and stored-event coverage do not require Ollama.

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
Match Data Coverage
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

Match Detail has four tabs:

```text
Overview
Timeline
Stats
Lineups
```

The Overview tab includes a compact, mobile-friendly stored-detail coverage block that states whether the dashboard has stored detail, when that local payload was refreshed, and whether goals, cards, or substitutions were recorded in it.

The Match Data Coverage panel aggregates that local stored state across completed fixtures. It displays scope-aware coverage, event-array counts, and a bounded set of completed fixtures without stored detail. Its refresh action makes a GET request only.

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
- persisted sync-run status and history
- dashboard-visible freshness state

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

The v1.12.0 release verification baseline is:

```text
196 passed
```

The v1.13.0 release verification is:

```text
202 passed
```

The v1.14.0 release verification is:

```text
205 passed
```

Coverage includes:

- provider fixture and rich-detail sync
- canonical goals, cards, and substitutions
- duplicate handling and later-detail replacement behaviour
- stored-detail coverage semantics
- aggregate Match Data Coverage states, filters, event counters, and bounded missing-detail follow-up
- leaderboards and latest-result summaries
- dashboard static assets and logic markers
- AI summaries and deterministic fallbacks
- Group Race, standings, group insights, player stats, notifications, metrics, and release workflow

---

## Known Constraints

- The system is self-hosted and does not implement production authentication.
- Provider data quality determines available event detail.
- A stored empty event array does not prove a match had no events.
- Historical event correction/version storage is not implemented.
- Provider event identifiers are not currently stored.
- Assist leaders are unavailable when the provider does not supply assist events.
- Local Llama depends on Ollama availability on the Windows host.
- The public dashboard is dependent on the Windows runtime and Cloudflare Tunnel remaining online.
- Automatic sync and sync-generated Telegram alerts remain disabled unless explicitly configured.
- Match Data Coverage measures local stored-data presence; it does not certify provider completeness or factual correctness.
