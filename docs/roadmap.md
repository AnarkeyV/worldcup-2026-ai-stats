# Roadmap

## Current release: v1.21.0 — Knockout Stage UX & Official Match Video Links

v1.21.0 is complete in source form.

It shifts the live dashboard toward recognised provider-backed knockout fixtures, moves group-era information behind accessible progressive disclosure, repairs desktop More navigation behavior, and strengthens transparent official-video presentation.

### Completed in v1.21.0

- [x] Matchday prioritises recognised stored knockout fixtures without fabricating later-stage pairings, outcomes, or live state.
- [x] Fixture browsing offers stage-specific scopes for recognised Round of 32 through Final labels when supplied by stored provider data.
- [x] Group Standings, Group Race, and Group Insights are available in a semantic Group Stage disclosure that collapses only when recognised knockout fixtures exist.
- [x] Desktop and mobile More menus support destination close, Escape-to-close, click-away close, focus restoration, and viewport-change close behavior.
- [x] Desktop More navigation is released from the overflow/stacking context that clipped the opened panel.
- [x] Official Match Video presentation distinguishes verified match-specific videos, official coverage hubs, and unavailable records.
- [x] `mediacorp_sports_youtube` is limited to curator-verified direct `@SportsMediacorp` video URLs; no API key, discovery polling, scraping, or automatic import is added.
- [x] Full regression passes: 296 passed, 325 known warnings.
- [x] No provider schedule, threshold, active Windows `.env`, Docker, database, Telegram, Cloudflared, Ollama, provider-request, sync-trigger, or data-write behavior changes.

### Retained v1.20.1 / v1.20.0 / v1.19.1 / v1.19.0 / v1.18.1 / v1.18.0 capabilities

- [x] Fixed daily scheduler wording: **Fixed daily: 03:45 · 09:45 · 12:45 (Singapore time)**.
- [x] Additive, read-only freshness context and conservative stored fixture-state presentation.
- [x] Local-only Live Match Centre with factual sync-change and stored-detail coverage evidence.
- [x] Grouped fixture browsing, provider-backed match detail, player leaders, local AI fallback, and runtime observability remain available.


## Deliberately deferred

These remain deliberately outside v1.21.0:

- Any provider schedule, threshold, Windows `.env`, Docker, database, Telegram, Cloudflared, or Ollama configuration change.
- Automatic or browser-triggered provider polling.
- YouTube Data API credentials, automated YouTube discovery, scraping, automated video imports, or production video-record writes.
- Treating a future stored kickoff as provider-confirmed scheduling or using time to infer a live match.
- Fabricated later-round knockout pairings or outcomes when provider stage data is absent.
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
