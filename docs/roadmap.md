# Roadmap

World Cup 2026 AI Stats is developed through small, test-backed milestones. Each milestone should improve the dashboard, data quality, runtime resilience, or portfolio value without weakening the self-hosted workflow.

---

## Current Status

```text
Current release: v1.12.0 — Safe Matchday Sync, Audit History, and Data Freshness
Current development milestone: v1.13.0 — Provider Event Integrity and Stored Detail Coverage
Current development verification: 202 tests passed
Released v1.12.0 verification: 196 tests passed
Primary runtime: Windows laptop + Docker Compose
Development machine: MacBook Pro + VS Code + Python venv
Public dashboard: https://wc2026.khairulrizal.qzz.io/dashboard
```

Current live capabilities:

- provider-backed fixtures and stored rich match details
- status-first fixture browser and responsive match detail
- local Ollama health and summary workflow with deterministic fallback
- provider-backed goals and card leaderboards
- latest completed-match summary
- top-two Group Race board across populated groups
- persisted fixture sync audit history and safe freshness states
- disabled-by-default provider-only scheduling and completed-match Telegram alert policy
- Telegram status/testing and mobile dashboard links
- Prometheus, Grafana, sync observability, and Cloudflare access

---

## Current Development Milestone

### v1.13.0 — Provider Event Integrity and Stored Detail Coverage

**Goal:** Make stored provider event data more trustworthy and make event-data coverage transparent in the match-detail dashboard, without triggering provider writes or inventing football facts.

Delivered development scope:

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
- focused test coverage and full development-suite verification

Current boundaries retained:

- no provider event IDs
- no historical event-correction/version storage
- no database migration
- no automatic provider sync or rich-detail backfill
- no score reconciliation
- no inferred assists or player data
- no factual match-report export
- no runtime, Docker, scheduler, Telegram, or Cloudflare changes

Release preparation remains separate. The application version stays at v1.12.0 until that step.

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
| v1.13.0 | In development | Provider event integrity and stored detail coverage |

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
