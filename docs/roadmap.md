# Roadmap

World Cup 2026 AI Stats is developed through small, test-backed milestones. Each milestone should improve the dashboard, data quality, runtime resilience, or portfolio value without weakening the self-hosted workflow.

---

## Current Status

```text
Current release: v1.11.0 — Mobile Rich Match Dashboard, Provider Leaders, and Group Race
Release verification: 184 tests passed
Primary runtime: Windows laptop + Docker Compose
Development machine: MacBook Pro + VS Code + Python venv
Public dashboard: https://wc2026.khairulrizal.qzz.io/dashboard
Active milestone: v1.12.0 — Safe Matchday Sync, Audit History, and Data Freshness
```

Current live capabilities:

- provider-backed fixtures and rich match details
- status-first fixture browser and responsive match detail
- local Ollama health and summary workflow with deterministic fallback
- provider-backed goals and card leaderboards
- latest completed-match summary
- top-two Group Race board across populated groups
- Telegram status/testing and mobile dashboard links
- Prometheus, Grafana, sync observability, and Cloudflare access

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

---

## Active Milestone

### v1.12.0 — Safe Matchday Sync, Audit History, and Data Freshness

**Goal:** Make matchday operation safer and easier to verify without inventing football data or enabling side effects by default.

Committed scope:

- persisted fixture sync-run history for successful and failed attempts
- a read-only latest status endpoint backed by persisted history
- a read-only recent sync-history endpoint
- optional provider-only scheduler that is disabled by default
- no immediate provider call on application start and no overlapping scheduled runs
- completed-match Telegram alerts disabled by default and controlled separately from Telegram test messages
- visible dashboard states for no sync, fresh, aging, stale, unavailable, and last-sync-failed data
- clear stored match-detail refresh time based only on the local stored provider payload
- redacted, bounded persisted sync errors to avoid exposing configured secrets

Non-goals for this release:

- automatic rich-detail backfill
- automatic Telegram alerts from the scheduler
- meaningful-event alerting
- event deduplication or historical event-correction/version storage
- inferred assists, player analytics, or any data not supplied reliably by a provider
- factual match-report export

### Acceptance Criteria

- Fixture sync results survive backend restart because run history is stored in the database.
- `/fixtures/sync/status` reflects the latest persisted run and preserves the most recent successful timestamp.
- `/fixtures/sync/history` returns recent safe audit records without secrets.
- Scheduled provider sync is opt-in, waits a full configured interval before its first run, and cannot overlap another scheduled run.
- Scheduled sync never sends Telegram alerts.
- Manual sample/provider sync does not send completed-match Telegram alerts until `TELEGRAM_COMPLETED_MATCH_ALERTS_ENABLED=true` is explicitly configured.
- The dashboard describes stored data freshness and stored match-detail refresh honestly.
- Focused tests pass first, followed by the full suite and `git diff --check`.
- `APP_VERSION` remains at `1.11.0` until release preparation.

---

## Longer-Term Ideas

- provider event-quality normalization with provider-specific event IDs and correction handling
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
