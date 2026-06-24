"""Build a read-only, provider-backed match story from stored match detail.

This module intentionally does not call a provider, write to the database, or
infer events that are absent from the stored fixture and match-detail records.
It is designed to be used by a future read-only match-story route.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any


_STORY_METRICS = (
    {
        "key": "possessionPct",
        "label": "Possession",
        "unit": "percent",
    },
    {
        "key": "shotsTotal",
        "label": "Shots",
        "unit": "count",
    },
    {
        "key": "shotsOnGoal",
        "label": "Shots on target",
        "unit": "count",
    },
    {
        "key": "expectedGoals",
        "label": "Expected goals",
        "unit": "decimal",
    },
    {
        "key": "passesAccurate",
        "label": "Accurate passes",
        "unit": "count",
    },
    {
        "key": "corners",
        "label": "Corners",
        "unit": "count",
    },
    {
        "key": "fouls",
        "label": "Fouls",
        "unit": "count",
    },
)

_MINUTE_PATTERN = re.compile(r"^(?P<base>\d{1,3})(?:\+(?P<added>\d{1,3}))?$")
_EVENT_KIND_ORDER = {
    "goal": 0,
    "card": 1,
    "substitution": 2,
}


def build_match_story(fixture: Any, match_detail: Any | None) -> dict[str, Any]:
    """Return a conservative match-story contract from stored local data only.

    ``fixture`` and ``match_detail`` may be SQLAlchemy model instances, mapping
    objects, or simple namespaces. The result does not mutate either input.
    """

    source = _build_source(match_detail)

    if match_detail is None:
        return {
            "state": "unavailable",
            "source": source,
            "score_progression": _unavailable_section(
                "No stored provider match detail is available for this fixture."
            ),
            "timeline": _unavailable_section(
                "No stored provider event timeline is available for this fixture."
            ),
            "statistics": _unavailable_statistics(
                "No stored provider match statistics are available for this fixture."
            ),
        }

    goals = _as_list(_read_value(match_detail, "goals", []))
    cards = _as_list(_read_value(match_detail, "cards", []))
    substitutions = _as_list(_read_value(match_detail, "substitutions", []))

    score_progression = _build_score_progression(fixture, goals)
    timeline = _build_timeline(goals, cards, substitutions)
    statistics = _build_statistics(_read_value(match_detail, "statistics", {}))

    return {
        "state": _derive_story_state(score_progression, timeline, statistics),
        "source": source,
        "score_progression": score_progression,
        "timeline": timeline,
        "statistics": statistics,
    }


def _build_source(match_detail: Any | None) -> dict[str, Any]:
    return {
        "mode": "stored_provider_match_detail",
        "detail_available": match_detail is not None,
        "provider": _clean_text(_read_value(match_detail, "provider"))
        if match_detail is not None
        else None,
        "provider_match_id": _clean_text(
            _read_value(match_detail, "provider_match_id")
        )
        if match_detail is not None
        else None,
        "stored_detail_updated_at": _clean_text(
            _read_value(match_detail, "updated_at")
        )
        if match_detail is not None
        else None,
    }


def _build_score_progression(fixture: Any, goals: list[Any]) -> dict[str, Any]:
    home_score = _as_non_negative_int(_read_value(fixture, "home_score"))
    away_score = _as_non_negative_int(_read_value(fixture, "away_score"))

    if home_score is None or away_score is None:
        return _unavailable_section("Fixture score is not available.")

    valid_goals: list[dict[str, Any]] = []

    for goal in goals:
        if not isinstance(goal, Mapping):
            return _unavailable_section(
                "Stored goal events are incomplete and cannot support score progression."
            )

        team = _event_team(goal)
        minute = goal.get("minute")

        if team is None:
            return _unavailable_section(
                "Stored goal events are incomplete and cannot support score progression."
            )

        if not _is_usable_minute(minute):
            return _unavailable_section(
                "At least one stored goal is missing a usable minute."
            )

        valid_goals.append(
            {
                "minute": minute,
                "team": team,
                "scorer": _clean_text(goal.get("scorer")),
            }
        )

    home_goal_count = sum(goal["team"] == "home" for goal in valid_goals)
    away_goal_count = sum(goal["team"] == "away" for goal in valid_goals)

    if home_goal_count != home_score or away_goal_count != away_score:
        return _unavailable_section(
            "Stored goal events do not reconcile with the fixture score."
        )

    ordered_goals = sorted(valid_goals, key=lambda goal: _minute_sort_key(goal["minute"]))
    running_home_score = 0
    running_away_score = 0
    events: list[dict[str, Any]] = []

    for goal in ordered_goals:
        if goal["team"] == "home":
            running_home_score += 1
        else:
            running_away_score += 1

        events.append(
            {
                "minute": goal["minute"],
                "team": goal["team"],
                "scorer": goal["scorer"],
                "home_score": running_home_score,
                "away_score": running_away_score,
            }
        )

    return {
        "state": "available",
        "reason": None,
        "events": events,
    }


def _build_timeline(
    goals: list[Any],
    cards: list[Any],
    substitutions: list[Any],
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []

    for goal in goals:
        if not isinstance(goal, Mapping):
            continue

        team = _event_team(goal)
        if team is None:
            continue

        events.append(
            {
                "kind": "goal",
                "minute": goal.get("minute"),
                "team": team,
                "scorer": _clean_text(goal.get("scorer")),
            }
        )

    for card in cards:
        if not isinstance(card, Mapping):
            continue

        team = _event_team(card)
        color = _clean_text(card.get("color"))
        if team is None or color is None:
            continue

        events.append(
            {
                "kind": "card",
                "minute": card.get("minute"),
                "team": team,
                "player": _clean_text(card.get("player")),
                "color": color.casefold(),
            }
        )

    for substitution in substitutions:
        if not isinstance(substitution, Mapping):
            continue

        team = _event_team(substitution)
        if team is None:
            continue

        events.append(
            {
                "kind": "substitution",
                "minute": substitution.get("minute"),
                "team": team,
                "player_on": _clean_text(substitution.get("on")),
                "player_off": _clean_text(substitution.get("off")),
            }
        )

    if not events:
        return _unavailable_section(
            "No stored provider event timeline is available for this fixture."
        )

    ordered_events = sorted(
        events,
        key=lambda event: (
            _minute_sort_key(event.get("minute")),
            _EVENT_KIND_ORDER[event["kind"]],
        ),
    )

    return {
        "state": "available",
        "reason": None,
        "events": ordered_events,
    }


def _build_statistics(raw_statistics: Any) -> dict[str, Any]:
    statistics = raw_statistics if isinstance(raw_statistics, Mapping) else {}
    home_statistics = statistics.get("home")
    away_statistics = statistics.get("away")

    home_statistics = home_statistics if isinstance(home_statistics, Mapping) else {}
    away_statistics = away_statistics if isinstance(away_statistics, Mapping) else {}

    metrics: list[dict[str, Any]] = []
    incomplete_metric_keys: list[str] = []

    for metric in _STORY_METRICS:
        key = metric["key"]
        home_value = _as_finite_number(home_statistics.get(key))
        away_value = _as_finite_number(away_statistics.get(key))

        if home_value is not None and away_value is not None:
            metrics.append(
                {
                    "key": key,
                    "label": metric["label"],
                    "unit": metric["unit"],
                    "home": home_value,
                    "away": away_value,
                }
            )
        elif home_value is not None or away_value is not None:
            incomplete_metric_keys.append(key)

    if not metrics:
        return _unavailable_statistics(
            "No comparable provider statistics are stored for both teams."
        )

    return {
        "state": "partial" if incomplete_metric_keys else "available",
        "reason": (
            "Only statistics supplied for both teams are shown."
            if incomplete_metric_keys
            else None
        ),
        "metrics": metrics,
        "incomplete_metric_keys": incomplete_metric_keys,
    }


def _derive_story_state(
    score_progression: Mapping[str, Any],
    timeline: Mapping[str, Any],
    statistics: Mapping[str, Any],
) -> str:
    if (
        score_progression.get("state") == "available"
        and timeline.get("state") == "available"
        and statistics.get("state") == "available"
    ):
        return "available"

    if any(
        section.get("state") in {"available", "partial"}
        for section in (score_progression, timeline, statistics)
    ):
        return "partial"

    return "unavailable"


def _unavailable_section(reason: str) -> dict[str, Any]:
    return {
        "state": "unavailable",
        "reason": reason,
        "events": [],
    }


def _unavailable_statistics(reason: str) -> dict[str, Any]:
    return {
        "state": "unavailable",
        "reason": reason,
        "metrics": [],
        "incomplete_metric_keys": [],
    }


def _read_value(source: Any | None, key: str, default: Any = None) -> Any:
    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(key, default)

    return getattr(source, key, default)


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _event_team(event: Mapping[str, Any]) -> str | None:
    team = _clean_text(event.get("team"))
    if team is None:
        return None

    normalized_team = team.casefold()
    return normalized_team if normalized_team in {"home", "away"} else None


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    return text or None


def _as_non_negative_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value if value >= 0 else None

    return None


def _as_finite_number(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return value if math.isfinite(value) else None

    if isinstance(value, str):
        normalized_value = value.strip()
        if not normalized_value:
            return None

        try:
            numeric_value = float(normalized_value)
        except ValueError:
            return None

        if not math.isfinite(numeric_value):
            return None

        return int(numeric_value) if numeric_value.is_integer() else numeric_value

    return None


def _is_usable_minute(value: Any) -> bool:
    if isinstance(value, bool):
        return False

    if isinstance(value, int):
        return value >= 0

    if isinstance(value, str):
        return _MINUTE_PATTERN.fullmatch(value.strip()) is not None

    return False


def _minute_sort_key(value: Any) -> tuple[int, int, int, str]:
    if isinstance(value, int) and not isinstance(value, bool):
        return (0, value, 0, "")

    if isinstance(value, str):
        normalized_value = value.strip()
        match = _MINUTE_PATTERN.fullmatch(normalized_value)
        if match:
            return (
                0,
                int(match.group("base")),
                int(match.group("added") or 0),
                normalized_value.casefold(),
            )

        return (1, 999, 0, normalized_value.casefold())

    return (1, 999, 1, "")
