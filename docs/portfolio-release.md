# Portfolio Release Summary

## World Cup 2026 AI Stats v1.18.0 — Live Match Centre & Data Freshness

World Cup 2026 AI Stats is a self-hosted, provider-backed football intelligence dashboard built as a practical DevOps, backend, automation, observability, and local-AI project.

The v1.18.0 milestone focuses on a realistic matchday problem: making a dashboard more useful during tournament play without pretending stored provider data is a full real-time sports feed.

## What v1.18.0 delivers

- A read-only Live Match Centre for fixtures explicitly stored as live.
- Stored freshness states and local update timestamps.
- Provider-backed change capture for scores, statuses, completion, goals, cards, substitutions, and provider-event revisions.
- Explicit coverage states for stored match events.
- A concise What changed? view tied to persisted successful sync data.
- Better handling for unknown, postponed, cancelled, abandoned, and unsupported statuses.
- Mobile-aware dashboard additions that preserve existing Match Story, Match Detail, navigation, and official-watch boundaries.

## Engineering decisions

### Truthful data presentation

The milestone intentionally does not create a fake live-score experience.

A match is labelled live only when the stored provider status explicitly supports that claim. Freshness describes the age of the application’s latest successful stored snapshot, not a promise of real-time delivery.

Missing data remains visible as unavailable, not provided, coverage unknown, or detail not available.

### Change evidence instead of UI guesses

The project now stores additive v1.18+ successful-sync change sets. This lets the dashboard show factual deltas without reconstructing a timeline from overwritten records.

Historical syncs from before this change are explicitly labelled as not recorded rather than shown as “no changes.”

### Safe database evolution

The release avoids altering existing deployed tables. It adds companion evidence tables that can be created through the project’s existing SQLAlchemy bootstrap on a later approved runtime deployment.

### Read-only operations boundary

The Live Match Centre endpoint and dashboard refresh use local stored data only. They do not call a provider, trigger sync, write to the database, send Telegram, or alter scheduler state.

## Technical stack

```text
FastAPI
SQLAlchemy
PostgreSQL
Static HTML/CSS/JavaScript dashboard
Docker Compose
Prometheus and Grafana
Telegram Bot API
Ollama with llama3.2:1b
Cloudflare Tunnel
GitHub Actions
pytest
```

## Development workflow

- MacBook Pro: VS Code, Python virtual environment, tests, Git, code review.
- Windows laptop: Docker runtime and public demo host.
- Cloudflare Tunnel: public mobile access.
- SSH: post-release runtime verification only.

## Verification

```text
267 automated tests passed
316 known FastAPI/Starlette Python 3.14 deprecation warnings
```

The warnings are Python 3.14 framework deprecation warnings, not test failures.

## Portfolio talking points

- Designed a bounded live-match experience around persisted facts rather than generic sports-app imitation.
- Introduced explicit data-quality and freshness states to prevent misleading user-facing claims.
- Added a read-only API composition layer that joins fixture, detail, coverage, sync-run, and change-set data without operational side effects.
- Used additive persistence records to evolve a self-hosted database safely without rewriting existing schema in place.
- Preserved runtime safety: no deployment, sync, Telegram, scheduler, Cloudflared, Ollama, or secret changes occurred during source development.

## Current limits

- The dashboard is a stored provider snapshot, not a certified real-time delivery system.
- Provider payload quality determines available event coverage.
- Historic sync changes before v1.18 are not reconstructed.
- No scraping, arbitrary video sources, hard-coded events, invented player facts, or unsupported provider assumptions are used.
- Runtime deployment requires a separate explicit approval after PR merge, tag, and release.
