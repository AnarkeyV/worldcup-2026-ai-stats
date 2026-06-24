# Roadmap

## Current release: v1.18.0 — Live Match Centre & Data Freshness

v1.18.0 is complete in source form.

It adds a read-only Live Match Centre built from stored provider data, explicit local freshness states, persisted v1.18+ sync-change evidence, and dashboard visibility for those facts.

### Completed in v1.18.0

- [x] Explicit stored match-state contract: `live`, `completed`, `scheduled`, `unavailable`.
- [x] Local-only `GET /live-match-centre` API.
- [x] Additive event-coverage evidence for goals, cards, and substitutions.
- [x] Additive successful-sync change-set records.
- [x] Factual changes for score, status, completion, goals, cards, substitutions, and provider-event revisions.
- [x] Live Match Centre inside Matchday.
- [x] What changed? inside Provider Sync Runtime.
- [x] Explicit historical and missing-data states.
- [x] Browser status handling that does not silently classify unknown statuses as upcoming.
- [x] No provider call, sync trigger, Telegram send, dashboard polling, or runtime setting change in the read path.

## Deliberately deferred

These are not hidden within v1.18.0:

- Historical reconstruction of sync deltas before v1.18 change capture.
- Full event-version history or provider event identifiers.
- Automatic provider polling from the browser.
- New provider assumptions, scraping, backfill work, or fabricated live timelines.
- Automatic updates to Telegram or scheduler behaviour.
- Runtime deployment, database changes, or Windows host changes before explicit approval.

## Candidate future work

Future work should remain evidence-led and separately approved.

| Area | Possible direction | Guardrail |
|---|---|---|
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
