# World Cup 2026 AI Stats

![Version](https://img.shields.io/badge/version-v1.17.0-purple)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Database](https://img.shields.io/badge/database-PostgreSQL-336791)
![AI](https://img.shields.io/badge/AI-Ollama%20%2B%20Local%20Llama-green)
![Notifications](https://img.shields.io/badge/notifications-Telegram-lightblue)
![Monitoring](https://img.shields.io/badge/monitoring-Prometheus%20%2B%20Grafana-orange)

A self-hosted World Cup 2026 intelligence dashboard for provider-backed fixtures, match storytelling, transparent stored-data coverage, standings, player event leaders, local AI summaries, Telegram alerts, and runtime observability.

**Public dashboard**

```text
https://wc2026.khairulrizal.qzz.io/dashboard
```

**Current release**

```text
v1.17.0 — Provider-Backed Match Story and Official Watch
```

**Release verification**

```text
234 automated tests passed
```

---

## Why This Project Exists

World Cup 2026 AI Stats is a local-first football analytics project built as a practical DevOps, backend, automation, observability, and AI portfolio system.

It is designed to answer useful matchday questions without pretending the available data is richer than it is:

- Which fixtures are complete, live, or upcoming?
- What is the provider-backed sequence of goals, cards, and substitutions in a completed match?
- Can a score progression be shown safely from stored goal records?
- Which team statistics are actually comparable for both teams?
- Which players are leading in goals, yellow cards, and red cards?
- Who currently occupies the top two positions in each group?
- Can an official match-video destination be linked safely without scraping, embedding unknown content, or bypassing territory restrictions?
- Can a local model provide summaries without a paid cloud LLM?
- Can the system be operated from a Windows home runtime while development stays on a MacBook?

The project is intentionally self-hosted, provider-backed, explainable, and safe to demo.

---

## Current Release: v1.17.0

### Provider-Backed Match Story and Official Watch

v1.17.0 turns stored match detail into a more useful match narrative while retaining the project’s local-read and no-invention boundaries.

It adds:

- `GET /fixtures/{fixture_id}/story`, a computed read-only route derived only from local `Fixture`, `MatchDetail`, and approved outbound-video records
- a **Story** tab in the existing match-detail panel, alongside Timeline, Stats, and Lineups
- a score-progression sequence only when stored goal events reconcile exactly with the stored final score
- a chronological key-event flow for goals, cards, substitutions, and valid stoppage-time values
- paired-stat rendering that hides incomplete metrics instead of turning missing provider values into `0` or a false 50:50 bar
- visible provider, provider-match-ID, and stored-detail-refresh provenance
- an **Official Highlights / Watch** area using server-vetted outbound links only
- no-video-yet and region-dependent states, including official FIFA and meWATCH coverage-hub fallbacks
- a small local `official_match_videos` registry for future manually verified match-specific links

The release does not scrape websites, search platforms, download or rehost video, bypass territory restrictions, embed third-party players, trigger provider work, alter scheduled sync behaviour, or send Telegram messages.

**Release verification**

```text
234 automated tests passed
```

---

## Architecture at a Glance

```text
MacBook Pro
VS Code + Python venv + Git
        |
        | git push / SSH control
        v
Windows Laptop Runtime Host
Docker Desktop + Docker Compose
        |
        |-- FastAPI backend + static dashboard
        |-- PostgreSQL
        |-- Prometheus
        |-- Grafana
        |-- Cloudflare Tunnel
        |-- Telegram test and scheduled digest integration
        |-- Ollama on the Windows host
        |
        +--> Public mobile dashboard
             https://wc2026.khairulrizal.qzz.io/dashboard
```

External integrations:

```text
Zafronix Provider API  --->  FastAPI backend  --->  PostgreSQL
Telegram Bot API       <---  manual notifications and scheduled digests
Cloudflare Tunnel      --->  public dashboard URL
Ollama                <---  local AI health and summaries
Prometheus            <---  backend metrics
Grafana               <---  dashboard visualization
```

Read the detailed design in [docs/architecture.md](docs/architecture.md).

---

## Core Capabilities

### Match Story and Data Provenance

The match story is intentionally a **derived local view**, not a live commentary feed.

| Story element | Requirement before it is shown |
|---|---|
| Score progression | Fixture scores exist; every stored goal has a usable minute and a valid side; stored home/away goal counts reconcile with the final score. |
| Key-event timeline | Stored valid goal, card, or substitution records exist. Untimed events are retained but are shown without a fabricated minute. |
| Match-stat comparison | Both teams have a finite provider value for the same metric. |
| Official Watch card | A locally stored, manually verified, match-specific record passes the source, URL, content-type, territory, and verification checks. |

Each story response includes the stored provider name, provider match identifier, and local stored-detail timestamp. A missing section is represented as unavailable or partial rather than filled with a guess.

### Fixture and Provider Data

The backend stores competition, stage, group, teams, kickoff time, venue, status, score, provider external ID, timestamps, and optional rich match detail.

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/fixtures` | List and filter fixtures |
| `GET` | `/fixtures/data-quality` | Read aggregate stored match-detail coverage |
| `GET` | `/fixtures/{fixture_id}` | Read one fixture |
| `GET` | `/fixtures/{fixture_id}/detail` | Read raw locally stored rich detail |
| `GET` | `/fixtures/{fixture_id}/story` | Read computed local match story and official-watch state |
| `POST` | `/fixtures/sync/sample` | Seed deterministic sample fixtures |
| `POST` | `/fixtures/sync/provider` | Sync configured provider data |
| `GET` | `/fixtures/sync/status` | Read latest persisted sync state |
| `GET` | `/fixtures/sync/history` | Read recent persisted sync-run history |

Both match-detail routes are read-only. Neither calls a provider, starts a backfill, sends a message, or changes the scheduler.

### Official Highlights / Watch Policy

v1.17.0 treats video as a trusted outbound destination, not hosted content.

The initial server allow-list supports only:

- FIFA web destinations on approved FIFA hosts
- exact, manually verified FIFA YouTube video URLs
- meWATCH destinations on approved meWATCH hosts

A link is rejected unless it is HTTPS, uses an approved source key and host, has an allowed content type, is marked match-specific, and includes a curator verification timestamp. Links open externally with `target="_blank"` and `rel="noopener noreferrer"`.

The dashboard may show official FIFA and meWATCH coverage hubs when no verified match-specific link has been added. Those hubs are clearly labelled as fallbacks; they are not claimed to be a specific match’s video.

The current release does **not** include automatic web discovery, search-result harvesting, a public write route, a video embed, thumbnail proxying, fan uploads, or a bypass for region locks. Official availability can be delayed or territory-dependent.

### Provider Event Integrity

Stored rich-event arrays remain factual provider records. The canonical event layer:

- accepts only supported event shapes
- normalises `home` and `away` side values
- keeps the dedicated event-minute field separate from player text
- removes exact normalised duplicates
- preserves valid untimed entries without inventing a minute
- sorts valid timed events chronologically, including stoppage-time values such as `45+2`
- protects provider leaderboards and latest-result summaries from duplicate or malformed stored arrays

An empty stored event array means only that the latest stored provider payload contains no such records. It does not prove that no event occurred.

### Visual Matchday Experience

The dashboard prioritises an at-a-glance matchday view before deeper operational detail:

- visual cards select the most relevant live, completed, and upcoming fixtures from the stored fixture response
- the Data health badge reuses the existing local-only coverage result and does not start sync or contact a provider
- player and Group Race bars are descriptive comparisons, not predictions
- the match-detail Story view is a factual local reading of provider-backed data
- the mobile bottom navigation links only to existing page sections and does not create a separate mobile application

### Standings, Player Leaders, and Local AI

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

The project does not infer assists when the provider does not supply assist events. Structured AI Insights and Group Race do not depend on Ollama availability.

### Fixed-Time Provider Sync and Telegram Digest

Scheduled matchday automation remains explicit and opt-in.

- `PROVIDER_SYNC_SCHEDULER_ENABLED` controls the fixed-time provider scheduler.
- Default slots remain `03:45`, `09:45`, and `12:45` in `Asia/Singapore`.
- The scheduler waits for the next future configured slot after startup or restart; it does not run an automatic catch-up sync.
- `TELEGRAM_SCHEDULED_DIGEST_ENABLED` separately controls scheduled notification delivery.
- The existing manual-sync per-fixture alert policy remains separate and disabled by default.

v1.17.0 does not change these settings or their runtime behaviour.

---

## Development and Runtime Workflow

| Machine | Role |
|---|---|
| MacBook Pro | Main development, tests, Git control, and package review |
| Windows laptop | Docker runtime and demo host |
| VS Code | Main editor |
| Python venv | Local test environment |
| SSH | Remote runtime verification after release approval |

### MacBook Development

```bash
cd ~/documents/worldcup-2026-ai-stats/backend
source .venv/bin/activate
python -m pytest -q
cd ..
git status --short
git diff --check
```

Do not run Docker on the MacBook.

### Windows Runtime

After merge and explicit runtime-deployment approval, use Windows PowerShell:

```powershell
cd "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats"
docker compose ps
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/fixtures/sync/status
```

Do not modify the active `.env` directly. Use the existing candidate → non-secret validation → timestamped backup → promote → verify workflow when configuration changes are approved.

---

## Configuration and Secrets

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

The v1.17.0 release changes only the safe version placeholder in `.env.example`. It does not create, replace, or expose an active `.env` file.

---

## Testing

Run the full suite from `backend`:

```bash
python -m pytest -q
```

Useful focused checks:

```bash
python -m pytest -q \
  tests/test_match_story_service.py \
  tests/test_match_story_routes.py \
  tests/test_official_match_video_service.py \
  tests/test_match_story_dashboard.py \
  tests/test_release_workflow.py \
  tests/test_dashboard.py
```

Release verification history:

```text
v1.12.0: 196 passed
v1.13.0: 202 passed
v1.14.0: 205 passed
v1.15.0: 209 passed
v1.16.0: 218 passed
v1.17.0: 234 passed
```

Python 3.14 may emit FastAPI/Starlette deprecation warnings related to `asyncio.iscoroutinefunction`. They remain warnings, not failing tests, in the current suite.

---

## Release Workflow

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

---

## Documentation

- [Architecture](docs/architecture.md)
- [Changelog](docs/changelog.md)
- [Roadmap](docs/roadmap.md)
- [Demo Walkthrough](docs/demo-walkthrough.md)
- [v1.17.0 Release Notes](docs/v1.17.0-match-story-official-watch.md)
- [Portfolio Release Summary](docs/portfolio-release.md)

---

## Milestone History

| Version | Milestone | Status |
|---|---|---|
| v0.1.0 | Project foundation | Completed |
| v0.2.0 | Fixture and API foundation | Completed |
| v0.3.0 | Provider abstraction | Completed |
| v0.4.0 | Match completion detection | Completed |
| v0.5.0 | Telegram notifications | Completed |
| v0.6.0 | Interactive dashboard | Completed |
| v0.7.0 | Fixture filters and dashboard polish | Completed |
| v0.8.0 | Local Llama summary agent | Completed |
| v1.1.0 | Group standings engine | Completed |
| v1.4.0 | Monitoring and observability foundation | Completed |
| v1.4.1 | Grafana dashboard polish | Completed |
| v1.4.2 | Telegram live-integration hardening | Completed |
| v1.4.3 | Documentation and demo-evidence cleanup | Completed |
| v1.5.0 | Portfolio release polish | Completed |
| v1.6.0 | Real match-data sync improvement | Completed |
| v1.7.0 | Provider sync observability and runtime demo | Completed |
| v1.8.0 | AI insights upgrade | Completed |
| v1.9.0 | Live local AI, Telegram, Cloudflare, and Windows runtime resilience | Completed |
| v1.10.0 | Match detail dashboard and README polish | Completed |
| v1.11.0 | Mobile rich match dashboard, provider leaders, and Group Race | Completed |
| v1.12.0 | Safe matchday sync, audit history, and data freshness | Completed |
| v1.13.0 | Provider event integrity and stored detail coverage | Completed |
| v1.14.0 | Match data quality dashboard | Completed |
| v1.15.0 | Visual Matchday UX and charts | Completed |
| v1.16.0 | Fixed-time scheduled sync and Telegram digest | Completed |
| v1.17.0 | Provider-backed match story and official watch | Completed |

---

## Current Limitations

- The application is self-hosted and local-first, not a production SaaS deployment.
- Provider coverage and payload quality determine available match detail.
- A stored empty event array does not prove a match had no goals, cards, or substitutions.
- Score progression is intentionally unavailable when stored goal events do not reconcile with the stored final score.
- Incomplete statistics are hidden instead of normalised into misleading zero values.
- The official-video registry is empty until a future controlled curator workflow adds individually verified match-specific links.
- Official video availability may be delayed, require sign-in or subscription, or vary by territory.
- The release does not embed third-party video, proxy thumbnails, or implement automatic official-video discovery.
- Historical event-correction/version storage and provider event IDs are not implemented.
- Assist leaderboards remain unavailable until the provider supplies assist events.
- Local Llama requires Ollama to be running on the Windows host.
- The default local stack does not implement production authentication or hardened secret management.
- Dashboard data is a stored provider snapshot and changes after future approved syncs.
- Fixed-time provider sync and scheduled Telegram digest delivery remain configured separately and are not changed by this release.

---

## Security Notes

Keep all secrets local. This repository should contain safe placeholders only.

```text
Do not commit .env files, API keys, bot tokens, chat IDs, Cloudflare credentials,
or host-specific production settings.
```

---

## License

Personal portfolio and learning project.
