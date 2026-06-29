# World Cup 2026 AI Stats

![Version](https://img.shields.io/badge/version-v1.20.1-purple)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Database](https://img.shields.io/badge/database-PostgreSQL-336791)
![AI](https://img.shields.io/badge/AI-Ollama%20%2B%20Local%20Llama-green)
![Notifications](https://img.shields.io/badge/notifications-Telegram-lightblue)
![Monitoring](https://img.shields.io/badge/monitoring-Prometheus%20%2B%20Grafana-orange)

A self-hosted World Cup 2026 intelligence dashboard for provider-backed fixtures, factual stored-data freshness, match storytelling, standings, player event leaders, local AI summaries, Telegram alerts, and runtime observability.

**Public dashboard**

```text
https://wc2026.khairulrizal.qzz.io/dashboard
```

**Current release**

```text
v1.20.1 — Standings & Dashboard Resilience Hotfix
```

**Release verification**

```text
283 automated tests passed
325 known FastAPI/Starlette Python 3.14 deprecation warnings
```

## Why this project exists

World Cup 2026 AI Stats is a local-first football analytics project built as a practical DevOps, backend, automation, observability, and AI portfolio system.

It aims to be useful on matchday without pretending the available provider data is richer or fresher than it is. The dashboard distinguishes stored facts from unavailable or delayed data instead of filling gaps with guessed events, invented player details, fake timelines, or unverified live claims.

## v1.20.1: Standings & Dashboard Resilience Hotfix

v1.20.1 is a focused corrective release for provider data that includes a completed fixture without an explicit group label.

### What changed

- Group standings now exclude completed fixtures without an explicit `group_name`. Those fixtures remain available in the fixture browser and match-detail views, but do not participate in group rankings.
- The same guard keeps dependent structured AI insights available when an ungrouped completed fixture is present.
- Dashboard core panels now settle independently: a standings, group-insights, or structured-AI-insights failure no longer hides a healthy fixture browser or Matchday view.
- Dashboard and Live Match Centre cache-busting values advance to `v1.20.1`.

### Validation

- Focused standings, AI, and dashboard coverage: **82 passed**.
- Full regression: **283 passed**.
- Known warnings: **325** FastAPI/Starlette Python 3.14 deprecation warnings.
- Static JavaScript syntax check and `git diff --check` completed without findings.

## v1.20.0: Matchday Home & Compact Sync UX

v1.20.0 improves the dashboard's matchday information hierarchy while preserving the factual stored-data boundaries established in v1.18.1 through v1.19.1.

### Changed

- Matchday now prioritises **Now**, **Next**, and **Latest** fixture cards.
- A compact **Data trust** strip presents provider-snapshot freshness separately from **Match detail coverage**, which remains a local stored-detail measure.
- A stored live fixture is labelled **Last recorded live** when snapshot freshness is stale; present-tense wording is reserved for a fresh or aging stored snapshot.
- Future fixtures derived from a valid stored kickoff are labelled **Upcoming from stored kickoff**. Explicit provider scheduled states remain distinct.
- Desktop and mobile primary navigation prioritise Matchday, Matches, Groups, and Players, with Overview, Data, Insights, and Sync retained under **More**.
- Sync's factual change summary now uses native **Show change details** disclosure for individual records.
- Cache-busting values for dashboard and Live Match Centre CSS and JavaScript advance to `v1.20.0`.

### Accessibility and truthfulness rules

- Interactive navigation, fixture controls, cards, and disclosure controls use 44px minimum tap targets with visible keyboard focus.
- The established four-state fixture display contract remains: Live, Completed, Upcoming, and Data unavailable.
- Matchday uses the same conservative fixture-state classifier as the fixture browser.
- Time is never used to infer that a fixture is live. A past or unresolved `unknown` fixture remains unavailable.
- This release changes front-end presentation only. It does not change provider schedules, thresholds, sync behaviour, provider requests, stored data, Telegram, Docker, Cloudflared, Ollama, or an active runtime `.env`.
- Windows runtime deployment and public visual review remain separate approved steps.

## v1.19.1: Fixed Schedule Sync Mode Truthfulness

v1.19.1 is a small dashboard-only truthfulness patch. It corrects the Provider Sync Runtime display so a fixed daily scheduler is shown as the configured Singapore-time slots rather than as an interval derived from legacy compatibility metadata.

### Changed

- `fixed_daily_times` now displays **Fixed daily: 03:45 · 09:45 · 12:45 (Singapore time)** using the scheduler API payload.
- Interval wording such as **Every 30 min** is now shown only when the scheduler is actually interval-based.
- The dashboard JavaScript cache-buster advances to `v1.19.1` so the corrected label is fetched after deployment.

### Truthfulness rules

- This patch changes display wording only. It does not change the configured provider schedule, thresholds, scheduler behavior, provider requests, stored fixtures, or sync history.
- `interval_minutes` remains a backward-compatible status field. It does not describe a `fixed_daily_times` runtime schedule.
- The v1.19.0 Freshness Context and v1.18.1 no-time-inference safeguards remain unchanged.

## v1.19.0: Freshness Context and Matchday Trust Signals

v1.19.0 makes stored-snapshot freshness easier to interpret on matchday. It explains the relationship between the latest successful stored provider refresh, the configured Asia/Singapore fixed-time schedule, and the point at which that snapshot becomes stale.

### Added

- Additive, read-only `freshness_context` metadata in `GET /fixtures/sync/status`.
- Mirrored schedule-aware context in `GET /live-match-centre` under `data_freshness.freshness_context`.
- Exact stored-snapshot times for the last successful refresh, next scheduled refresh, and stale-after boundary, with derived configured-timezone display values when available.
- A factual diagnostic that distinguishes a successful-but-stale stored snapshot from a failed latest refresh.
- Dashboard Freshness Context presentation for last successful snapshot, next scheduled refresh, and stale-after time.
- Conservative stale Live Match Centre wording: **Last confirmed live from stored snapshot**.

### Truthfulness rules

- A successful provider refresh and a stale snapshot are compatible facts: success records the terminal result of the latest sync attempt, while freshness records the age of the latest successful stored snapshot.
- The schedule-aware diagnostic is explanatory only. It does not create a new sync, change a scheduled time, rewrite a provider status, or alter stored data.
- A stale timestamp never makes a fixture live or completed. Fixture state remains based on stored provider status and the conservative v1.18.1 display contract.
- Reading these routes and dashboard panels remains local-data-only: no provider call, sync, database write, Telegram send, or scheduler change occurs.

## v1.18.1: Scheduled from Stored Kickoff

v1.18.1 is a small factual display-state improvement for fixtures whose provider status is stored as `unknown` but whose stored kickoff still gives reliable future-fixture context.

### Added

- Kickoff-aware display derivation for fixtures stored with `unknown` status.
- `scheduled_sources` in `GET /live-match-centre`, separating explicit provider-scheduled fixtures from fixtures scheduled from stored kickoff data.
- Dashboard labels for **Scheduled from stored kickoff** with the supporting note **Provider match status unavailable**.

### Truthfulness rules

- Stored provider status remains unchanged. A derived scheduled display state never rewrites `unknown` in the database.
- A fixture is derived as scheduled only when its stored status is `unknown`, its UTC kickoff is valid and in the future, and both stored scores are absent.
- Explicit provider states remain authoritative.
- Time is never used to infer a live match.
- An unknown fixture at or after kickoff, with a missing or malformed kickoff, with stored scores, or with a postponed/cancelled/abandoned status remains unavailable.
- Reading the dashboard and Live Match Centre remains local-data-only: no provider call, sync, database write, Telegram send, or scheduler change occurs.

## v1.18.0: Live Match Centre & Data Freshness

v1.18.0 adds a focused Live Match Centre that makes existing stored provider data easier to interpret during tournament matches.

### Added

- Read-only `GET /live-match-centre` aggregation endpoint.
- Explicit application match states: `live`, `completed`, `scheduled`, and `unavailable`.
- Matchday Live Match Centre cards for fixtures explicitly stored as live.
- Stored snapshot freshness and local record-update timestamps.
- A concise **What changed?** view inside Provider Sync Runtime.
- Provider-backed delta capture for score, status, match-completion, goals, cards, substitutions, and provider-event revisions.
- Additive companion persistence for event-coverage evidence and v1.18+ successful sync change sets.
- Clear dashboard states when live data, detail coverage, or a successful refresh is unavailable.

### Truthfulness rules

- A fixture is shown as live only when the stored provider status maps explicitly to `live`.
- Unknown, postponed, cancelled, abandoned, or unsupported statuses remain `unavailable` unless an `unknown` fixture has a future valid stored UTC kickoff and no stored scores; that narrow case is labelled as scheduled from stored kickoff, not provider-confirmed scheduling.
- Freshness describes the age of the latest successful **stored snapshot**. It is not a guarantee of real-time provider delivery.
- Event changes are shown only when the provider-backed event category was stored and covered by the persisted record.
- A missing detail category means `not_provided`, `coverage_unknown`, or `detail_not_available`; it is never converted into “no event happened.”
- Historical sync runs from before v1.18 change capture are labelled `not_recorded_before_v1_18`, not represented as an empty change list.
- Reading the Live Match Centre does not call a provider, trigger sync, backfill data, write to PostgreSQL, send Telegram, or change scheduler state.
- The dashboard does not poll automatically. Its refresh action re-reads the local API only.

## Core capabilities

### Live Match Centre and sync changes

| Capability | What it shows | What it does not claim |
|---|---|---|
| Live Match Centre | Fixtures whose stored status is explicitly live, score, local update time, and stored event coverage | That the provider is real-time or that no unreported event occurred |
| Data freshness | Latest successful stored-sync time, age, state, scheduled next refresh, stale-after boundary, and explanatory diagnostic | That the result is current beyond the stored snapshot or that a successful refresh cannot later become stale |
| What changed? | Persisted v1.18+ score/status/event deltas from successful syncs | A full historical replay or changes before v1.18 capture |
| Event coverage | Whether stored goals, cards, and substitutions are available, not supplied, unknown, or absent with no detail | Complete match-event coverage |

### Match Story and official watch

The Match Story remains a derived local view, not a live commentary feed.

| Story element | Requirement before it is shown |
|---|---|
| Score progression | Stored scores exist; stored goals have valid sides and usable minutes; goal totals reconcile with the stored score |
| Key-event timeline | Valid stored goals, cards, or substitutions exist |
| Match-stat comparison | Both teams have a finite provider value for the same metric |
| Official Watch card | A locally stored, manually verified outbound record passes source, URL, content-type, territory, and verification checks |

Missing information remains unavailable or partial. It is never filled with a guess.

### Provider-backed fixtures and detail

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/fixtures` | List and filter stored fixtures |
| `GET` | `/fixtures/data-quality` | Read aggregate stored match-detail coverage |
| `GET` | `/fixtures/{fixture_id}` | Read one stored fixture |
| `GET` | `/fixtures/{fixture_id}/detail` | Read raw locally stored rich detail |
| `GET` | `/fixtures/{fixture_id}/story` | Read computed local Match Story and official-watch state |
| `GET` | `/live-match-centre` | Read stored live-match, freshness, coverage, and latest-change state |
| `POST` | `/fixtures/sync/sample` | Seed deterministic sample fixtures |
| `POST` | `/fixtures/sync/provider` | Sync configured provider data |
| `GET` | `/fixtures/sync/status` | Read latest persisted sync state |
| `GET` | `/fixtures/sync/history` | Read persisted sync-run history |

All read routes above use stored application data. They do not contact a provider or change data.

### Standings, players, and local AI

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/standings` | Group table calculation |
| `GET` | `/insights/groups` | Group leaders, attacks, defences, unbeaten and winless teams |
| `GET` | `/ai/insights` | Structured AI-ready insights and Group Race |
| `GET` | `/players/leaders` | Provider-derived scorer and card leaderboards |
| `GET` | `/ai/latest-completed/summary` | Latest completed result with stored incidents and scorers |
| `GET` | `/ai/health` | Confirm local AI availability |
| `GET` | `/ai/fixtures/summary` | Tournament-wide fixture summary |
| `GET` | `/ai/fixtures/{fixture_id}/summary` | Fixture-specific summary |

The project does not infer assists when the provider does not supply assist events.

## Architecture at a glance

```text
MacBook Pro
VS Code + Python venv + Git
        |
        | Git / SSH control
        v
Windows laptop runtime host
Docker Desktop + Docker Compose
        |
        |-- FastAPI backend + static dashboard
        |-- PostgreSQL
        |-- Prometheus
        |-- Grafana
        |-- Cloudflare Tunnel
        |-- Ollama on Windows host
        +--> Public mobile dashboard
```

External integrations remain bounded:

```text
Configured provider API ---> FastAPI backend ---> PostgreSQL
Telegram Bot API <--- manual notifications and scheduled digests
Cloudflare Tunnel ---> public dashboard URL
Ollama <--- local AI health and summaries
Prometheus <--- backend metrics
Grafana <--- monitoring dashboard
```

Read the fuller design in [docs/architecture.md](docs/architecture.md).

## Development and runtime workflow

| Machine | Role |
|---|---|
| MacBook Pro | Main development, tests, Git control, package review |
| Windows laptop | Docker runtime and demo host |
| VS Code | Main editor |
| Python venv | Local test environment |
| SSH | Remote runtime verification after release approval |

### MacBook development

```bash
cd ~/documents/worldcup-2026-ai-stats/backend
source .venv/bin/activate
python -m pytest -q

cd ..
git status --short
git diff --check
```

Do not run Docker on the MacBook.

### Windows runtime

Only after merge, tag, GitHub release, and explicit runtime-deployment approval:

```powershell
cd "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats"
.\scripts\windows\get-worldcup-runtime-status.ps1
```

The status checker is read-only. It does not rebuild or restart Docker, run a provider sync, send Telegram, start or restart Cloudflared, start or stop Ollama, change Scheduled Tasks, or print `.env` values.

Docker/container recovery remains bounded to the existing startup/watchdog scripts. Cloudflared and Ollama remain report-only and require a human-approved recovery action when unavailable.

## Configuration and secrets

Create a local environment file:

```bash
cp .env.example .env
```

Edit `.env` locally and never commit it.

Keep local:

- provider API keys
- Telegram bot token and chat ID
- Cloudflare credentials
- production database credentials
- host-specific runtime files

The source release updates only the safe `APP_VERSION` placeholder in `.env.example`. It never creates, replaces, or exposes an active runtime `.env`.

## Testing

Run the full suite from `backend`:

```bash
python -m pytest -q
```

v1.20.1 source verification:

- 82 focused standings, AI, and dashboard tests passed.
- 283 full regression tests passed.
- 325 known FastAPI/Starlette Python 3.14 deprecation warnings.

v1.20.0 source verification:

```text
281 passed, 325 warnings
```

The warnings are FastAPI/Starlette Python 3.14 deprecations related to `asyncio.iscoroutinefunction`. They are warnings, not failing tests.

## Release workflow

```bash
git checkout main
git pull --ff-only origin main
git checkout -b feature/vX.Y.Z-description

cd backend
source .venv/bin/activate
python -m pytest -q

cd ..
git add .
git commit -m "Implement vX.Y.Z"
git push -u origin feature/vX.Y.Z-description
```

Then:

1. Open and review the pull request.
2. Merge into `main`.
3. Pull merged `main` locally.
4. Tag the release.
5. Publish the GitHub release.
6. Only after explicit approval, refresh the Windows runtime from merged `main`.
7. Verify the runtime safely without triggering provider sync or Telegram delivery.
8. Delete the merged feature branch locally and remotely.

## Documentation

- [Architecture](docs/architecture.md)
- [Changelog](docs/changelog.md)
- [Roadmap](docs/roadmap.md)
- [Demo Walkthrough](docs/demo-walkthrough.md)
- [Portfolio Release Summary](docs/portfolio-release.md)
- [v1.20.1 Standings & Dashboard Resilience Hotfix](docs/v1.20.1-standings-dashboard-resilience-hotfix.md)
- [v1.20.0 Matchday Home & Compact Sync UX](docs/v1.20.0-matchday-home-compact-sync-ux.md)
- [v1.19.1 Fixed Schedule Sync Mode Truthfulness](docs/v1.19.1-fixed-schedule-sync-mode.md)
- [v1.19.0 Freshness Context and Matchday Trust Signals](docs/v1.19.0-freshness-context-trust-signals.md)
- [v1.17.1 Runtime Reliability Notes](docs/v1.17.1-runtime-reliability.md)
- [Windows Runtime Recovery Guide](docs/windows-runtime-recovery.md)
- [v1.17.0 Match Story and Official Watch Notes](docs/v1.17.0-match-story-official-watch.md)

## Milestone history

| Version | Milestone | Status |
|---|---|---|
| v0.1.0–v0.8.0 | Foundation, provider abstraction, notifications, dashboard, filters, local Llama | Completed |
| v1.1.0 | Group standings engine | Completed |
| v1.4.x | Monitoring, Grafana polish, Telegram hardening, documentation cleanup | Completed |
| v1.5.0 | Portfolio release polish | Completed |
| v1.6.0 | Real match-data sync improvement | Completed |
| v1.7.0 | Provider sync observability and runtime demo | Completed |
| v1.8.0 | AI insights upgrade | Completed |
| v1.9.0 | Live local AI, Telegram mobile links, Cloudflare, and Windows runtime resilience | Completed |
| v1.10.0 | Match detail dashboard and README polish | Completed |
| v1.11.0 | Mobile rich match dashboard, provider leaders, and Group Race | Completed |
| v1.12.0 | Safe matchday sync, audit history, and data freshness | Completed |
| v1.13.0 | Provider event integrity and stored detail coverage | Completed |
| v1.14.0 | Match data quality dashboard | Completed |
| v1.15.0 | Visual Matchday UX and charts | Completed |
| v1.16.0 | Fixed-time scheduled sync and Telegram digest | Completed |
| v1.17.0 | Provider-backed Match Story and Official Watch | Completed |
| v1.17.1 | Runtime reliability safeguards and read-only Windows status checker | Completed |
| v1.20.1 | Standings and dashboard resilience hotfix | Completed |
| v1.20.0 | Matchday Home and compact Sync UX | Completed |
| v1.19.1 | Fixed schedule sync-mode truthfulness | Completed |
| v1.19.0 | Freshness context and matchday trust signals | Completed |
| v1.18.1 | Scheduled-from-stored-kickoff display derivation | Completed |
| v1.18.0 | Live Match Centre and factual sync-change visibility | Completed |

## Current limitations

- The application is self-hosted and local-first, not a production SaaS deployment.
- Provider coverage and payload quality determine available match detail.
- A stored empty event array does not prove a match had no goals, cards, or substitutions.
- Historical event correction/version storage is not implemented beyond v1.18+ sync change capture.
- Historical sync runs before v1.18 do not have a reconstructed change log.
- The Live Match Centre does not poll providers or certify real-time delivery.
- Freshness Context explains the age of the latest stored snapshot against the configured schedule; it does not guarantee that the next scheduled refresh will succeed or create a provider update.
- Scheduled-from-stored-kickoff is a display derivation for a future fixture with missing provider status; it never certifies provider scheduling or infers a live match.
- Incomplete statistics are hidden instead of normalised into misleading zero values.
- The official-video registry is empty until a controlled curator workflow adds individually verified match-specific links.
- Official video availability can be delayed, require sign-in or subscription, or vary by territory.
- Local Llama requires Ollama to be running on the Windows host.
- The Windows runtime scripts report Cloudflared and Ollama failure rather than blindly repairing sensitive host services.
- The default local stack does not implement production authentication or hardened secret management.

## Security notes

Keep all secrets local.

```text
Do not commit .env files, API keys, bot tokens, chat IDs,
Cloudflare credentials, or host-specific production settings.
```

## License

Personal portfolio and learning project.
