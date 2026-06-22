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

## Candidate Next Milestone

### Live Matchday Automation and Data Quality

**Goal:** Improve the project’s ability to operate safely during live matchdays while keeping provider data transparent and reviewable.

Potential scope:

- scheduled provider sync with explicit opt-in configuration
- persisted sync-run history instead of process-memory-only runtime state
- Telegram notification policy for newly completed matches and meaningful incidents
- dashboard indicators for stale data and last successful detail refresh
- provider event-quality normalization for duplicate, malformed, or corrected events
- richer player detail where the provider supplies reliable fields
- optional match report export using only stored factual data

This is intentionally a candidate scope, not a committed release contract. It should be selected and broken into a small milestone before implementation.

---

## Longer-Term Ideas

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
