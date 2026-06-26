# Architecture

## Overview

World Cup 2026 AI Stats is a self-hosted football analytics platform built around a FastAPI backend, PostgreSQL, provider-backed match detail, a static browser dashboard, local AI summaries, Telegram notifications, and Prometheus/Grafana observability.

The current release is **v1.19.0 — Freshness Context & Matchday Trust Signals**.

The platform remains local-first:

- **MacBook Pro:** development, tests, Git, and SSH control.
- **Windows laptop:** Docker runtime, Ollama host, and public dashboard host.
- **Cloudflare Tunnel:** optional public/mobile access.
- **Environment variables:** provider and Telegram credentials.

The canonical browser interface remains:

```text
GET /dashboard
```

## High-level architecture

```text
+-----------------------------+
| Browser / phone             |
| Local or public dashboard   |
+--------------+--------------+
               |
               v
+-----------------------------+
| Cloudflare Tunnel (optional)|
+--------------+--------------+
               |
               v
+-------------------+     +------------------------------+
| Provider adapters | --> | FastAPI backend              |
| fixtures + detail |     | routes, dashboard, services  |
+-------------------+     +--------------+---------------+
                                         |
                                         v
                           +------------------------------+
                           | PostgreSQL                   |
                           | fixtures                     |
                           | match_details                |
                           | fixture_sync_runs            |
                           | match_detail_event_coverage  |
                           | fixture_sync_change_sets     |
                           | official_match_videos        |
                           +------------------------------+
                                         |
        +--------------------+-----------+-----------+--------------------+
        |                    |                       |                    |
        v                    v                       v                    v
   Ollama host          Prometheus               Telegram             Grafana
   local AI             metrics                  optional alerts      monitoring
```

## Runtime components

| Component | Responsibility |
|---|---|
| FastAPI backend | API routes, static dashboard, provider orchestration, Match Story, Live Match Centre, summaries, standings, and metrics |
| PostgreSQL | Stored fixtures, rich detail, sync audit state, v1.18 coverage/change evidence, and official-video registry |
| Static dashboard | Responsive HTML, CSS, and JavaScript served by FastAPI |
| Provider adapters | Normalise provider fixture/detail payloads into the application’s stored contract |
| Ollama | Optional local LLM health and summary generation |
| Telegram Bot API | Optional test notifications and scheduled matchday digests |
| Prometheus | Metrics collection |
| Grafana | Metrics visualisation |
| Cloudflare Tunnel | Optional public/mobile access |
| Docker Compose | Windows runtime orchestration and bounded container recovery |
| Windows runtime status checker | Read-only operator status and local/public version consistency |

## Stored data model

### Fixture

A `Fixture` stores match-level information used for filtering, standings, Matchday display, and Live Match Centre classification:

```text
external ID
competition
stage
group
home and away teams/codes
kickoff time
venue
stored status
home and away score
creation/update timestamps
```

### MatchDetail

A `MatchDetail` is one-to-one with a fixture when richer provider detail exists:

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

Rich detail remains separate from the core fixture row. Fixture browsing, standings, and freshness remain usable when provider detail is missing or incomplete.

### MatchDetailEventCoverage

`MatchDetailEventCoverage` is an additive v1.18 companion record per fixture. It records whether the currently stored provider payload explicitly covered each of:

```text
goals
cards
substitutions
```

The record allows the application to distinguish:

```text
available
not_provided
coverage_unknown
detail_not_available
```

It does not certify that the provider had complete match coverage.

### FixtureSyncChangeSet

`FixtureSyncChangeSet` is an additive v1.18 companion record for a successful stored sync run. It retains a compact factual change summary produced from the prior local snapshot and the newly stored snapshot.

It records only observed local deltas such as:

```text
score_changed
status_changed
match_completed
goal_added
card_added
substitution_added
provider_event_record_revised
```

A first locally observed fixture does not claim that all present score or event data is new. A historical sync before v1.18 change capture has no companion record and is reported as:

```text
not_recorded_before_v1_18
```

### OfficialMatchVideo

`OfficialMatchVideo` remains a local registry of manually verified, outbound-only destinations. It has no public write endpoint, crawler, import-on-read flow, or automatic discovery service.

## Provider normalisation and event integrity

Provider payloads pass through conservative normalisation before storage.

```text
provider payload
      |
      v
fixture and detail normalisation
      |
      v
provider_event_integrity
      |
      v
stored Fixture / MatchDetail
      |
      +--> Match Story
      +--> player leaders
      +--> latest completed-result summary
      +--> Live Match Centre
```

For goals, cards, and substitutions, the canonical event layer:

- accepts only supported event shapes;
- normalises safe string fields and `home`/`away` sides;
- requires meaningful participant data for the event type;
- keeps provider minutes only when usable;
- removes exact normalised duplicates;
- orders valid timed events chronologically;
- keeps valid untimed events without inventing a minute.

It does not infer assists, player identities, missing teams, event minutes, score reconciliation, or any unprovided fact.

## Live Match Centre

`GET /live-match-centre` is a read-only local aggregation route.

```text
stored Fixture rows
stored MatchDetail rows
stored MatchDetailEventCoverage rows
stored FixtureSyncRun rows
stored FixtureSyncChangeSet rows
      |
      v
live_match_centre_service
      |
      v
Live Match Centre response
```

The route does **not** call a provider, trigger sync, backfill data, write to PostgreSQL, send Telegram, or alter scheduler state.

### Match-state contract

The service maps stored statuses into four application states:

| State | Meaning |
|---|---|
| `live` | Stored status explicitly represents an in-progress match |
| `completed` | Stored status explicitly represents a completed match |
| `scheduled` | Stored status explicitly represents a scheduled/not-started match |
| `unavailable` | Unknown, postponed, cancelled, abandoned, or unsupported stored status |

Only `live` fixtures appear in the Live Match Centre live list.

### Freshness contract

Freshness is calculated from the latest successful stored sync. It describes the age of the most recent locally persisted provider snapshot.

The service can report:

```text
fresh
aging
stale
last_sync_failed
not_started
unavailable
```

v1.19.0 adds an additive `freshness_context` object to sync status and mirrors it into `data_freshness.freshness_context` in the Live Match Centre response. The object is derived only from the existing stored success timestamp, configured thresholds, and read-only schedule metadata:

```text
last_success_at
last_success_at_local
next_scheduled_run_at
snapshot_becomes_stale_at
snapshot_becomes_stale_at_local
stale_before_next_scheduled_run
diagnostic
message
```

A successful sync result and a stale snapshot are compatible states. The former describes the latest sync attempt; the latter describes the age of the last successful stored snapshot. `stale_before_next_scheduled_run` is an explanation of the configured schedule and thresholds, not a trigger to sync and not a prediction that the next sync will succeed.

Freshness is not a claim of real-time provider delivery.

### Change-capture contract

For a successful v1.18+ sync, the application compares previous local stored state with newly normalised stored state before completing audit capture.

The response reports recent factual deltas only where supported by stored coverage. It never reconstructs a historical timeline from overwritten data. No companion record for a historical sync is explicitly labelled rather than treated as zero changes.

## Dashboard architecture

The static dashboard uses:

```text
backend/app/static/dashboard.html
backend/app/static/dashboard.css
backend/app/static/dashboard.js
backend/app/static/live_match_centre.css
backend/app/static/live_match_centre.js
```

v1.18.0 keeps Match Story, fixture browsing, mobile navigation, and official-watch policy intact.

It adds:

- a Live Match Centre inside Matchday;
- explicit freshness and local-update evidence;
- a local-API-only refresh action;
- a concise What changed? view inside Provider Sync Runtime;
- conditional unavailable-status handling in the fixture browser.

v1.19.0 adds a compact Freshness Context presentation for the last successful snapshot, next scheduled refresh, and stale-after boundary. When freshness is `stale` or `last_sync_failed`, live cards are labelled **Last confirmed live from stored snapshot** and the dashboard explicitly states that it does not infer current live status from kickoff time.

The browser does not poll automatically. It does not ask a provider to refresh data.

## Match Story and official watch

`GET /fixtures/{fixture_id}/story` remains a read-only local composition route.

Score progression appears only when stored goal records reconcile exactly with the stored score. Timelines preserve available provider minutes, including valid stoppage time, without inventing a missing minute. Team statistics appear only when both teams have comparable provider-supplied values.

Official Watch remains outbound-only. It does not scrape sources, embed third-party video, proxy thumbnails, automatically discover links, or bypass region restrictions.

## Fixed-time provider sync and Telegram digest

The scheduler configuration remains unchanged:

```text
timezone: Asia/Singapore
slots: 03:45, 09:45, 12:45
```

The scheduler is opt-in and waits for the next future configured slot after startup or restart. Scheduled Telegram digests remain separately controlled and disabled by default.

The v1.19.0 release does not alter the schedule or freshness thresholds. It exposes the relationship between the configured slots and the stale-after boundary so an operator can see when a successful stored snapshot has aged beyond that boundary before the next planned refresh.

The Live Match Centre does not change the schedule, send Telegram messages, or run an automatic provider request.

## Database bootstrap boundary

The project uses SQLAlchemy metadata bootstrap. v1.18.0 uses additive companion tables rather than altering existing deployed tables. v1.19.0 adds no table, migration, or persisted-data change.

On a later approved runtime deployment, missing companion tables can be created through normal application bootstrap. Source preparation alone does not modify active runtime data, run migrations, backfill historical data, or alter live database records.

## Windows runtime reliability boundary

The Windows runtime separates bounded Docker recovery from sensitive host-service operations:

```text
startup/watchdog scripts
  +--> may start Docker Desktop and recover unhealthy Docker containers
  +--> report-only: Cloudflared service state and public health
  +--> report-only: host Ollama API, application AI health, and Ollama task state
```

`get-worldcup-runtime-status.ps1` reports Docker, local endpoints, Cloudflared/public health, Ollama, application AI, scheduled-task state, and local/public version consistency.

It does not start, stop, restart, rebuild, sync, send, reconfigure, create, delete, or display active secrets.

## Configuration and secrets

Primary safe source files:

```text
.env.example
VERSION
backend/app/config.py
```

Version-consistency tests compare:

```text
VERSION
APP_VERSION in .env.example
default app_version in backend/app/config.py
```

The repository stores placeholders only. Active `.env`, provider keys, Telegram tokens, Cloudflare credentials, database credentials, model files, and host-specific runtime files remain local.

## Testing and release verification

v1.19.0 local source verification:

```text
277 passed, 325 warnings
```

The warnings are known FastAPI/Starlette Python 3.14 deprecations related to `asyncio.iscoroutinefunction`; they are not test failures.

## Known constraints

- Provider payload quality determines available fixture and event detail.
- A stored empty event array does not prove that no event occurred.
- The Live Match Centre reports local stored snapshots, not provider real-time delivery.
- Freshness Context explains stored-snapshot age relative to the configured schedule; it does not change schedule, thresholds, or provider behavior.
- Historical sync changes before v1.18 are not reconstructed.
- Provider event identifiers and complete historical event-correction/version storage are not implemented.
- The system is self-hosted and does not implement production authentication.
- Dashboard visuals are descriptive stored-data views, not predictive analytics or qualification simulations.
