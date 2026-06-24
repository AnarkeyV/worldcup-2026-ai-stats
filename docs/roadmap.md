# Roadmap

World Cup 2026 AI Stats is developed through small, test-backed milestones. Each milestone should improve matchday usefulness, data honesty, runtime resilience, or portfolio value without weakening the self-hosted workflow.

---

## Current Status

```text
Current release: v1.17.1 — Runtime Reliability Safeguards
Release verification: 241 tests passed
Known warnings: 296 FastAPI/Starlette Python 3.14 deprecation warnings
Previous v1.17.0 verification: 234 tests passed
Primary runtime: Windows laptop + Docker Compose
Development machine: MacBook Pro + VS Code + Python venv
Public dashboard: https://wc2026.khairulrizal.qzz.io/dashboard
```

Current live capabilities:

- visual Matchday home with live/latest/next stored-fixture cards and a local Data health badge
- provider-backed fixtures and stored rich match details
- read-only Match Story with score progression only when stored goals reconcile with the stored score
- key-event narrative for goals, cards, substitutions, and stoppage time when supplied
- paired team-stat comparisons that omit incomplete provider data
- Official Highlights / Watch states using server-vetted outbound destinations only
- read-only Match Data Coverage with visual coverage progress and missing-detail follow-up
- comparative player and Group Race bars derived from existing stored responses
- local Ollama health and summary workflow with deterministic fallback
- provider-backed goals and card leaderboards
- top-two Group Race board across populated groups
- persisted fixture sync audit history and safe freshness states
- fixed-time provider scheduling and scheduled Telegram digest policy configured separately
- Prometheus, Grafana, Cloudflare access, and Windows Docker runtime support
- read-only Windows runtime status checker with local/public version-consistency reporting
- bounded Docker/container recovery and report-only Cloudflared/Ollama safeguards

---

## v1.17.1 Release Notes

### Runtime Reliability Safeguards

**Goal:** Make the personally hosted Windows runtime easier to inspect and safer to recover without turning sensitive host services into blind auto-repair targets.

Delivered scope:

- read-only Windows runtime status checker for Docker, backend, dashboard, Cloudflared, public health, host Ollama, application AI health, task state, and local/public version consistency
- `-FailOnCritical` support for local operator checks without adding a mutating automation path
- Cloudflared and Ollama changed to report-only in the existing startup and watchdog scripts
- Docker Desktop startup and unhealthy-container recovery retained as the existing bounded recovery scope
- private-safe recovery guide with no tunnel token, credential file, active `.env`, model-file, or task-XML exposure
- focused tests and candidate-runtime execution against the real v1.17.0 Windows host

Current boundaries retained:

- no provider request, sync, backfill, scheduler change, Telegram delivery, active `.env` change, Docker rebuild, Cloudflared action, Ollama action, or Scheduled Task action during status checks
- no automatic tunnel recreation, config copying, model replacement, model download, or local AI exposure beyond the Windows host
- active runtime promotion remains explicit and candidate/back-up controlled

---

## v1.17.0 Release Notes

### Provider-Backed Match Story and Official Watch

**Goal:** Help a viewer understand what happened in a completed match from local provider-backed data, while treating official video as a trusted outbound option rather than a risky content-integration feature.

Delivered scope:

- local-read `GET /fixtures/{fixture_id}/story`
- score progression gated by exact stored score/event reconciliation
- goals, cards, substitutions, and stoppage-time timeline support
- partial and unavailable states instead of fabricated charts or zero values
- paired provider-stat comparisons only
- provider and stored-refresh provenance
- strict official outbound-link policy and fallback coverage hubs
- Story-first match-detail dashboard rendering with mobile-first layout
- cache-bust/version alignment and full regression verification

Current boundaries retained:

- no provider request, sync, backfill, scheduler change, Telegram delivery, Docker action, or Windows runtime action during source development
- no scraping, automated web discovery, video download, rehosting, thumbnail proxying, arbitrary fan upload, or third-party embed
- no public write API for official-video links
- no hard-coded match-specific highlight links
- no prediction, xG timeline, shot map, possession-over-time chart, or inferred football event

---

## Recommended Next Small Milestone

### Live Match Centre and Data Freshness

The next feature milestone should deepen matchday usefulness without weakening the data-honesty rules established so far.

Possible scope:

- clearer live/in-progress fixture state and stored provider refresh timestamp
- compact “What changed?” summary after a stored refresh, only when a provider-backed score, goal, card, substitution, or status change is genuinely present
- focused, explicitly approved refresh behaviour for fixtures that are already in progress, without broad polling of all records
- improved delayed-detail and provider-gap states in Match Story
- tests for no-change, incomplete, delayed, and corrected-provider states

This should remain local-data-first, avoid invented live commentary, and keep provider work separate from ordinary dashboard reads.

---

## Longer-Term Ideas

### Data depth and truthfulness

- provider-specific event IDs and historical correction/version handling
- richer provider event taxonomy where genuinely supplied: penalties, own goals, VAR, assist data, and event detail
- provider-supported shot locations, xG, or possession-over-time only after capability and contractual availability are verified
- factual stored-data match report export
- provider data freshness and delayed-detail indicators per fixture

### Dashboard and user experience

- team comparison views based only on stored comparable metrics
- match story share links or printable summary cards
- optional verified-source thumbnails only where platform usage is explicitly appropriate
- accessibility review for event colours, keyboard tabs, and reduced-motion behaviour
- per-user dashboard preferences after authentication exists

### Operations and resilience

- controlled curator import for official match links
- database backup and restore workflow
- lightweight background job queue where a real operational need appears
- CI/CD deployment automation
- low-cost VPS or cloud deployment
- optional Kubernetes demonstration deployment
- authentication and role-based dashboard access

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
| v1.17.1 | Completed | Runtime reliability safeguards, read-only status checker, and report-only Cloudflared/Ollama boundary |
| v1.17.0 | Completed | Provider-backed match story and official watch policy/UI |

---

## Roadmap Principles

- Prefer a small source of truth over a large unverified feature.
- Do not make a chart merely because a dashboard has room for one.
- Do not infer a football fact that the provider did not supply.
- Treat missing data as an explicit product state, not a zero.
- Treat video as a rights-sensitive outbound resource.
- Keep automation opt-in and separate from read-only dashboard behaviour.
- Keep MacBook development and Windows Docker runtime responsibilities distinct.
- Do not expose secrets or replace active runtime configuration without an approved candidate-and-backup workflow.
