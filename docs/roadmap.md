# Roadmap

World Cup 2026 AI Stats is developed through small, test-backed milestones. Each milestone should improve the dashboard, data quality, runtime resilience, or portfolio value without weakening the self-hosted workflow.

---

## Current Status

```text
Current release: v1.16.0 — Fixed-Time Scheduled Sync and Telegram Digest
Release verification: 217 tests passed
Previous v1.15.0 verification: 209 tests passed
Primary runtime: Windows laptop + Docker Compose
Development machine: MacBook Pro + VS Code + Python venv
Public dashboard: https://wc2026.khairulrizal.qzz.io/dashboard
```

Current live capabilities:

- visual Matchday home with live/latest/next stored-fixture cards and a local Data health badge
- provider-backed fixtures and stored rich match details
- read-only Match Data Coverage with visual coverage progress and missing-detail follow-up
- comparative player and Group Race bars derived from existing stored responses
- status-first fixture browser and responsive match detail
- local Ollama health and summary workflow with deterministic fallback
- provider-backed goals and card leaderboards
- latest completed-match summary
- top-two Group Race board across populated groups
- persisted fixture sync audit history and safe freshness states
- disabled-by-default fixed-time provider scheduling and scheduled Telegram digest policy
- Telegram status/testing and mobile dashboard links
- Prometheus, Grafana, sync observability, and Cloudflare access

---

## v1.16.0 Release Notes

### v1.16.0 — Fixed-Time Scheduled Sync and Telegram Digest

**Goal:** Refresh the stored provider snapshot around the current Singapore match windows and send one useful Telegram roundup after newly completed matches, without enabling automation or delivery by default.

Delivered scope:

- fixed daily schedule configuration, defaulting to `03:45`, `09:45`, and `12:45` in `Asia/Singapore`
- strict next-future-slot behavior after startup or restart, with no immediate catch-up sync
- one provider fixture sync per scheduled slot
- one Telegram digest for all newly completed fixtures from that run when the digest policy is enabled
- no Telegram delivery when the completion set is empty
- public dashboard link in the digest
- read-only schedule metadata in sync status: mode, timezone, slots, and next run
- explicit environment placeholders and release checks for the new settings
- full regression-suite verification

Current boundaries retained:

- the scheduler and scheduled digest are disabled by default
- no `.env` activation, Windows runtime change, provider sync, or Telegram message occurs during release preparation
- no automatic rich-detail backfill, database migration, forecast, qualification probability, or factual match-report export
- schedule times are configurable and should be revisited for later tournament-stage timing changes

---

## v1.15.0 Release Notes

### v1.15.0 — Visual Matchday UX and Charts

**Goal:** Make the dashboard quicker to scan on desktop and mobile with visual matchday context, comparison bars, and clearer data-health presentation, without changing the stored-data or runtime contract.

Delivered scope:

- visual Matchday cards for live, latest completed, and next scheduled fixtures
- compact Data health badge using the existing read-only Match Data Coverage response
- CSS-based visual bars for player leader metrics and Group Race points
- visual Match Data Coverage donut/progress treatment
- mobile-only bottom navigation for the key fan-facing sections
- focused dashboard acceptance checks and full regression-suite verification

Current boundaries retained:

- no new API route or chart library
- no provider request, sync, automatic rich-detail backfill, scheduler, or Telegram change
- no database migration, Docker, Cloudflare, or Windows runtime change
- no forecasts, qualification probabilities, or provider-completeness claim from visual indicators

---

## v1.14.0 Release Notes

### v1.14.0 — Match Data Quality Dashboard

**Goal:** Make the completeness of locally stored completed-match detail visible across the tournament without performing a provider lookup, backfill, or other side effect.

Delivered scope:

- read-only `GET /fixtures/data-quality` over existing fixture and match-detail records
- coverage state, counts, percentage, and latest locally stored-detail refresh
- goals, cards, and substitutions counters for recorded event arrays, empty stored arrays, and missing stored detail
- optional group/team filtering and a bounded missing-detail fixture list
- a compact Match Data Coverage dashboard panel with a manual refresh and fixture follow-up links
- focused acceptance coverage for unavailable, partial, and filtered scopes
- full regression-suite verification

Current boundaries retained:

- no provider request, sync, or automatic rich-detail backfill
- no scheduler, Telegram, Docker, Cloudflare, or Windows runtime changes
- no database migration
- no inferred events, assists, player data, or score reconciliation
- no provider-completeness or factual-accuracy claim from local coverage counts

---

## v1.13.0 Release Notes

### v1.13.0 — Provider Event Integrity and Stored Detail Coverage

**Goal:** Make stored provider event data more trustworthy and make event-data coverage transparent in the match-detail dashboard, without triggering provider writes or inventing football facts.

Delivered scope:

- canonical goals, cards, and substitutions through a shared service
- safe participant and side validation for supported event shapes
- exact normalized duplicate removal
- stable ordering of timed events with valid untimed events retained after them
- canonical handling at provider normalization, match-detail persistence, and reader paths
- reader protection for provider leaderboards and latest-result summaries
- read-only `stored_event_coverage` in the fixture-detail endpoint
- dashboard coverage block that distinguishes:
  - no stored provider detail
  - stored event records
  - stored detail with no event records in the last payload
- focused test coverage and full release-suite verification

Current boundaries retained:

- no provider event IDs
- no historical event-correction/version storage
- no database migration
- no automatic provider sync or rich-detail backfill
- no score reconciliation
- no inferred assists or player data
- no factual match-report export
- no runtime, Docker, scheduler, Telegram, or Cloudflare changes

---

## Completed Milestones

| Version | Status | Delivered |
|---|---|---|
| v0.1.0 | Completed | FastAPI foundation, Dockerfile, health route, pytest setup |
| v0.2.0 | Completed | Fixture model, sample sync, database persistence |
| v0.3.0 | Completed | Provider abstraction and provider sync |
| v0.4.0 | Completed | Match-completion detection |
| v0.5.0 | Completed | Telegram notification workflow |
| v0.6.0 | Completed | Interactive dashboard |
| v0.7.0 | Completed | Fixture filters and team search |
| v0.8.0 | Completed | Local Llama/Ollama summary agent |
| v1.1.0 | Completed | Group standings engine |
| v1.2.0 | Completed | Team insights and group analytics |
| v1.3.0 | Completed | Player-statistics foundation |
| v1.4.0 | Completed | Prometheus and Grafana foundation |
| v1.4.1 | Completed | Grafana dashboard polish |
| v1.4.2 | Completed | Telegram API hardening |
| v1.4.3 | Completed | Documentation and demo-evidence cleanup |
| v1.5.0 | Completed | Portfolio release polish |
| v1.6.0 | Completed | Real match-data sync reliability |
| v1.7.0 | Completed | Provider sync observability |
| v1.8.0 | Completed | Structured AI Insights |
| v1.9.0 | Completed | Live local AI, Telegram mobile links, Cloudflare, and Windows runtime resilience |
| v1.10.0 | Completed | Match-detail dashboard and README polish |
| v1.11.0 | Completed | Rich match details, provider leaders, latest result, sticky navigation, Group Race |
| v1.12.0 | Completed | Safe matchday sync audit history, opt-in scheduler/alerts, and factual freshness indicators |
| v1.13.0 | Completed | Provider event integrity and stored detail coverage |
| v1.14.0 | Completed | Read-only match data quality dashboard and missing-detail follow-up |
| v1.15.0 | Completed | Visual Matchday home, descriptive charts, data-health badge, and mobile navigation |
| v1.16.0 | Completed | Fixed-time scheduled provider sync, next-run visibility, and opt-in Telegram matchday digest |

---

## v1.12.0 Release Notes

### v1.12.0 — Safe Matchday Sync, Audit History, and Data Freshness

**Goal:** Make matchday operation safer and easier to verify without inventing football data or enabling side effects by default.

Delivered scope:

- persisted fixture sync-run history for successful and failed attempts
- read-only latest status and recent sync-history endpoints backed by stored audit records
- optional provider-only scheduler that is disabled by default
- no immediate provider call on application start and no overlapping scheduled runs
- completed-match Telegram alerts disabled by default and controlled separately from Telegram test messages
- visible dashboard states for no sync, fresh, aging, stale, unavailable, and last-sync-failed data
- clear stored match-detail refresh time based only on the locally stored provider payload
- redacted, bounded persisted sync errors to avoid exposing configured secrets

Release boundaries retained:

- no automatic rich-detail backfill
- no automatic Telegram alerts from the scheduler
- no meaningful-event alerting
- no inferred assists, player analytics, or data not supplied reliably by a provider
- no factual match-report export

Validation completed before release preparation:

```text
Focused test suite: 100 passed
Full regression suite: 196 passed
git diff --check: passed with no whitespace errors
```

---

## Longer-Term Ideas

- provider-specific event IDs and historical correction/version handling
- factual stored-data match report export
- authentication and per-user preferences
- team comparison views
- group qualification scenario simulation
- historical match report pages
- lightweight background job queue
- cache layer for provider data
- CI/CD deployment automation
- low-cost VPS or cloud deployment
- optional Kubernetes demonstration deployment
- database backup and restore workflow
- role-based dashboard access

---

## Roadmap Principles

Every milestone should follow this workflow:

```text
Clear scope
→ focused tests
→ full suite passes
→ clean Git diff
→ feature branch commit and push
→ PR review
→ merge
→ version tag and release
→ Windows runtime verification
→ local and remote branch cleanup
```

The project should remain:

- local-first by default
- safe with secrets
- honest about provider limitations
- usable on mobile
- easy to demonstrate
- explainable during interviews
