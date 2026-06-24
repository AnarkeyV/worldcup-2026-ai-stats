# Changelog

All notable changes to World Cup 2026 AI Stats are documented here.

The project follows semantic versioning and milestone-based releases.

---

## [1.17.0] — Provider-Backed Match Story and Official Watch

### Added

- Read-only `GET /fixtures/{fixture_id}/story` route derived only from local `Fixture`, `MatchDetail`, and manually verified `OfficialMatchVideo` records.
- Conservative score-progression contract that requires stored goal events to reconcile exactly with the stored fixture score.
- Stored match-event sequence for goals, cards, substitutions, and valid stoppage-time values.
- Provider provenance in the story response: provider name, provider match ID, and stored-detail refresh timestamp.
- Paired statistic normalisation for possession, shots, shots on target, expected goals, accurate passes, corners, and fouls.
- `OfficialMatchVideo` local registry model for future manually verified, match-specific outbound links.
- Strict initial official-watch policy for FIFA web, exact FIFA YouTube video URLs, and meWATCH destinations.
- Official FIFA and meWATCH coverage-hub fallbacks when no verified match-specific link is stored.
- Match-detail Story tab and mobile-first unavailable, partial, delayed-video, and region-dependent states.
- Focused coverage for story construction, route behaviour, official-link policy, and dashboard rendering.

### Changed

- The match-detail panel now leads with **Story** while retaining Timeline, Stats, and Lineups.
- Statistics no longer convert missing or invalid provider values to zero for visual comparisons.
- Dashboard static asset cache-busters now use `v1.17.0`.
- Version declarations in `VERSION`, `.env.example`, and `backend/app/config.py` are aligned to `1.17.0`.

### Verified

```text
234 automated tests passed
296 known FastAPI/Starlette Python 3.14 deprecation warnings
```

### Boundaries

- The story route reads local database records only. It does not call a provider, write data, sync, backfill, send Telegram, or alter scheduler state.
- No scraping, search harvesting, download, rehosting, thumbnail proxying, arbitrary channel linking, fan-upload linking, or region-restriction bypass was added.
- No third-party video embed is used; verified links open externally.
- No verified match-specific videos are hard-coded into the release. Until a later controlled curator workflow adds validated records, the dashboard shows a clear not-available-yet state with official coverage-hub fallbacks.
- The existing ORM bootstrap can create the empty `official_match_videos` table on an approved later runtime deployment; no backfill or active runtime change happens during source preparation.

---

## [1.16.0] — Fixed-Time Scheduled Sync and Telegram Digest

### Added

- Fixed daily provider-sync schedule configuration with `Asia/Singapore` and `03:45,09:45,12:45` defaults.
- Fixed-time schedule parsing that normalises, sorts, and deduplicates configured slots.
- Strict next-future-slot calculation so startup, restart, or a late boot does not cause an immediate catch-up provider sync.
- Safe fixed-time scheduler metadata in `GET /fixtures/sync/status`, including mode, timezone, configured slots, and next run.
- Optional scheduled Telegram digest policy, disabled by default.
- One Telegram roundup for every fixture that transitions to completed during a single scheduled sync.
- Silent scheduled outcomes when no newly completed fixtures exist.
- Dashboard-link delivery in scheduled Telegram digests.

### Changed

- The configured runtime startup path uses fixed daily times rather than an interval cadence.
- The legacy interval setting remains available for compatibility and status output but does not drive the configured runtime scheduler.

### Verified

```text
218 automated tests passed
```

### Boundaries

- The scheduler and scheduled Telegram digest remain disabled by default.
- No `.env` value, provider request, database write, Docker change, Cloudflare change, or Telegram message is activated by release preparation alone.

---

## [1.15.0] — Visual Matchday UX and Charts

### Added

- Visual **Matchday** home area with stored-fixture cards for live, latest completed, and next scheduled context.
- Compact **Data health** badge using the existing read-only `GET /fixtures/data-quality` response.
- CSS-based comparative bars for leaderboards and Group Race.
- Visual coverage-progress treatment in Match Data Coverage.
- Mobile-only bottom navigation for Matchday, Matches, Groups, Players, and Data.

### Verified

```text
209 automated tests passed
```

### Boundaries

- Frontend-focused release using existing stored API data.
- No charting dependency, provider request, sync, backfill, scheduler, Telegram behaviour, database migration, Docker, Cloudflare, or Windows-runtime change.

---

## [1.14.0] — Match Data Quality Dashboard

### Added

- Read-only `GET /fixtures/data-quality` endpoint over locally stored `Fixture` and `MatchDetail` records.
- Scope-aware completed-fixture coverage, event counters, filters, and bounded missing-detail follow-up.
- Dashboard Match Data Coverage panel with manual refresh and fixture links.

### Verified

```text
205 automated tests passed
```

---

## [1.13.0] — Provider Event Integrity and Stored Detail Coverage

### Added

- Shared canonical handling for goals, cards, and substitutions.
- Read-only stored-event coverage in fixture detail.
- Dashboard states for unavailable detail, recorded events, and empty stored event arrays.

### Verified

```text
202 automated tests passed
```

---

## [1.12.0] — Safe Matchday Sync, Audit History, and Data Freshness

### Added

- Persisted fixture sync-run history and read-only latest sync status.
- Optional provider-only scheduler with no immediate startup sync and no overlapping runs.
- Disabled-by-default completed-match Telegram alert policy.
- Dashboard freshness states and stored-detail refresh indicators.

### Verified

```text
196 automated tests passed
```

---

## Earlier Milestones

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
