# Changelog

All notable changes to World Cup 2026 AI Stats are documented here.

The project follows semantic versioning and milestone-based releases.

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
- Updated application version metadata to `1.11.0`.
- Refreshed README, architecture, roadmap, demo walkthrough, portfolio release summary, and release notes.

### Verified

```text
184 automated tests passed
```

### Release Runtime Snapshot

```text
72 provider fixtures available
40 completed fixtures
40 of 40 completed fixtures with stored match details
12 populated Group Race boards
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
