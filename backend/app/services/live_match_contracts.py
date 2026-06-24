"""Pure contracts for factual live-match state and stored snapshot deltas.

This module is intentionally read-only and provider-agnostic. It classifies only
already-normalized, stored fixture statuses and compares only supplied stored
snapshots. It never calls a provider, performs a sync, sends notifications, or
writes to the database.

Event deltas are emitted only when both snapshots explicitly state that the
relevant provider event category was available. Legacy detail records without
coverage metadata remain explicit as ``coverage_unknown`` rather than being
interpreted as an empty provider event feed.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from app.services.provider_event_integrity import (
    canonicalize_card_events,
    canonicalize_goal_events,
    canonicalize_substitution_events,
)

MATCH_STATE_LIVE = "live"
MATCH_STATE_COMPLETED = "completed"
MATCH_STATE_SCHEDULED = "scheduled"
MATCH_STATE_UNAVAILABLE = "unavailable"

COMPARISON_AVAILABLE = "available"
COMPARISON_BASELINE_UNAVAILABLE = "baseline_unavailable"

EVENT_COMPARISON_AVAILABLE = "available"
EVENT_COMPARISON_BASELINE_UNAVAILABLE = "baseline_unavailable"
EVENT_COMPARISON_PREVIOUS_DETAIL_MISSING = "previous_detail_missing"
EVENT_COMPARISON_CURRENT_DETAIL_MISSING = "current_detail_missing"
EVENT_COMPARISON_COVERAGE_UNKNOWN = "coverage_unknown"
EVENT_COMPARISON_NOT_PROVIDED = "not_provided"

EVENT_COVERAGE_AVAILABLE = "available"
EVENT_COVERAGE_NOT_PROVIDED = "not_provided"

# These are normalized application statuses, not raw provider status codes.
# API-Football currently maps known in-progress statuses to ``live`` and known
# finished statuses to ``complete`` before the sync service receives them.
_LIVE_STATUSES = frozenset({"live"})
_COMPLETED_STATUSES = frozenset(
    {
        "complete",
        "completed",
        "finished",
        "final",
        "ft",
        "full time",
        "match finished",
        "aet",
        "pen",
    }
)
_SCHEDULED_STATUSES = frozenset({"scheduled", "not started", "ns"})

_EVENT_SPECS: tuple[tuple[str, str, Callable[[Any], list[dict[str, Any]]]], ...] = (
    ("goals", "goal_added", canonicalize_goal_events),
    ("cards", "card_added", canonicalize_card_events),
    ("substitutions", "substitution_added", canonicalize_substitution_events),
)


def normalize_stored_status(status: Any) -> str:
    """Normalize a stored status for conservative comparison only."""
    if status is None:
        return ""

    normalized = str(status).strip().casefold()
    normalized = normalized.replace("_", " ").replace("-", " ")
    return " ".join(normalized.split())


def classify_stored_match_status(status: Any) -> str:
    """Return a factual match state from an already-stored provider status.

    Only explicitly recognized normalized values are promoted to live,
    completed, or scheduled. Every other value—including postponed, cancelled,
    abandoned, missing, and future unsupported values—remains unavailable.
    """
    normalized = normalize_stored_status(status)

    if normalized in _LIVE_STATUSES:
        return MATCH_STATE_LIVE
    if normalized in _COMPLETED_STATUSES:
        return MATCH_STATE_COMPLETED
    if normalized in _SCHEDULED_STATUSES:
        return MATCH_STATE_SCHEDULED
    return MATCH_STATE_UNAVAILABLE


def build_fixture_change_summary(
    previous_fixture: Mapping[str, Any] | None,
    current_fixture: Mapping[str, Any],
    *,
    previous_detail: Mapping[str, Any] | None = None,
    current_detail: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a concise, factual delta between two already-stored snapshots.

    The function intentionally emits no changes for a first observation because
    there is no stored prior state to compare. It emits event additions only
    where both detail snapshots explicitly mark that event category as provider
    available. Event removals or edits become a neutral revision marker instead
    of a potentially misleading new-event claim.
    """
    external_id = _first_text(
        current_fixture.get("external_id"),
        previous_fixture.get("external_id") if previous_fixture else None,
    )

    if previous_fixture is None:
        return {
            "external_id": external_id,
            "comparison_status": COMPARISON_BASELINE_UNAVAILABLE,
            "event_comparison": _event_comparison_map(
                EVENT_COMPARISON_BASELINE_UNAVAILABLE
            ),
            "changes": [],
        }

    changes = _fixture_changes(previous_fixture, current_fixture)
    event_comparison: dict[str, str] = {}

    for event_type, change_type, canonicalize in _EVENT_SPECS:
        comparison_status = _event_comparison_status(
            previous_detail,
            current_detail,
            event_type,
        )
        event_comparison[event_type] = comparison_status

        if comparison_status != EVENT_COMPARISON_AVAILABLE:
            continue

        changes.extend(
            _event_changes(
                event_type=event_type,
                change_type=change_type,
                previous_events=canonicalize(previous_detail.get(event_type)),
                current_events=canonicalize(current_detail.get(event_type)),
            )
        )

    return {
        "external_id": external_id,
        "comparison_status": COMPARISON_AVAILABLE,
        "event_comparison": event_comparison,
        "changes": changes,
    }


def _fixture_changes(
    previous_fixture: Mapping[str, Any],
    current_fixture: Mapping[str, Any],
) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []

    previous_score = _score_pair(previous_fixture)
    current_score = _score_pair(current_fixture)
    if (
        previous_score is not None
        and current_score is not None
        and previous_score != current_score
    ):
        changes.append(
            {
                "type": "score_changed",
                "before": _score_payload(previous_score),
                "after": _score_payload(current_score),
            }
        )

    previous_status = _display_status(previous_fixture.get("status"))
    current_status = _display_status(current_fixture.get("status"))
    previous_normalized = normalize_stored_status(previous_status)
    current_normalized = normalize_stored_status(current_status)

    if (
        previous_normalized
        and current_normalized
        and previous_normalized != current_normalized
    ):
        changes.append(
            {
                "type": "status_changed",
                "before": previous_status,
                "after": current_status,
            }
        )

        if (
            classify_stored_match_status(previous_status) != MATCH_STATE_COMPLETED
            and classify_stored_match_status(current_status) == MATCH_STATE_COMPLETED
        ):
            changes.append(
                {
                    "type": "match_completed",
                    "status": current_status,
                }
            )

    return changes


def _event_comparison_status(
    previous_detail: Mapping[str, Any] | None,
    current_detail: Mapping[str, Any] | None,
    event_type: str,
) -> str:
    if previous_detail is None:
        return EVENT_COMPARISON_PREVIOUS_DETAIL_MISSING
    if current_detail is None:
        return EVENT_COMPARISON_CURRENT_DETAIL_MISSING

    previous_coverage = _event_coverage(previous_detail, event_type)
    current_coverage = _event_coverage(current_detail, event_type)

    if (
        previous_coverage == EVENT_COVERAGE_NOT_PROVIDED
        or current_coverage == EVENT_COVERAGE_NOT_PROVIDED
    ):
        return EVENT_COMPARISON_NOT_PROVIDED

    if (
        previous_coverage != EVENT_COVERAGE_AVAILABLE
        or current_coverage != EVENT_COVERAGE_AVAILABLE
    ):
        return EVENT_COMPARISON_COVERAGE_UNKNOWN

    return EVENT_COMPARISON_AVAILABLE


def _event_coverage(detail: Mapping[str, Any], event_type: str) -> str | None:
    coverage = detail.get("event_coverage")
    if not isinstance(coverage, Mapping):
        return None

    value = coverage.get(event_type)
    if not isinstance(value, str):
        return None

    normalized = value.strip().casefold()
    if normalized == EVENT_COVERAGE_AVAILABLE:
        return EVENT_COVERAGE_AVAILABLE
    if normalized == EVENT_COVERAGE_NOT_PROVIDED:
        return EVENT_COVERAGE_NOT_PROVIDED
    return None


def _event_changes(
    *,
    event_type: str,
    change_type: str,
    previous_events: list[dict[str, Any]],
    current_events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    previous_keys = {_event_key(event) for event in previous_events}
    current_keys = {_event_key(event) for event in current_events}
    removed_keys = previous_keys - current_keys

    if removed_keys:
        return [
            {
                "type": "provider_event_record_revised",
                "event_type": event_type,
                "previous_count": len(previous_events),
                "current_count": len(current_events),
            }
        ]

    return [
        {
            "type": change_type,
            "event": event,
        }
        for event in current_events
        if _event_key(event) not in previous_keys
    ]


def _event_key(event: Mapping[str, Any]) -> tuple[tuple[str, Any], ...]:
    return tuple(
        (field_name, _identity_value(value))
        for field_name, value in sorted(event.items(), key=lambda item: item[0])
    )


def _identity_value(value: Any) -> Any:
    return value.casefold() if isinstance(value, str) else value


def _score_pair(fixture: Mapping[str, Any]) -> tuple[int, int] | None:
    home_score = fixture.get("home_score")
    away_score = fixture.get("away_score")

    if (
        not isinstance(home_score, int)
        or isinstance(home_score, bool)
        or not isinstance(away_score, int)
        or isinstance(away_score, bool)
    ):
        return None

    return home_score, away_score


def _score_payload(score: tuple[int, int]) -> dict[str, int]:
    return {"home": score[0], "away": score[1]}


def _display_status(status: Any) -> str | None:
    if status is None:
        return None

    value = str(status).strip()
    return value or None


def _first_text(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue
        cleaned = str(value).strip()
        if cleaned:
            return cleaned
    return None


def _event_comparison_map(status: str) -> dict[str, str]:
    return {event_type: status for event_type, _, _ in _EVENT_SPECS}
