# Roadmap

## Current release: v1.22.0 — Confirmed Knockout Path & Matchday Changes

v1.22.0 is complete in source form.

It adds a compact stored-data-only Road to the Final and a browser-local summary of confirmed knockout changes, while preserving knockout-first Matchday, Group Stage progressive disclosure, Match Story, detailed match data, freshness boundaries, and Official Match Video trust signals.

### Completed in v1.22.0

- [x] Road to the Final lists only recognised stored provider-backed stages and fixtures in the fixed Round of 32 through Final order.
- [x] Later stages appear only after matching stored fixtures exist; no empty future brackets, placeholder pairings, assumed winners, or fabricated advancement paths are shown.
- [x] A completed draw does not identify an advancing team, and the dashboard does not infer penalties, extra time, aggregate results, winners, or progression.
- [x] Existing fixture selection, Match Story, timeline, statistics, lineups, AI summary, player leaders, freshness, and Official Watch states remain available from the confirmed-path experience.
- [x] What changed since your last visit compares only already loaded stored knockout fixture data with a versioned browser-local snapshot.
- [x] Local comparison distinguishes first visit, newly stored fixtures, newly completed fixtures, confirmed score/status changes, unchanged state, and unavailable comparison state without claiming live delivery.
- [x] Full regression passes: 304 passed, 325 known warnings.
- [x] No provider schedule, threshold, active Windows `.env`, Docker, database, Telegram, Cloudflared, Ollama, provider-request, sync-trigger, server-side data-write, or background-job behavior changes.

### Retained v1.21.0 / v1.20.1 / v1.20.0 / v1.19.1 / v1.19.0 / v1.18.1 / v1.18.0 capabilities

- [x] Knockout-first Matchday, Group Stage progressive disclosure, resilient More navigation, and evidence-first Official Match Video presentation.
- [x] Fixed daily scheduler wording: **Fixed daily: 03:45 · 09:45 · 12:45 (Singapore time)**.
- [x] Additive, read-only freshness context and conservative stored fixture-state presentation.
- [x] Local-only Live Match Centre with factual sync-change and stored-detail coverage evidence.
- [x] Grouped fixture browsing, provider-backed match detail, player leaders, local AI fallback, and runtime observability remain available.


## Deliberately deferred

These remain deliberately outside v1.22.0:

- Any provider schedule, threshold, Windows `.env`, Docker, database, Telegram, Cloudflared, or Ollama configuration change.
- Automatic or browser-triggered provider polling.
- YouTube Data API credentials, automated YouTube discovery, scraping, automated video imports, or production video-record writes.
- Treating a future stored kickoff as provider-confirmed scheduling or using time to infer a live match.
- Fabricated later-round knockout pairings or outcomes when provider stage data is absent.
- Inferring advancement from a completed or drawn fixture without explicit stored provider evidence.
- Treating browser-local comparison as real-time delivery, provider freshness, or Live Match Centre evidence.
- Historical reconstruction of sync deltas before v1.18 change capture.
- Full event-version history or provider event identifiers.
- New provider assumptions, backfill work, or fabricated live timelines.
- Runtime deployment, database changes, or Windows host changes before explicit approval.

## Candidate future work

Future work should remain evidence-led and separately approved.

| Area | Possible direction | Guardrail |
|---|---|---|
| Sync policy review | Assess schedule and threshold alignment after real observed matchdays | Do not change runtime schedule or thresholds without a separate audited decision |
| Event correction history | Provider IDs and durable correction/version lineage | Do not claim a complete history until a provider supports it and stored data proves it |
| Provider coverage | Better normalised detail coverage from supported providers | No scraped or unsupported sources |
| Match-day UX | Small readability improvements for high-density tournament days | Preserve mobile clarity and avoid generic sports-app clutter |
| Data operations | Operator-visible audit/read tools | Do not trigger syncs or writes from read dashboards |
| Runtime verification | Approved post-release Windows deployment and reboot/Ollama verification | Preserve report-only Cloudflared/Ollama boundaries |
| Security | Authentication and stronger secret-management design | Separate milestone with explicit threat model and migration plan |

## Release process

A source milestone is not a runtime deployment.

For every release:

1. Complete source changes on the MacBook.
2. Run focused tests, then full regression.
3. Commit and push the feature branch.
4. Open, review, and merge the pull request.
5. Tag and publish the GitHub release.
6. Obtain explicit approval before refreshing the Windows runtime.
7. Perform read-only runtime verification without triggering provider sync or Telegram delivery.
