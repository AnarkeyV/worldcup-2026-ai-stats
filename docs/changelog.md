# Changelog

All notable changes to World Cup 2026 AI Stats are documented here.

The project follows semantic versioning and milestone-based releases.

---

## [1.19.1] — Fixed Schedule Sync Mode Truthfulness

### Changed

- Provider Sync Runtime now renders `fixed_daily_times` using the configured schedule slots and timezone, for example: **Fixed daily: 03:45 · 09:45 · 12:45 (Singapore time)**.
- Interval wording such as **Every 30 min** is reserved for genuine interval-mode scheduling only.
- Dashboard JavaScript cache-busting advances to `v1.19.1`.

### Verified

```text
277 automated tests passed
325 known FastAPI/Starlette Python 3.14 deprecation warnings
```

### Boundaries

- This is a dashboard truthfulness correction only. It does not alter the runtime scheduler, configured slot times, freshness thresholds, provider calls, sync history, fixture data, Telegram, Docker, Cloudflared, Ollama, or an active runtime `.env`.
- `interval_minutes` remains backward-compatible status metadata and is not treated as the active schedule when `mode` is `fixed_daily_times`.

---

## [1.19.0] — Freshness Context & Matchday Trust Signals

### Added

- Additive, read-only `freshness_context` in `GET /fixtures/sync/status`.
- Mirrored context in `GET /live-match-centre` at `data_freshness.freshness_context`.
- Snapshot timing metadata for the latest successful refresh, next configured scheduled refresh, and stale-after boundary, including derived configured-timezone values when valid.
- Factual diagnostic states that distinguish:
  - a latest refresh failure;
  - a successful snapshot that is already stale;
  - a successful snapshot that will become stale before the next scheduled refresh;
  - a snapshot within its current freshness window.
- Dashboard Freshness Context presentation and conservative stale Live Match Centre labels: **Last confirmed live from stored snapshot**.

### Changed

- Freshness messaging now explains that successful sync outcome and stored-snapshot age are separate facts.
- Stale or failed freshness no longer lets Live Match Centre wording imply that stored live state is definitely current.
- Safe version declarations and dashboard JavaScript cache-busters align to `1.19.0` / `v1.19.0`.

### Verified

```text
277 automated tests passed
325 known FastAPI/Starlette Python 3.14 deprecation warnings
```

### Boundaries

- The configured provider schedule remains unchanged: `03:45`, `09:45`, and `12:45` in `Asia/Singapore`.
- Freshness Context is read-only explanatory metadata. It does not trigger provider requests, alter a scheduled slot, write fixture or sync data, send Telegram, or change Docker, Cloudflared, Ollama, or active runtime `.env` values.
- A successful refresh may become stale before the next configured slot. This describes the stored snapshot age; it does not mean that the refresh failed.
- Time is never used to infer that a fixture is live or completed. The v1.18.1 conservative `unknown` fixture-display contract remains intact.

---

## [1.18.1] — Scheduled from Stored Kickoff

### Added

- A conservative kickoff-aware display-state contract for fixtures whose stored provider status is `unknown`.
- `scheduled_sources` in `GET /live-match-centre`, separating `provider_status` from `stored_kickoff` scheduled counts.
- Dashboard context that labels derived fixtures as **Scheduled from stored kickoff** and states that provider match status is unavailable.

### Changed

- A stored `unknown` fixture is displayed as scheduled only when it has a valid future UTC kickoff and both stored scores are absent.
- The existing Matchday next-up selection, scheduled fixture tab, and dashboard counts now use the same conservative stored-kickoff rule.
- Safe version declarations and core dashboard asset cache-bust values align to `1.18.1` / `v1.18.1`.

### Verified

```text
274 automated tests passed
318 known FastAPI/Starlette Python 3.14 deprecation warnings
```

### Boundaries

- The stored provider status is not changed or rewritten by the display derivation.
- Explicit provider states remain authoritative.
- Time is never used to infer a live match.
- An unknown fixture at or after kickoff, without a valid timezone-aware kickoff, with stored scores, or with an explicit postponed/cancelled/abandoned status remains unavailable.
- No provider request, sync, database write, Telegram send, scheduler update, Docker change, or active runtime `.env` change is introduced by this release.

---

## [1.18.0] — Live Match Centre & Data Freshness

### Added

- Read-only `GET /live-match-centre` endpoint built only from locally stored fixtures, match detail, event-coverage records, persisted sync runs, and v1.18+ change sets.
- Shared stored-status classification with four explicit application states: `live`, `completed`, `scheduled`, and `unavailable`.
- Additive `match_detail_event_coverage` companion table for provider-backed evidence about goals, cards, and substitutions.
- Additive `fixture_sync_change_sets` companion table for factual deltas from successful v1.18+ sync runs.
- Change detection for stored score changes, status changes, completion transitions, newly stored goals, cards, substitutions, and provider-event record revisions.
- Matchday Live Match Centre dashboard panel and a local-API-only refresh action.
- Provider Sync Runtime **What changed?** view using persisted change-set facts.
- Conditional dashboard handling for unavailable match statuses rather than silently classifying them as upcoming.

### Changed

- The dashboard now distinguishes explicit stored live status from scheduled, completed, and unavailable states.
- Sync freshness remains a local stored-snapshot age; it is presented as data freshness rather than a real-time delivery guarantee.
- Event availability is explicit when detail is absent, an event category was not supplied, or historical coverage is unknown.
- Dashboard static asset cache-bust values align to `v1.18.0`.
- Safe version declarations in `VERSION`, `.env.example`, and `backend/app/config.py` align to `1.18.0`.

### Verified

```text
267 automated tests passed
316 known FastAPI/Starlette Python 3.14 deprecation warnings
```

### Boundaries

- The Live Match Centre route reads local records only. It does not call a provider, trigger sync, backfill data, write to PostgreSQL, send Telegram, or alter scheduler state.
- The dashboard refresh action re-reads the local API only; it does not poll automatically or initiate provider work.
- A fixture is shown as live only when the stored status explicitly maps to `live`.
- Unknown, postponed, cancelled, abandoned, and unsupported statuses remain `unavailable`.
- No event, timeline, player detail, or match statistic is fabricated.
- Historical sync runs without a v1.18 change set are labelled `not_recorded_before_v1_18`; they are not presented as an empty change list.
- The additive ORM tables are created only during a later approved runtime deployment. No release-preparation step modifies active runtime data, `.env`, scheduler configuration, Telegram state, Cloudflared, Ollama, Docker volumes, or tunnel credentials.

---

## [1.17.1] — Runtime Reliability Safeguards

### Added

- Read-only `scripts/windows/get-worldcup-runtime-status.ps1` for Windows operator checks.
- One status view for Docker engine and Compose state, backend and dashboard health, Cloudflared service state, public health, host Ollama API, application AI health, and the user-level Ollama launcher task.
- Explicit local/public backend version-consistency reporting.
- `docs/windows-runtime-recovery.md`, with secret-safe diagnostic and recovery boundaries.
- Focused safeguards that prevent the status script from rebuilding/restarting Docker, syncing providers, sending Telegram, changing Cloudflared, changing Ollama, changing tasks, or printing active configuration.

### Changed

- Existing Windows startup and watchdog scripts retain Docker startup and unhealthy-container recovery.
- Cloudflared is report-only in those scripts; no project script starts or restarts the service.
- Ollama is report-only in those scripts; no project script launches, kills, reconfigures, or downloads a model.
- Safe version declarations align to `1.17.1`.

### Verified

```text
241 automated tests passed
296 known FastAPI/Starlette Python 3.14 deprecation warnings
```

---

## [1.17.0] — Provider-Backed Match Story and Official Watch

### Added

- Read-only `GET /fixtures/{fixture_id}/story` derived only from local `Fixture`, `MatchDetail`, and manually verified `OfficialMatchVideo` records.
- Conservative score-progression contract that requires stored goal events to reconcile exactly with the stored fixture score.
- Stored match-event sequence for goals, cards, substitutions, and valid stoppage-time values.
- Provider provenance in the story response: provider name, provider match ID, and stored-detail refresh timestamp.
- Paired statistic normalisation for possession, shots, shots on target, expected goals, accurate passes, corners, and fouls.
- Official Watch policy for manually verified, outbound-only FIFA and meWATCH destinations.

### Boundaries

- The story route reads local database records only. It does not call a provider, write data, sync, backfill, send Telegram, or alter scheduler state.
- No scraping, automatic discovery, download, rehosting, third-party embed, fan-upload linking, or region-restriction bypass is used.

---

## [1.16.0] — Fixed-Time Scheduled Sync and Telegram Digest

### Added

- Fixed daily provider-sync schedule configuration with `Asia/Singapore` and `03:45`, `09:45`, `12:45` defaults.
- Strict next-future-slot calculation so startup, restart, or a late boot does not cause an immediate catch-up sync.
- Optional scheduled Telegram digest policy, disabled by default.
- One Telegram roundup for fixtures that transition to completed during a single scheduled sync.
- Dashboard-link delivery in scheduled Telegram digests.

### Boundaries

- Scheduler and scheduled Telegram digest remain disabled by default.
- Release preparation does not activate provider requests, database writes, Docker changes, Cloudflare changes, or Telegram messages.

---

## [1.15.0] — Visual Matchday UX and Charts

### Added

- Visual Matchday home area with stored-fixture cards for live, latest completed, and next scheduled context.
- Compact Data health badge using the existing read-only stored-data result.
- CSS-based comparative bars for leaderboards and Group Race.
- Mobile-only bottom navigation for Matchday, Matches, Groups, Players, and Data.

---

## [1.14.0] — Match Data Quality Dashboard

### Added

- Read-only `GET /fixtures/data-quality` endpoint over locally stored `Fixture` and `MatchDetail` records.
- Scope-aware completed-fixture coverage, event counters, filters, and bounded missing-detail follow-up.
- Dashboard Match Data Coverage panel with manual refresh and fixture links.

---

## [1.13.0] — Provider Event Integrity and Stored Detail Coverage

### Added

- Shared canonical handling for goals, cards, and substitutions.
- Read-only stored-event coverage in fixture detail.
- Dashboard states for unavailable detail, recorded events, and empty stored event arrays.

---

## [1.12.0] — Safe Matchday Sync, Audit History, and Data Freshness

### Added

- Persisted fixture sync-run history and read-only latest sync status.
- Optional provider-only scheduler with no immediate startup sync and no overlapping runs.
- Disabled-by-default completed-match Telegram alert policy.
- Dashboard freshness states and stored-detail refresh indicators.

---

## Earlier milestones

| Version | Summary |
|---|---|
| v1.11.0 | Mobile rich match dashboard, provider leaders, latest result, and Group Race |
| v1.10.0 | Match detail dashboard and README polish |
| v1.9.0 | Live local AI, Telegram mobile links, Cloudflare, and Windows runtime resilience |
| v1.8.0 | Structured AI Insights |
| v1.7.0 | Provider sync observability and runtime demo |
| v1.6.0 | Real match-data sync improvement |
| v1.5.0 | Portfolio release polish |
| v1.4.x | Monitoring, Grafana polish, Telegram hardening, and documentation cleanup |
| v1.1.0 | Group standings engine |
| v0.1.0–v0.8.0 | Project foundation, fixtures, provider abstraction, completion detection, notifications, dashboard, filters, and local Llama summary agent |
