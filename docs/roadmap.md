# Roadmap

## Current release: v1.22.1 — Matchday Changes Load-Order Hotfix

v1.22.1 is complete in source form.

It fixes the browser-local Matchday comparison lifecycle so the dashboard does not treat temporary loading-time fixture state as a genuine empty knockout dataset. It preserves the stored-data-only Road to the Final, conservative fixture presentation, and every v1.22.0 factual boundary.

### Completed in v1.22.1

- [x] The local comparison panel stays in a loading state until the normal stored fixture list has completed loading.
- [x] A temporary empty fixture list cannot be cached as a genuine no-knockout-fixtures result.
- [x] Successful fixture loading resets stale comparison render state, allowing a valid saved baseline to report unchanged stored knockout data when appropriate.
- [x] Failed fixture loading renders an unavailable comparison state without reading, replacing, or discarding the existing browser-local baseline.
- [x] Full regression passes: 307 passed, 325 known warnings.
- [x] No provider schedule, threshold, active Windows `.env`, Docker, database, Telegram, Cloudflared, Ollama, provider-request, sync-trigger, server-side data-write, or background-job behavior changes.

### Retained v1.22.0 / v1.21.0 / v1.20.1 / v1.20.0 / v1.19.1 / v1.19.0 / v1.18.1 / v1.18.0 capabilities

- [x] Stored-data-only Road to the Final and browser-local Matchday changes remain separate from provider freshness and Live Match Centre sync-change evidence.

- [x] Knockout-first Matchday, Group Stage progressive disclosure, resilient More navigation, and evidence-first Official Match Video presentation.
- [x] Fixed daily scheduler wording: **Fixed daily: 03:45 · 09:45 · 12:45 (Singapore time)**.
- [x] Additive, read-only freshness context and conservative stored fixture-state presentation.
- [x] Local-only Live Match Centre with factual sync-change and stored-detail coverage evidence.
- [x] Grouped fixture browsing, provider-backed match detail, player leaders, local AI fallback, and runtime observability remain available.


## Deliberately deferred

These remain deliberately outside v1.22.1:

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
