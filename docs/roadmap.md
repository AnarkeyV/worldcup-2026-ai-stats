# Roadmap

## Current release: v1.19.1 — Fixed Schedule Sync Mode Truthfulness

v1.19.1 is complete in source form.

It is a small dashboard-only truthfulness patch. The release corrects a misleading Sync Mode label by presenting the active fixed daily schedule rather than legacy interval compatibility metadata.

### Completed in v1.19.1

- [x] Provider Sync Runtime now shows `fixed_daily_times` as configured daily slots in the configured timezone.
- [x] The active schedule is displayed as **Fixed daily: 03:45 · 09:45 · 12:45 (Singapore time)**.
- [x] Interval wording is reserved for actual interval-mode scheduling.
- [x] Dashboard JavaScript cache-busting advances to `v1.19.1`.
- [x] Focused dashboard tests and full regression pass.
- [x] No provider schedule, threshold, Windows `.env`, Docker, database, Telegram, Cloudflared, Ollama, provider-request, sync-trigger, or data-write behavior changes.

### Retained v1.19.0 / v1.18.1 / v1.18.0 capabilities

- [x] Additive, read-only `freshness_context` in provider sync status and Live Match Centre freshness data.
- [x] Latest successful snapshot, next scheduled refresh, stale-after timing context, and diagnostics that separate failed syncs from stale snapshots.
- [x] Dashboard Freshness Context and conservative **Last confirmed live from stored snapshot** wording.
- [x] Conservative future-`unknown` display derivation from valid stored kickoff time only before kickoff with absent scores.
- [x] Explicit stored match-state contract: `live`, `completed`, `scheduled`, `unavailable`.
- [x] Local-only `GET /live-match-centre` API with factual sync-change and event-coverage evidence.

## Deliberately deferred

These remain deliberately outside v1.19.1:

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
