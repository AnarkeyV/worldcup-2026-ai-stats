"""Canonical handling for stored provider match events.

The helpers retain only event fields that the provider supplied. They never
infer assists, player identities, teams, event times, or unsupported facts.
"""

from __future__ import annotations

import re
from typing import Any, Callable

_EVENT_SIDE_VALUES = frozenset({"home", "away"})
_MINUTE_PATTERN = re.compile(r"^(?P<base>\d{1,3})(?:\+(?P<added>\d{1,3}))?$")


def canonicalize_goal_events(raw_events: Any) -> list[dict[str, Any]]:
    """Return usable goal events in stable chronological order."""

    return _canonicalize_events(raw_events, _build_goal_event)


def canonicalize_card_events(raw_events: Any) -> list[dict[str, Any]]:
    """Return usable card events in stable chronological order."""

    return _canonicalize_events(raw_events, _build_card_event)


def canonicalize_substitution_events(raw_events: Any) -> list[dict[str, Any]]:
    """Return usable substitution events in stable chronological order."""

    return _canonicalize_events(raw_events, _build_substitution_event)


def _canonicalize_events(
    raw_events: Any,
    event_builder: Callable[[Any], dict[str, Any] | None],
) -> list[dict[str, Any]]:
    if not isinstance(raw_events, list):
        return []

    canonical_events: list[dict[str, Any]] = []
    seen_event_keys: set[tuple[tuple[str, Any], ...]] = set()

    for raw_event in raw_events:
        event = event_builder(raw_event)
        if event is None:
            continue

        event_key = _event_identity_key(event)
        if event_key in seen_event_keys:
            continue

        seen_event_keys.add(event_key)
        canonical_events.append(event)

    return sorted(canonical_events, key=_event_sort_key)


def _build_goal_event(raw_event: Any) -> dict[str, Any] | None:
    if not isinstance(raw_event, dict):
        return None

    team = _normalize_event_side(raw_event.get("team"))
    scorer = _clean_text(raw_event.get("scorer"))

    if not team or not scorer:
        return None

    return {
        "minute": _normalize_minute(raw_event.get("minute")),
        "team": team,
        "scorer": scorer,
    }


def _build_card_event(raw_event: Any) -> dict[str, Any] | None:
    if not isinstance(raw_event, dict):
        return None

    team = _normalize_event_side(raw_event.get("team"))
    player = _clean_text(raw_event.get("player"))
    color = _clean_text(raw_event.get("color"))

    if not team or not player or not color:
        return None

    return {
        "minute": _normalize_minute(raw_event.get("minute")),
        "team": team,
        "player": player,
        "color": color.casefold(),
    }


def _build_substitution_event(raw_event: Any) -> dict[str, Any] | None:
    if not isinstance(raw_event, dict):
        return None

    team = _normalize_event_side(raw_event.get("team"))
    player_on = _clean_text(raw_event.get("on"))
    player_off = _clean_text(raw_event.get("off"))

    if not team or not player_on or not player_off:
        return None

    return {
        "minute": _normalize_minute(raw_event.get("minute")),
        "team": team,
        "on": player_on,
        "off": player_off,
    }


def _normalize_event_side(value: Any) -> str | None:
    normalized_value = _clean_text(value)
    if not normalized_value:
        return None

    side = normalized_value.casefold()
    if side not in _EVENT_SIDE_VALUES:
        return None

    return side


def _normalize_minute(value: Any) -> int | str | None:
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value

    normalized_value = _clean_text(value)
    if not normalized_value:
        return None

    try:
        return int(normalized_value)
    except ValueError:
        return normalized_value


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None

    cleaned_value = str(value).strip()
    if not cleaned_value:
        return None

    return cleaned_value


def _event_identity_key(event: dict[str, Any]) -> tuple[tuple[str, Any], ...]:
    return tuple(
        (field_name, _identity_value(value))
        for field_name, value in sorted(event.items(), key=lambda item: item[0])
    )


def _identity_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.casefold()

    return value


def _event_sort_key(event: dict[str, Any]) -> tuple[int, int, int, str]:
    return _minute_sort_key(event.get("minute"))


def _minute_sort_key(value: Any) -> tuple[int, int, int, str]:
    if isinstance(value, int) and not isinstance(value, bool):
        return (0, value, 0, "")

    if isinstance(value, str):
        match = _MINUTE_PATTERN.fullmatch(value)
        if match:
            return (
                0,
                int(match.group("base")),
                int(match.group("added") or 0),
                value.casefold(),
            )

        return (1, 999, 0, value.casefold())

    return (1, 999, 1, "")
