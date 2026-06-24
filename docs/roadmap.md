# Roadmap

## Current release: v1.18.1 — Scheduled from Stored Kickoff

v1.18.1 is complete in source form.

It is a narrow data-quality and Matchday usability improvement: fixtures stored with `unknown` provider status can be shown as scheduled only when their existing stored kickoff data proves they are still future fixtures and their scores are absent.

### Completed in v1.18.1

- [x] Pure kickoff-aware display-state contract for future `unknown` fixtures.
- [x] UTC-aware future-kickoff validation with no inference from a naive or malformed timestamp.
- [x] `scheduled_sources` in the local-only Live Match Centre response.
- [x] Dashboard Scheduled tab, Matchday next-up context, counts, and fixture presentation use the same conservative display rule.
- [x] Clear **Scheduled from stored kickoff** and **Provider match status unavailable** wording.
- [x] No stored provider status rewrite, provider call, sync trigger, Telegram send, database write, browser polling, or runtime setting change.

### Retained v1.18.0 capabilities

- [x] Explicit stored match-state contract: `live`, `completed`, `scheduled`, `unavailable`.
- [x] Local-only `GET /live-match-centre` API.
- [x] Additive event-coverage evidence and successful-sync change sets.
- [x] Factual score, status, completion, goals, cards, substitutions, and provider-event-revision changes.
- [x] Live Match Centre inside Matchday and What changed? inside Provider Sync Runtime.

## Deliberately deferred

These remain deliberately outside v1.18.1:

- Historical reconstruction of sync deltas before v1.18 change capture.
- Treating a future stored kickoff as provider-confirmed scheduling or using time to infer a live match.
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
