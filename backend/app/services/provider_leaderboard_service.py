from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

from app.services.standings_service import COMPLETED_STATUSES


GOAL_SCORER_TRAILING_ANNOTATION_PATTERN = re.compile(
    r"\s+\d{1,3}(?:\+\d{1,3})?[\'’]?(?:\s+(?:pen|penalty))?\s*$",
    re.IGNORECASE,
)


def clean_goal_scorer_name(value: Any) -> str:
    """
    Keep player names separate from a provider's embedded goal annotation.

    Some Zafronix goal strings contain the event minute and penalty note inside
    the scorer field, for example ``Havertz 45+5' pen``. The minute already
    exists as structured event data, so the leaderboard and match summary use
    the cleaned name while retaining the minute in its dedicated field.
    """
    source_name = str(value or "").replace("\u00a0", " ").strip()

    return GOAL_SCORER_TRAILING_ANNOTATION_PATTERN.sub("", source_name).strip()



def get_value(record: Any, field_name: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(field_name, default)

    return getattr(record, field_name, default)


def normalize_status(fixture: Any) -> str:
    return str(get_value(fixture, "status", "") or "").strip().lower()


def is_completed_fixture(fixture: Any) -> bool:
    return normalize_status(fixture) in COMPLETED_STATUSES


def build_provider_player_leaderboards(
    fixtures: list[Any],
    match_details: list[Any],
) -> dict[str, Any]:
    """
    Build real player leaderboards from stored provider match details.

    The current Zafronix match-detail payload exposes goal and card events, but
    not assists. The response therefore makes assists explicitly unavailable
    rather than inventing values or reusing sample player data.
    """
    details_by_fixture_id = {
        get_value(detail, "fixture_id"): detail
        for detail in match_details
        if get_value(detail, "fixture_id") is not None
    }

    player_rows: dict[tuple[str, str], dict[str, Any]] = {}
    completed_fixture_count = 0
    detailed_fixture_count = 0

    for fixture in fixtures:
        if not is_completed_fixture(fixture):
            continue

        completed_fixture_count += 1
        fixture_id = get_value(fixture, "id")
        detail = details_by_fixture_id.get(fixture_id)

        if detail is None:
            continue

        detailed_fixture_count += 1
        _aggregate_goal_events(
            player_rows=player_rows,
            fixture=fixture,
            events=get_value(detail, "goals", []) or [],
        )
        _aggregate_card_events(
            player_rows=player_rows,
            fixture=fixture,
            events=get_value(detail, "cards", []) or [],
        )

    rows = list(player_rows.values())

    return {
        "provider": _get_provider_name(match_details),
        "source": "provider_backed_match_details",
        "coverage": {
            "completed_fixture_count": completed_fixture_count,
            "detailed_fixture_count": detailed_fixture_count,
        },
        "assist_data": {
            "available": False,
            "message": (
                "Assist leaders are unavailable because the current provider "
                "match-detail payload does not include assist events."
            ),
        },
        "leaderboards": {
            "top_scorers": _sort_rows(rows, "goals"),
            "yellow_card_leaders": _sort_rows(rows, "yellow_cards"),
            "red_card_leaders": _sort_rows(rows, "red_cards"),
        },
    }


def build_latest_completed_match_summary(
    fixtures: list[Any],
    match_details: list[Any],
) -> dict[str, Any] | None:
    """
    Build a deterministic latest-result summary.

    When provider events are available, a red-card incident is placed before
    the result and scorers. When only fixture-level data exists, the response
    stays factual and reports the completed score without fabricated events.
    """
    completed_fixtures = [
        fixture for fixture in fixtures
        if is_completed_fixture(fixture)
    ]

    if not completed_fixtures:
        return None

    latest_fixture = max(completed_fixtures, key=_fixture_sort_key)
    details_by_fixture_id = {
        get_value(detail, "fixture_id"): detail
        for detail in match_details
        if get_value(detail, "fixture_id") is not None
    }
    detail = details_by_fixture_id.get(get_value(latest_fixture, "id"))

    red_cards = _build_card_events(latest_fixture, detail, color="red")
    goals = _build_goal_events(latest_fixture, detail)

    summary_parts = []

    if red_cards:
        summary_parts.append(
            "Major incident: "
            f"{_format_card_event(red_cards[0])}."
        )

    summary_parts.append(_build_result_sentence(latest_fixture))

    if goals:
        summary_parts.append(
            f"Scorers: {_format_goal_scorers(goals)}."
        )

    return {
        "fixture": _serialize_fixture_reference(latest_fixture),
        "detail_available": detail is not None,
        "provider": (
            str(get_value(detail, "provider", "") or "").strip()
            if detail is not None
            else "fixture_data"
        ),
        "summary": " ".join(summary_parts),
        "major_incidents": red_cards,
        "goals": goals,
    }


def _aggregate_goal_events(
    player_rows: dict[tuple[str, str], dict[str, Any]],
    fixture: Any,
    events: list[Any],
) -> None:
    for event in events:
        if not isinstance(event, dict):
            continue

        raw_scorer = str(event.get("scorer") or "").strip()
        source_name = clean_goal_scorer_name(raw_scorer)

        if not source_name or _is_own_goal(raw_scorer):
            continue

        team, team_code = _resolve_team_context(fixture, event.get("team"))

        if not team:
            continue

        row = _get_or_create_player_row(
            player_rows=player_rows,
            source_name=source_name,
            team=team,
            team_code=team_code,
            group_name=get_value(fixture, "group_name"),
        )
        row["goals"] += 1


def _aggregate_card_events(
    player_rows: dict[tuple[str, str], dict[str, Any]],
    fixture: Any,
    events: list[Any],
) -> None:
    for event in events:
        if not isinstance(event, dict):
            continue

        source_name = str(event.get("player") or "").strip()
        color = str(event.get("color") or "").strip().lower()

        if not source_name or not color:
            continue

        team, team_code = _resolve_team_context(fixture, event.get("team"))

        if not team:
            continue

        row = _get_or_create_player_row(
            player_rows=player_rows,
            source_name=source_name,
            team=team,
            team_code=team_code,
            group_name=get_value(fixture, "group_name"),
        )

        if "red" in color:
            row["red_cards"] += 1
        elif "yellow" in color:
            row["yellow_cards"] += 1


def _get_or_create_player_row(
    player_rows: dict[tuple[str, str], dict[str, Any]],
    source_name: str,
    team: str,
    team_code: str | None,
    group_name: str | None,
) -> dict[str, Any]:
    key = (source_name.casefold(), team.casefold())

    return player_rows.setdefault(
        key,
        {
            "player_name": source_name,
            "team": team,
            "team_code": team_code,
            "group_name": group_name,
            "goals": 0,
            "yellow_cards": 0,
            "red_cards": 0,
        },
    )


def _build_goal_events(fixture: Any, detail: Any | None) -> list[dict[str, Any]]:
    if detail is None:
        return []

    goals = []

    for event in get_value(detail, "goals", []) or []:
        if not isinstance(event, dict):
            continue

        raw_scorer = str(event.get("scorer") or "").strip()
        scorer = clean_goal_scorer_name(raw_scorer)
        team, team_code = _resolve_team_context(fixture, event.get("team"))

        if not scorer or not team:
            continue

        goals.append(
            {
                "minute": event.get("minute"),
                "team": team,
                "team_code": team_code,
                "scorer": scorer,
                "own_goal": _is_own_goal(raw_scorer),
            }
        )

    return sorted(goals, key=_event_sort_key)


def _build_card_events(
    fixture: Any,
    detail: Any | None,
    color: str | None = None,
) -> list[dict[str, Any]]:
    if detail is None:
        return []

    cards = []

    for event in get_value(detail, "cards", []) or []:
        if not isinstance(event, dict):
            continue

        event_color = str(event.get("color") or "").strip().lower()

        if color and color not in event_color:
            continue

        player = str(event.get("player") or "").strip()
        team, team_code = _resolve_team_context(fixture, event.get("team"))

        if not player or not team:
            continue

        cards.append(
            {
                "minute": event.get("minute"),
                "team": team,
                "team_code": team_code,
                "player": player,
                "color": event_color,
            }
        )

    return sorted(cards, key=_event_sort_key)


def _build_result_sentence(fixture: Any) -> str:
    home_team = str(get_value(fixture, "home_team", "Home Team") or "Home Team")
    away_team = str(get_value(fixture, "away_team", "Away Team") or "Away Team")
    home_score = get_value(fixture, "home_score")
    away_score = get_value(fixture, "away_score")
    group_name = str(get_value(fixture, "group_name", "") or "").strip()
    group_suffix = f" in {group_name}" if group_name else ""

    if home_score is None or away_score is None:
        return f"{home_team} vs {away_team} is complete{group_suffix}, but the final score is unavailable."

    if home_score > away_score:
        return f"{home_team} beat {away_team} {home_score}-{away_score}{group_suffix}."

    if away_score > home_score:
        return f"{away_team} beat {home_team} {away_score}-{home_score}{group_suffix}."

    return f"{home_team} drew {away_team} {home_score}-{away_score}{group_suffix}."


def _format_goal_scorers(goals: list[dict[str, Any]]) -> str:
    entries = [
        f"{goal['scorer']} ({_format_minute(goal.get('minute'))})"
        for goal in goals
    ]

    return _join_readable(entries)


def _format_card_event(card: dict[str, Any]) -> str:
    return (
        f"{card['player']} received a red card for {card['team']} "
        f"in the {_format_minute(card.get('minute'))}"
    )


def _serialize_fixture_reference(fixture: Any) -> dict[str, Any]:
    return {
        "id": get_value(fixture, "id"),
        "group_name": get_value(fixture, "group_name"),
        "home_team": get_value(fixture, "home_team"),
        "away_team": get_value(fixture, "away_team"),
        "home_score": get_value(fixture, "home_score"),
        "away_score": get_value(fixture, "away_score"),
        "status": get_value(fixture, "status"),
        "kickoff_time": get_value(fixture, "kickoff_time"),
    }


def _resolve_team_context(
    fixture: Any,
    event_team: Any,
) -> tuple[str | None, str | None]:
    normalized_side = str(event_team or "").strip().lower()

    if normalized_side == "home":
        return (
            get_value(fixture, "home_team"),
            get_value(fixture, "home_team_code"),
        )

    if normalized_side == "away":
        return (
            get_value(fixture, "away_team"),
            get_value(fixture, "away_team_code"),
        )

    return None, None


def _sort_rows(rows: list[dict[str, Any]], metric_name: str) -> list[dict[str, Any]]:
    return sorted(
        [row for row in rows if int(row.get(metric_name, 0)) > 0],
        key=lambda row: (
            -int(row.get(metric_name, 0)),
            -int(row.get("goals", 0)),
            row.get("player_name") or "",
            row.get("team") or "",
        ),
    )


def _get_provider_name(match_details: list[Any]) -> str:
    providers = {
        str(get_value(detail, "provider", "") or "").strip()
        for detail in match_details
        if str(get_value(detail, "provider", "") or "").strip()
    }

    if len(providers) == 1:
        return next(iter(providers))

    if providers:
        return "mixed"

    return "unavailable"


def _fixture_sort_key(fixture: Any) -> tuple[datetime, int]:
    kickoff_time = get_value(fixture, "kickoff_time")
    parsed = _parse_datetime(kickoff_time)
    fixture_id = int(get_value(fixture, "id", 0) or 0)

    return parsed, fixture_id


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        try:
            parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            parsed = datetime.min.replace(tzinfo=timezone.utc)
    else:
        parsed = datetime.min.replace(tzinfo=timezone.utc)

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def _event_sort_key(event: dict[str, Any]) -> tuple[int, str]:
    minute = event.get("minute")

    if isinstance(minute, int):
        return minute, ""

    value = str(minute or "").strip()
    digits = "".join(character for character in value if character.isdigit())

    return int(digits or 999), value


def _format_minute(value: Any) -> str:
    minute = str(value or "").strip()

    if not minute:
        return "an unspecified minute"

    return f"{minute}'"


def _is_own_goal(value: Any) -> bool:
    normalized = str(value or "").strip().lower()

    return "o.g." in normalized or "own goal" in normalized


def _join_readable(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return f"{', '.join(items[:-1])}, and {items[-1]}"
