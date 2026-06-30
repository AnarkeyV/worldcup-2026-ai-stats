# Official Match Video Curation

## Purpose

This is a manual, evidence-first process for adding a verified outbound official
match video to World Cup 2026 AI Stats. The dashboard does not search YouTube,
scrape pages, follow redirects, embed footage, download footage, or write a
record through a public HTTP endpoint.

## Source policy

`mediacorp_sports_youtube` is restricted to a **direct YouTube video URL** from
the official `@SportsMediacorp` channel. A direct `/watch?v=...` URL does not
prove its uploader by itself, so the curator must verify the channel manually
before storing a record.

Accepted content types:

- `highlights`
- `full_match` — shown in the dashboard as **Full-match replay**
- `recap`

The default territory is `region_dependent`. Do not call a video global unless
that availability is directly evidenced.

## Required evidence gates

Before any database write, confirm all of the following:

1. The local fixture has resolved team names and a stored stage/status.
2. The exact video is visible on the official `@SportsMediacorp` channel.
3. The video title, thumbnail, and description together support the fixture
   association. Both teams must be identifiable; stage and score should also
   align where the source provides them.
4. The URL is a direct HTTPS video link:
   `https://www.youtube.com/watch?v=<video-id>` or an accepted Shorts URL.
   Do not store channel pages, search results, playlists, third-party mirrors,
   downloads, or embeds.
5. `content_type`, territory, `published_at` (when visible), and `verified_at`
   are recorded honestly.
6. A second review is completed before production data is changed.

## Example record shape — review only

This is an illustrative payload, not an import command and not a live record.

```json
{
  "fixture_id": 77,
  "source_key": "mediacorp_sports_youtube",
  "content_type": "highlights",
  "title": "<exact official video title>",
  "external_url": "https://www.youtube.com/watch?v=<verified-video-id>",
  "territory": "region_dependent",
  "is_match_specific": true,
  "published_at": "<ISO-8601 time when visible>",
  "verified_at": "<ISO-8601 curator review time>"
}
```

No production database write should occur until the fixture/video association,
published time, and approved write procedure have been separately reviewed.
