"""Build trusted, outbound-only official match-video link cards.

The service never searches third-party platforms, scrapes pages, downloads or
rehosts video, follows redirects, or makes HTTP requests. It reads only local
records that a later controlled workflow has manually verified.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any
from urllib.parse import parse_qs, urlparse


SOURCE_POLICY_VERSION = "v1.17.0"

# This intentionally contains a narrow initial allow-list. In particular,
# generic YouTube, team, broadcaster, and sports-news links are not accepted.
# New sources must be explicitly researched, reviewed, and added here first.
_OFFICIAL_SOURCE_POLICY = {
    "fifa_web": {
        "source_name": "FIFA",
        "allowed_hosts": frozenset(
            {
                "fifa.com",
                "www.fifa.com",
                "plus.fifa.com",
                "vod.fifa.com",
            }
        ),
        "default_territory": "global",
        "allowed_content_types": frozenset(
            {"highlights", "full_match", "live", "recap"}
        ),
        "youtube": False,
    },
    "fifa_youtube": {
        "source_name": "FIFA on YouTube",
        "allowed_hosts": frozenset({"youtube.com", "www.youtube.com"}),
        "default_territory": "global",
        "allowed_content_types": frozenset(
            {"highlights", "full_match", "live", "recap"}
        ),
        "youtube": True,
    },
    "mediacorp_mewatch": {
        "source_name": "meWATCH",
        "allowed_hosts": frozenset({"mewatch.sg", "www.mewatch.sg"}),
        "default_territory": "singapore",
        "allowed_content_types": frozenset(
            {"highlights", "full_match", "live", "recap"}
        ),
        "youtube": False,
    },
}

_TERRITORY_DETAILS = {
    "global": {
        "label": "Global",
        "note": "Availability may still vary by territory.",
    },
    "singapore": {
        "label": "Singapore",
        "note": "Singapore availability; sign-in or subscription may apply.",
    },
    "region_dependent": {
        "label": "Region dependent",
        "note": "Availability depends on the viewer's territory.",
    },
}

_FALLBACK_LINKS = (
    {
        "source_key": "fifa_highlights_hub",
        "source_name": "FIFA",
        "title": "FIFA World Cup 2026 highlights",
        "content_type": "coverage_hub",
        "url": "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/highlights",
        "territory": "Global",
        "territory_note": "Availability may still vary by territory.",
        "is_match_specific": False,
        "external": True,
        "link_target": "_blank",
        "link_rel": "noopener noreferrer",
    },
    {
        "source_key": "mediacorp_mewatch_hub",
        "source_name": "meWATCH",
        "title": "FIFA World Cup 2026 on meWATCH",
        "content_type": "coverage_hub",
        "url": "https://www.mewatch.sg/fifaworldcup",
        "territory": "Singapore",
        "territory_note": "Singapore availability; sign-in or subscription may apply.",
        "is_match_specific": False,
        "external": True,
        "link_target": "_blank",
        "link_rel": "noopener noreferrer",
    },
)


def build_official_watch(records: Iterable[Any] | None) -> dict[str, Any]:
    """Return only validated, locally stored official outbound links.

    A record must be match-specific, include a curator verification timestamp,
    use one of the narrow source keys above, and satisfy that source's URL and
    content-type policy. Invalid records are silently omitted so a corrupted
    database row cannot produce an unsafe dashboard link.
    """

    links: list[dict[str, Any]] = []
    seen_links: set[tuple[str, str]] = set()

    for record in records or []:
        normalized = _normalize_official_video(record)
        if normalized is None:
            continue

        link_key = (normalized["source_key"], normalized["url"])
        if link_key in seen_links:
            continue

        seen_links.add(link_key)
        links.append(normalized)

    links.sort(
        key=lambda link: (
            link["source_name"].casefold(),
            link["title"].casefold(),
            link["url"],
        )
    )

    if not links:
        return {
            "state": "not_available_yet",
            "reason": "No verified match-specific official video is available yet.",
            "message": "Official video availability may be delayed or vary by territory.",
            "source_policy": "manual_verified_outbound_links_only",
            "source_policy_version": SOURCE_POLICY_VERSION,
            "links": [],
            "fallback_links": [link.copy() for link in _FALLBACK_LINKS],
        }

    territories = {link["territory"] for link in links}
    only_region_limited = territories.issubset({"Singapore", "Region dependent"})

    if only_region_limited:
        state = "region_dependent"
        message = "Verified official video is available, but access is region-dependent."
    elif len(territories) > 1 or "Singapore" in territories or "Region dependent" in territories:
        state = "available"
        message = "Verified official match video is available. Some links may be region-dependent."
    else:
        state = "available"
        message = "Verified official match video is available."

    return {
        "state": state,
        "reason": None,
        "message": message,
        "source_policy": "manual_verified_outbound_links_only",
        "source_policy_version": SOURCE_POLICY_VERSION,
        "links": links,
        "fallback_links": [link.copy() for link in _FALLBACK_LINKS],
    }


def _normalize_official_video(record: Any) -> dict[str, Any] | None:
    source_key = _clean_text(_read_value(record, "source_key"))
    if source_key is None:
        return None

    policy = _OFFICIAL_SOURCE_POLICY.get(source_key)
    if policy is None:
        return None

    title = _clean_text(_read_value(record, "title"))
    content_type = _normalize_content_type(_read_value(record, "content_type"))
    verified_at = _clean_text(_read_value(record, "verified_at"))

    if not title or not content_type or not verified_at:
        return None

    if content_type not in policy["allowed_content_types"]:
        return None

    if _read_value(record, "is_match_specific") is not True:
        return None

    url = _normalize_url(_read_value(record, "external_url"), policy)
    if url is None:
        return None

    territory_key = _normalize_territory(_read_value(record, "territory"))
    if territory_key is None:
        territory_key = policy["default_territory"]

    territory = _TERRITORY_DETAILS[territory_key]
    published_at = _clean_text(_read_value(record, "published_at"))

    return {
        "source_key": source_key,
        "source_name": policy["source_name"],
        "title": title,
        "content_type": content_type,
        "url": url,
        "territory": territory["label"],
        "territory_note": territory["note"],
        "is_match_specific": True,
        "published_at": published_at,
        "verified_at": verified_at,
        "external": True,
        "link_target": "_blank",
        "link_rel": "noopener noreferrer",
    }


def _normalize_url(value: Any, policy: Mapping[str, Any]) -> str | None:
    raw_url = _clean_text(value)
    if raw_url is None:
        return None

    try:
        parsed = urlparse(raw_url)
        _ = parsed.port
    except ValueError:
        return None

    if parsed.scheme.casefold() != "https":
        return None

    if parsed.username is not None or parsed.password is not None:
        return None

    host = (parsed.hostname or "").casefold()
    if host not in policy["allowed_hosts"]:
        return None

    if not parsed.path or parsed.path == "/":
        return None

    if policy["youtube"] and not _is_supported_youtube_video_url(parsed):
        return None

    return raw_url


def _is_supported_youtube_video_url(parsed) -> bool:
    path = parsed.path.rstrip("/")

    if path == "/watch":
        video_ids = parse_qs(parsed.query).get("v", [])
        return len(video_ids) == 1 and _is_youtube_video_id(video_ids[0])

    if path.startswith("/shorts/"):
        video_id = path.removeprefix("/shorts/")
        return "/" not in video_id and _is_youtube_video_id(video_id)

    return False


def _is_youtube_video_id(value: str) -> bool:
    return 1 <= len(value) <= 32 and all(
        character.isalnum() or character in {"-", "_"}
        for character in value
    )


def _normalize_content_type(value: Any) -> str | None:
    cleaned = _clean_text(value)
    if cleaned is None:
        return None

    normalized = cleaned.casefold().replace("-", "_").replace(" ", "_")
    return normalized or None


def _normalize_territory(value: Any) -> str | None:
    cleaned = _clean_text(value)
    if cleaned is None:
        return None

    normalized = cleaned.casefold().replace("-", "_").replace(" ", "_")
    return normalized if normalized in _TERRITORY_DETAILS else None


def _read_value(value: Any, field_name: str) -> Any:
    if isinstance(value, Mapping):
        return value.get(field_name)

    return getattr(value, field_name, None)


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None

    cleaned = str(value).strip()
    return cleaned or None
