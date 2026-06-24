# Demo Walkthrough

## v1.18.0 — Live Match Centre & Data Freshness

This walkthrough demonstrates the v1.18.0 source behaviour without presenting stored data as a live provider feed.

Use the public dashboard only after an approved runtime deployment:

```text
https://wc2026.khairulrizal.qzz.io/dashboard
```

For local development or API inspection:

```text
/dashboard
/docs
/live-match-centre
```

## Demo objective

Show how the project answers matchday questions using only stored/provider-backed data:

- Which fixtures are explicitly stored as live?
- How fresh is the latest successful stored snapshot?
- What factual changes were captured during the latest v1.18+ successful refresh?
- What event detail is available, not supplied, unknown, or absent?
- How does the dashboard remain useful when data is delayed or incomplete?

## Suggested flow

### 1. Open Matchday

Open the dashboard and begin in **Matchday**.

Explain that the dashboard presents a local stored snapshot. It does not contact the provider simply because a visitor opens the page.

Point out the Live Match Centre:

- fixtures appear there only when their stored status explicitly maps to `live`;
- visible scores are stored fixture values;
- local update timestamps identify when the application record was last updated;
- event availability is shown only when stored provider detail supports it.

### 2. Explain the freshness state

Show the freshness wording and status badge.

Use this explanation:

```text
Freshness describes the age of the latest successful stored provider snapshot.
It does not certify real-time provider delivery.
```

Possible states include:

| State | Meaning |
|---|---|
| `fresh` | Latest successful stored snapshot is within the configured fresh threshold |
| `aging` | Snapshot is older than fresh but not yet stale |
| `stale` | Snapshot is older than the configured stale threshold |
| `last_sync_failed` | The latest recorded sync failed; an older successful snapshot may still exist |
| `not_started` | No successful stored provider snapshot exists yet |

Do not claim that a fixture is live merely because its kickoff time is near or because the dashboard was opened recently.

### 3. Show “What changed?”

Navigate to **Provider Sync Runtime** and show **What changed?**

Explain that this view is derived from persisted v1.18+ sync change sets, not from guessed commentary.

Potential factual entries:

- score changed;
- stored status changed;
- match completed;
- goal added;
- card added;
- substitution added;
- provider event record revised.

If the dashboard shows `not_recorded_before_v1_18`, say:

```text
This historical sync completed before change capture was introduced,
so the application does not pretend it knows what changed.
```

If the dashboard shows zero changes, say:

```text
No provider-backed change was recorded in that successful refresh.
```

### 4. Open a match detail

Use the existing **Open match** / fixture selection interaction.

The Match Story, Timeline, Stats, Lineups, and Official Watch flow remain unchanged.

Highlight that:

- event records come from stored provider detail;
- missing event categories are explicit;
- score progression appears only when stored goal records reconcile with the stored score;
- incomplete paired statistics are omitted instead of normalised to zero;
- official links are outbound-only and manually verified.

### 5. Show an unavailable or incomplete state

When available in the stored data, show a fixture whose status or detail is incomplete.

Explain:

```text
Unknown, postponed, cancelled, abandoned, or unsupported statuses are
shown as unavailable rather than being silently treated as upcoming.

An empty stored event list does not prove that no event happened.
```

This is a deliberate product boundary, not an error state to hide.

### 6. Verify the API contract

Open:

```text
/live-match-centre
```

Use it to show the read-only response fields:

- `data_freshness`;
- `latest_successful_refresh`;
- `matches`;
- `counts`;
- per-match event-data availability;
- recorded or historical change-capture availability.

Do not invoke provider sync during this demo. The route is safe to read because it uses only local data.

## Demonstration boundaries

Do not claim or do any of the following:

- do not call the data real-time unless the provider’s stored delivery contract actually proves it;
- do not describe a missing event as “no event occurred”;
- do not invent a minute, player, assist, card, or substitution;
- do not use a fake live timeline;
- do not trigger provider sync, Telegram, or scheduler actions merely to populate the screen;
- do not scrape or embed third-party video;
- do not alter Windows `.env`, Cloudflared, Ollama, Docker, or Scheduled Tasks during a source-only demonstration.

## Post-release runtime verification

After GitHub merge, tag, release, and separate approval, use the read-only Windows status checker:

```powershell
cd "C:\Users\Khairul Rizal\Documents\worldcup-2026-ai-stats"
.\scripts\windows\get-worldcup-runtime-status.ps1
```

The status checker is not a deployment command. It does not rebuild containers, run provider sync, send Telegram, start/restart Cloudflared, or start/stop Ollama.
