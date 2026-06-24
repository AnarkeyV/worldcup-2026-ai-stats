# Architecture

## Overview

World Cup 2026 AI Stats is a self-hosted football analytics platform built around a FastAPI backend, PostgreSQL, provider-backed match detail, a static browser dashboard, local AI summaries, Telegram notifications, and Prometheus/Grafana observability.

The current release is **v1.17.1 — Runtime Reliability Safeguards**. It retains the v1.17.0 read-only match-story and Official Watch design while adding a safe Windows operator status checker, local/public version-consistency reporting, and explicit report-only boundaries for Cloudflared and Ollama. Docker/container recovery remains bounded to the existing Windows runtime scripts.

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
+------------------+      +----------------------------+      +------------------------+
| Zafronix Provider|----->| FastAPI Backend            |----->| PostgreSQL             |
| fixture + detail |      | - routes                   |      | fixtures               |
+------------------+      | - dashboard                |      | match_details          |
                          | - story service            |      | official_match_videos  |
+------------------+      | - metrics                  |      +------------------------+
| Ollama on Windows|<---->| - local AI client          |
| llama3.2:1b      |      +-------------+--------------+----->| Prometheus             |
+------------------+                    |                     +----------+-------------+
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
| FastAPI backend | API routes, dashboard assets, provider orchestration, match-story construction, summaries, standings, metrics |
| PostgreSQL | Fixture, match-detail, official-video registry, and persisted sync-run state |
| Static dashboard | Responsive HTML, CSS, and JavaScript served by FastAPI |
| Zafronix | Provider-backed fixture and match-detail source |
| Ollama | Optional local LLM health and summary generation |
| Telegram Bot API | Optional test notifications and one-message scheduled matchday digests |
| Prometheus | Metrics collection |
| Grafana | Metrics visualisation |
| Cloudflare Tunnel | Optional public/mobile access |
| Docker Compose | Windows runtime orchestration and bounded container recovery |
| Windows runtime status checker | Read-only operator view; reports Docker, endpoints, Cloudflared, public reachability, Ollama, AI, task state, and version consistency |

---

## Data Model

### Fixture

A `Fixture` stores stable match-level information used for filtering, standings, and baseline display:

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

A `MatchDetail` is associated one-to-one with a fixture when the provider supplies richer data:

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

Rich detail remains separate from the core fixture row so that fixture browsing, standings, and availability remain usable even when a provider detail payload is absent or incomplete.

### OfficialMatchVideo

`OfficialMatchVideo` is a small local registry of manually verified, outbound-only destinations:

```text
fixture ID
source key
content type
title
external URL
territory
match-specific flag
published timestamp
verification timestamp
creation and update timestamps
```

There is no public write endpoint, crawler, import-on-read flow, or automatic discovery service. The record is deliberately designed for a future controlled curator workflow.

The project continues to use SQLAlchemy metadata bootstrap. On a later approved runtime deployment, the existing bootstrap can create the empty `official_match_videos` table. This release does not backfill records, migrate historical data, or change active runtime data before deployment approval.

---

## Provider Event Integrity

The shared `provider_event_integrity` service is used at three boundaries:

```text
provider payload
        |
        v
Zafronix detail normalisation
        |
        v
match-detail persistence
        |
        v
stored MatchDetail event arrays
        |
        +--> provider leaderboards
        +--> latest completed-result summary
        +--> match-detail timeline
        +--> match-story contract
```

For goals, cards, and substitutions, the service:

- accepts only supported object shapes
- trims safe string fields
- accepts only `home` or `away` sides
- requires meaningful participant fields for that event type
- normalises event minutes without inventing a value
- removes exact duplicates after normalisation
- orders timed events chronologically
- retains valid untimed events after timed events

The implementation does not infer assists, player identities, teams, event minutes, score reconciliation, or unprovided event facts.

---

## Match Story Contract

`GET /fixtures/{fixture_id}/story` is a read-only local composition route.

```text
fixture ID
        |
        +--> local Fixture row
        +--> local MatchDetail row
        +--> local OfficialMatchVideo rows
        |
        v
match_story_service + official_match_video_service
        |
        v
fixture + story response
```

The route does not call a provider, write to the database, trigger sync work, scrape sites, follow redirects, send a message, or alter scheduler state.

### Contract sections

```text
fixture
story.state
story.source
story.score_progression
story.timeline
story.statistics
story.official_watch
```

`story.source` exposes the local data mode, stored-detail availability, provider identity, provider match ID, and stored-detail refresh timestamp.

### Score progression

A score progression is available only when all of these are true:

1. Fixture home and away scores are stored non-negative integers.
2. Every stored goal is a supported record with a valid team side and usable minute.
3. Goal counts by side match the stored final score exactly.

When any condition fails, the contract returns an unavailable state and a reason. It does not invent a goal time, infer an own goal, guess a penalty, or draw an incomplete score trace.

### Timeline

The timeline combines stored goals, cards, and substitutions. It preserves valid stoppage time such as `45+2` and `90+5`. Valid untimed events can appear after timed events but are never assigned an invented minute.

### Statistics

The statistic normaliser considers a defined practical set of metrics:

```text
possessionPct
shotsTotal
shotsOnGoal
expectedGoals
passesAccurate
corners
fouls
```

A metric is shown only when both home and away values are finite provider-supplied numbers. If a metric is present for only one side, it is reported as incomplete and omitted from the comparison view. Missing values are not converted to zero.

---

## Official Watch Policy

The official-watch service builds trusted, outbound-only link cards from local records.

```text
local OfficialMatchVideo record
        |
        v
source key / URL / content type / territory / verification validation
        |
        +--> accepted: safe external card
        |
        +--> rejected: omitted from response
```

### Initial allowed sources

| Source key | Allowed hosts | Notes |
|---|---|---|
| `fifa_web` | `fifa.com`, `www.fifa.com`, `plus.fifa.com`, `vod.fifa.com` | HTTPS and non-root direct path required |
| `fifa_youtube` | `youtube.com`, `www.youtube.com` | Exact supported video URL required; generic channel paths are rejected |
| `mediacorp_mewatch` | `mewatch.sg`, `www.mewatch.sg` | Singapore availability may apply |

A record must also:

- have an allowed content type: `highlights`, `full_match`, `live`, or `recap`
- be explicitly match-specific
- have a title and verification timestamp
- use HTTPS without credentials in the URL
- pass the source-specific host and path checks

Accepted links are returned with:

```text
target="_blank"
rel="noopener noreferrer"
```

The service exposes official FIFA and meWATCH coverage-hub fallbacks when no verified match-specific record exists. Fallbacks are labelled as coverage hubs and are never represented as match-specific videos.

### Explicit exclusions

- no scraping or page parsing
- no automatic search or platform discovery
- no download, rehosting, or thumbnail proxying
- no iframe embed
- no fan upload, mirror, short-link, or arbitrary sports-news URL
- no region bypass or rightsholder circumvention
- no public API that inserts links into the registry

---

## Existing Stored-Data Contracts

`GET /fixtures/{fixture_id}/detail` remains the raw stored-detail route. `GET /fixtures/data-quality` remains a local aggregate of stored detail coverage for completed fixtures. Both perform local reads only and do not certify provider completeness or factual truth beyond the stored record.

The v1.17.0 story contract builds on these records without replacing them.

---

## Dashboard Architecture

The static dashboard uses:

```text
backend/app/static/dashboard.html
backend/app/static/dashboard.css
backend/app/static/dashboard.js
```

The match-detail panel now has four tabs:

```text
Story
Timeline
Stats
Lineups
```

The Story tab prioritises a compact visual account of what happened:

```text
stored score + reconciled goal events
        |
        v
score progression
        |
        +--> key-event sequence
        +--> paired stat comparisons
        +--> official watch state/cards
```

Timeline, Stats, and Lineups remain available for deeper inspection. The existing dashboard is responsive; mobile layout uses stacked reading order and clear unavailable/partial states rather than forcing dense visualisations.

Dashboard asset URLs use the v1.17.0 cache-bust suffix so returning browsers receive the Story and Official Watch JavaScript and CSS.

---

## Fixed-Time Provider Sync and Telegram Digest

v1.16.0 fixed-time scheduling remains unchanged.

Default configuration:

```text
timezone: Asia/Singapore
slots:    03:45, 09:45, 12:45
```

The scheduler is opt-in and waits for the next future configured slot after startup or restart. Scheduled Telegram digests remain separately controlled and disabled by default.

The match-story route and dashboard Story tab do not trigger sync, backfill match detail, alter the scheduler, send Telegram, or call the provider.

---

## Windows Runtime Reliability Boundary

The Windows runtime separates bounded Docker recovery from sensitive host-service operations:

```text
startup/watchdog scripts
        |
        +--> may start Docker Desktop and recover unhealthy Docker containers
        |
        +--> report-only: Cloudflared service state and public health
        |
        +--> report-only: host Ollama API, application AI health, and Ollama task state
```

`get-worldcup-runtime-status.ps1` is a local diagnostic script. It reports:

- Docker engine and Compose service state
- local backend and dashboard health
- Cloudflared service state and public health
- local and public application versions, including a mismatch warning
- host Ollama model availability, application AI health, and the user-level Ollama launcher task

It does not start, stop, restart, rebuild, sync, send, reconfigure, create, delete, or display active secrets. `docs/windows-runtime-recovery.md` records the human-approved recovery sequence for tunnel, Ollama, and Docker incidents.

---

## Configuration and Secrets

Configuration remains environment-driven.

Primary files:

```text
.env.example
.env
VERSION
backend/app/config.py
```

Version consistency tests compare:

```text
VERSION
APP_VERSION in .env.example
default app_version in backend/app/config.py
```

The v1.17.1 source package updates only the safe version declarations. It does not modify an active `.env` file. Any active runtime `APP_VERSION` update is handled only through an approved candidate-and-backup deployment workflow.

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

v1.17.1 local regression verification:

```text
241 passed, 296 warnings
```

The warnings are existing FastAPI/Starlette Python 3.14 deprecations related to `asyncio.iscoroutinefunction`; they are not test failures.

Coverage includes:

- match-story score reconciliation and unavailable states
- stoppage-time event ordering
- timeline and partial-data handling
- paired-stat normalisation that rejects missing or invalid values
- official source, URL, content-type, territory, and verification validation
- rejected generic YouTube, unsafe scheme, non-match-specific, and unverified records
- official fallback-link states
- dashboard Story and Official Watch rendering markers
- release version consistency and cache-busted static assets
- Windows runtime report-only safeguards and version-consistency status reporting
- existing provider sync, scheduler, Telegram, AI, standings, player, metrics, and dashboard coverage

---

## Known Constraints

- The system is self-hosted and does not implement production authentication.
- Provider data quality determines available event detail.
- A stored empty event array does not prove a match had no events.
- Score progression intentionally disappears when stored events cannot reconcile with the stored score.
- Provider event identifiers and historical event-correction/version storage are not implemented.
- No automated official-video discovery or curator import workflow is implemented yet.
- Official match-video availability can be delayed or region-dependent.
- Local Llama depends on Ollama availability on the Windows host.
- The public dashboard depends on the Windows runtime and Cloudflare Tunnel remaining online.
- Project scripts report Cloudflared and Ollama failure rather than attempting sensitive automatic repair; a human-approved recovery action is required.
- Match Data Coverage measures stored-data presence; it does not certify provider completeness or factual correctness.
- Dashboard visuals are descriptive stored-data views, not predictive analytics or qualification simulations.
