# Roadmap

World Cup 2026 AI Stats is developed through small, test-backed milestones. Each milestone should improve matchday usefulness, data honesty, runtime resilience, or portfolio value without weakening the self-hosted workflow.

---

## Current Status

```text
Current release: v1.17.0 — Provider-Backed Match Story and Official Watch
Release verification: 234 tests passed
Known warnings: 296 FastAPI/Starlette Python 3.14 deprecation warnings
Previous v1.16.0 verification: 218 tests passed
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

### Controlled official-link curation workflow

The v1.17.0 policy and storage model are intentionally ready before links are populated. The next small step should be a **controlled local curator workflow**, not automatic discovery.

Possible scope:

- a local-only, operator-run import command or checked-in review file with explicit verification fields
- dry-run validation against the existing source policy before data is written
- an auditable, bounded manifest with fixture ID, source key, direct URL, content type, territory, published time, and verification time
- idempotent upsert behaviour and a clear rejection report
- no public write endpoint, browser form, scraping, or provider dependency
- focused tests for bad source, bad URL, duplicate, missing verification, and dry-run safety

This would allow a human to add individually researched match links while preserving the current no-trust-by-default boundary.

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
