# Roadmap

## Current release: v1.20.1 — Standings & Dashboard Resilience Hotfix

v1.20.1 is complete in source form.

It corrects an ungrouped-fixture standings edge case and makes the dashboard preserve healthy fixture and Matchday data when a secondary panel is unavailable.

### Completed in v1.20.1

- [x] Completed fixtures without an explicit group are excluded from group standings while remaining visible in fixture and match-detail views.
- [x] `/standings` and dependent `/ai/insights` no longer fail when stored provider data contains both grouped and ungrouped completed fixtures.
- [x] Dashboard fixture, Matchday, standings, group-insights, and structured-AI-insights panels settle independently.
- [x] A secondary data-panel failure no longer hides healthy fixture-browser data.
- [x] Dashboard and Live Match Centre static asset cache-busting values advance to `v1.20.1`.
- [x] Focused coverage and full regression pass: 283 passed, 325 known warnings.
- [x] No provider schedule, threshold, active Windows `.env`, Docker, database, Telegram, Cloudflared, Ollama, provider-request, sync-trigger, or data-write behaviour changes.

### Retained from v1.20.0


- [x] Matchday cards prioritise **Now**, **Next**, and **Latest**.
- [x] A compact Data trust strip links to Sync details and remains separate from Match detail coverage.
- [x] Stored live fixtures use **Last recorded live** when freshness is stale or otherwise not current enough for present-tense wording.
- [x] Matchday hero selection reuses the established conservative fixture-state classifier.
- [x] Primary desktop and mobile navigation prioritises Matchday, Matches, Groups, and Players; More retains Overview, Data, Insights, and Sync.
- [x] Sync change records use native Show change details disclosure.
- [x] Touch targets and keyboard focus styling are strengthened for the matchday controls.
- [x] Focused UI tests and full regression pass: 281 passed, 325 known warnings.
- [x] No provider schedule, threshold, Windows `.env`, Docker, database, Telegram, Cloudflared, Ollama, provider-request, sync-trigger, or data-write behaviour changes.

### Retained v1.20.0 / v1.19.1 / v1.19.0 / v1.18.1 / v1.18.0 capabilities

- [x] Fixed daily scheduler wording: **Fixed daily: 03:45 · 09:45 · 12:45 (Singapore time)**.
- [x] Additive, read-only `freshness_context` in provider sync status and Live Match Centre freshness data.
- [x] Latest successful snapshot, next scheduled refresh, stale-after timing context, and diagnostics that separate failed syncs from stale snapshots.
- [x] Conservative future-`unknown` display derivation from valid stored kickoff time only before kickoff with absent scores.
- [x] Explicit stored match-state contract: `live`, `completed`, `scheduled`, `unavailable`.
- [x] Local-only `GET /live-match-centre` API with factual sync-change and event-coverage evidence.

## Deliberately deferred

These remain deliberately outside v1.20.1:

- Any provider schedule, threshold, Windows `.env`, Docker, database, Telegram, Cloudflared, or Ollama configuration change.
- Automatic or browser-triggered provider polling.
- Treating a future stored kickoff as provider-confirmed scheduling or using time to infer a live match.
- Historical reconstruction of sync deltas before v1.18 change capture.
- Full event-version history or provider event identifiers.
- New provider assumptions, scraping, backfill work, or fabricated live timelines.
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
