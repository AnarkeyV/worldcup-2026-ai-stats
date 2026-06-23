# Changelog

All notable changes to World Cup 2026 AI Stats are documented here.

The project follows semantic versioning and milestone-based releases.

---

## [1.14.0] — Match Data Quality Dashboard

### Added

- Read-only `GET /fixtures/data-quality` endpoint over locally stored `Fixture` and `MatchDetail` records.
- Scope-aware coverage for completed fixtures with stored detail, without stored detail, coverage percentage, and latest local stored-detail refresh.
- Goal, card, and substitution coverage counters that distinguish:
  - fixtures with recorded stored events
  - fixtures with empty stored event arrays
  - fixtures without stored detail
  - total stored events
- Optional `group_name` and `team` filters plus bounded missing-detail fixture follow-up.
- Dashboard **Match Data Coverage** panel with manual refresh and direct follow-up links for completed fixtures without stored detail.
- Focused acceptance tests for unavailable, partial, and group-filtered coverage states.

### Changed

- Dashboard Quick Links now include Match Data Coverage.
- Dashboard cache-busting assets and release metadata are updated for v1.14.0.
- README, architecture, and roadmap now describe the local-only aggregate quality contract.

### Verified

```text
205 automated tests passed
```

### Boundaries

- `GET /fixtures/data-quality` performs local database reads only.
- No provider sync, backfill, scheduler, Telegram, Docker, Cloudflare, Windows runtime, or database migration behavior was added.
- The aggregate does not infer missing events, request provider data, validate provider truth, or claim that a stored payload is complete.

---

## [1.13.0] — Provider Event Integrity and Stored Detail Coverage

### Added

- Shared `provider_event_integrity` service for canonical goals, cards, and substitutions.
- Read-only `stored_event_coverage` in `GET /fixtures/{fixture_id}/detail`.
- Explicit stored-detail states for:
  - unavailable provider detail
  - recorded event arrays
  - stored detail with no event records in the last payload
- Compact **Stored provider detail** coverage block in the match-detail Overview tab.
- Focused acceptance tests for:
  - canonical goal, card, and substitution events
  - exact duplicate handling
  - later provider-detail replacement behaviour
  - unavailable and empty stored-event coverage states
  - dashboard coverage logic and styling

### Changed

- Zafronix match-detail normalization now canonicalizes goals, cards, and substitutions before they enter fixture sync.
- Match-detail persistence canonicalizes event arrays before storing them.
- Provider player leaders and latest completed-result summaries canonicalize stored event arrays at read time, protecting reader views from duplicate or malformed legacy arrays.
- Event ordering is stable and chronological for timed events; valid untimed events are retained after timed events instead of being discarded.
- Updated README, architecture, roadmap, and version metadata for the v1.13.0 release.

### Verified

```text
202 automated tests passed
```

### Boundaries

- No external provider request is made by `GET /fixtures/{fixture_id}/detail`.
- No Docker, scheduler, Telegram, Cloudflare, or live runtime operation is required for the tests.
- No database migration, provider event ID, historical event-correction/version store, automatic backfill, score reconciliation, or assist inference was added.
- An empty stored event array does not prove that no such event occurred in the match.

---

## [1.12.0] — Safe Matchday Sync, Audit History, and Data Freshness

### Added

- Persisted fixture sync-run history for successful and failed attempts.
- Read-only latest sync status and recent sync-history endpoints backed by stored audit records.
- Optional provider-only scheduler, disabled by default.
- No immediate provider call on application start and no overlapping scheduled runs.
- Completed-match Telegram alerts disabled by default and controlled separately from Telegram test messages.
- Dashboard freshness states for no sync, fresh, aging, stale, unavailable, and last-sync-failed data.
- Stored match-detail refresh time based only on the locally stored provider payload.
- Redacted, bounded persisted sync errors to avoid exposing configured secrets.

### Changed

- Sync runtime reporting now distinguishes current status from freshness of the last successful stored data.
- Dashboard copy makes the manual-only default, disabled alert policy, and stored-data semantics visible.

### Verified

```text
196 automated tests passed
```

### Notes

- No automatic rich-detail backfill was added.
- No automatic scheduler-triggered Telegram alerting was enabled.
- Event deduplication and historical event-correction/version storage were deferred to a future milestone.

---

## [1.11.0] — Mobile Rich Match Dashboard, Provider Leaders, and Group Race

### Added

- Provider-backed rich match-detail persistence for fixture events, cards, substitutions, formations, lineups, statistics, referee data, and weather context.
- `GET /fixtures/{fixture_id}/detail` for a fixture plus its stored rich detail.
- Status-first fixture browsing for **Completed**, **Live**, and **Upcoming** matches, with group-level filtering.
- Responsive rich match-detail dashboard with overview, timeline, statistics, and lineups tabs.
- Sticky Quick Links navigation with active-section highlighting.
- `GET /players/leaders` for provider-derived top scorers, yellow-card leaders, and red-card leaders.
- `GET /ai/latest-completed/summary` for the latest completed provider-backed result with incident and scorer context.
- Provider scorer-name normalization so embedded event metadata such as time or penalty markers does not appear in leaderboard names.
- Group Race data in `GET /ai/insights`, returning the top two teams in each populated group.
- Group Race board in the Structured AI Insights dashboard panel.
- Focused test coverage for provider leaderboards, latest-result summaries, Group Race data, responsive dashboard behavior, and release verification.

### Changed

- Replaced the dashboard player-statistics placeholder with live provider-derived leaderboards.
- Reframed Structured AI Insights around qualification position and Group Race rather than generic strongest-attacks emphasis.
- Kept assist data explicitly unavailable when the provider payload does not supply assist events.

### Verified

```text
184 automated tests passed
```

### Notes

- The Group Race and provider leaderboards are deterministic views over stored provider data.
- No provider sync or rich-detail backfill is required to render existing stored data.
- Console encoding may display accented names incorrectly on some Windows terminals; browser output is the visual source of truth.

---

## [1.10.0] — Match Detail Dashboard and README Polish

### Added

- Clickable fixture cards and a match-detail dashboard experience.
- Provider-backed match detail views for scoreline, venue, group, stage, and fixture context.
- Dashboard presentation and README portfolio polish.

### Verified

```text
161 automated tests passed
```

---

## [1.9.0] — Live Runtime Enablement

### Added

- Zafronix World Cup provider workflow for the live runtime.
- Windows Docker runtime operation with Cloudflare public dashboard access.
- Local Ollama health checks and local summary support.
- Telegram readiness, testing, and mobile dashboard links.
- Runtime resilience and deployment validation improvements.

---

## [1.8.0] — AI Insights Upgrade

### Added

- `GET /ai/insights` for deterministic, fallback-safe structured AI insights.
- Group and team filtering for AI insights.
- Structured AI Insights dashboard panel.
- Fixture availability, completed-results, standings, and provider-sync insight categories.

### Verified

```text
149 automated tests passed
```

---

## [1.7.0] — Provider Sync Observability and Runtime Demo

### Added

- `GET /fixtures/sync/status`.
- Fixture sync runtime status tracking.
- Prometheus fixture-sync metrics.
- Provider Sync Runtime dashboard panel.
- Grafana provider-sync observability panels.
- Dedicated runtime demo guide.

### Verified

```text
138 automated tests passed
```

---

## [1.6.0] — Real Match Data Sync Improvement

### Added

- Provider error wrapping and invalid-payload protection.
- Fixture validation and incomplete-row skipping.
- Team-code fallback logic.
- Provider sync route coverage for success and failure cases.

### Changed

- Normalized provider statuses into application-friendly values.
- Hardened completion detection for `FT`, `AET`, and `PEN`.
- Returned `502` for provider-side sync failures.

### Verified

```text
123 automated tests passed
```

---

## [1.5.0] — Portfolio Release Polish

### Added

- Portfolio release summary.
- Demo walkthrough.
- Recruiter/interviewer-focused documentation.

### Verified

```text
114 automated tests passed
```

---

## Earlier Releases

| Version | Theme |
|---|---|
| v1.4.3 | Documentation and demo-evidence cleanup |
| v1.4.2 | Telegram API live-integration hardening |
| v1.4.1 | Grafana dashboard polish |
| v1.4.0 | Monitoring and observability foundation |
| v1.3.0 | Player-statistics foundation |
| v1.2.0 | Team insights and group analytics |
| v1.1.2 | Version and container workflow cleanup |
| v1.1.1 | README and documentation refresh |
| v1.1.0 | Group standings engine |
| v1.0.0 | AI summary quality and dashboard polish |
| v0.8.0 | Local Llama summary agent |
| v0.7.0 | API fixture filters |
| v0.6.0 | Interactive dashboard |
| v0.5.0 | Telegram notifications |
| v0.4.0 | Match completion detection |
| v0.3.0 | Provider abstraction |
| v0.2.0 | Fixture and API foundation |
| v0.1.1 | Documentation polish |
| v0.1.0 | Project foundation |
