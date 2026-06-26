# Roadmap

## Current release: v1.19.0 — Freshness Context and Matchday Trust Signals

v1.19.0 is complete in source form.

It is a narrow reliability and Matchday trust improvement. The release explains how a successful stored provider refresh can later be stale under the existing fixed-time schedule, without inventing data, inferring live state from time, or changing operational behavior.

### Completed in v1.19.0

- [x] Additive, read-only `freshness_context` in provider sync status and Live Match Centre freshness data.
- [x] Latest successful snapshot, next scheduled refresh, and stale-after timing context, with safe configured-timezone display values.
- [x] Diagnostics separating `latest_sync_failed`, stale stored snapshots, and snapshots that become stale before the next scheduled refresh.
- [x] Dashboard Freshness Context and conservative **Last confirmed live from stored snapshot** wording when freshness is stale or the latest refresh failed.
- [x] Focused tests for fixed-slot schedule gaps, thresholds, timezone-aware values, failed-sync distinction, and stale live-state wording.
- [x] No provider schedule change, browser polling, provider request, sync trigger, database write, Telegram send, Docker change, Cloudflared change, Ollama change, or active runtime `.env` change.

### Retained v1.18.1 / v1.18.0 capabilities

- [x] Conservative future-`unknown` display derivation: stored kickoff may support scheduled display only before kickoff with valid timezone-aware time and absent scores.
- [x] Explicit stored match-state contract: `live`, `completed`, `scheduled`, `unavailable`.
- [x] Local-only `GET /live-match-centre` API.
- [x] Additive event-coverage evidence and successful-sync change sets.
- [x] Factual score, status, completion, goals, cards, substitutions, and provider-event-revision changes.
- [x] Live Match Centre inside Matchday and What changed? inside Provider Sync Runtime.

## Deliberately deferred

These remain deliberately outside v1.19.0:

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
