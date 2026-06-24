from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.fixture import Fixture
from app.models.match_detail import MatchDetail
from app.models.match_detail_event_coverage import MatchDetailEventCoverage
from app.services.provider_event_integrity import (
    canonicalize_card_events,
    canonicalize_goal_events,
    canonicalize_substitution_events,
)

EVENT_COVERAGE_AVAILABLE = "available"
EVENT_COVERAGE_NOT_PROVIDED = "not_provided"
_EVENT_COVERAGE_TYPES = ("goals", "cards", "substitutions")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_dict(value: Any) -> dict:
    return value.copy() if isinstance(value, dict) else {}


def _clean_text(value: Any, fallback: str | None = None) -> str | None:
    if value is None:
        return fallback

    cleaned = str(value).strip()
    return cleaned or fallback


def normalize_event_coverage(value: Any) -> dict[str, str]:
    """Normalize only explicit provider event-category availability metadata.

    A provider may explicitly return an empty list for a category; that is
    recorded as ``available``. Missing or non-list category payloads are kept
    as ``not_provided`` and are never treated as proof that no events occurred.
    """
    raw_coverage = value if isinstance(value, dict) else {}
    normalized: dict[str, str] = {}

    for event_type in _EVENT_COVERAGE_TYPES:
        raw_state = raw_coverage.get(event_type)
        state = str(raw_state or "").strip().casefold()
        normalized[event_type] = (
            EVENT_COVERAGE_AVAILABLE
            if state == EVENT_COVERAGE_AVAILABLE
            else EVENT_COVERAGE_NOT_PROVIDED
        )

    return normalized


def upsert_match_detail(
    db: Session,
    fixture: Fixture,
    detail_data: dict,
) -> MatchDetail:
    if fixture.id is None:
        db.flush()

    now = _utc_now_iso()
    item = {
        "provider": _clean_text(detail_data.get("provider"), "unknown"),
        "provider_match_id": _clean_text(detail_data.get("provider_match_id")),
        "goals": canonicalize_goal_events(detail_data.get("goals")),
        "cards": canonicalize_card_events(detail_data.get("cards")),
        "substitutions": canonicalize_substitution_events(
            detail_data.get("substitutions")
        ),
        "formations": _as_dict(detail_data.get("formations")),
        "lineups": _as_dict(detail_data.get("lineups")),
        "statistics": _as_dict(detail_data.get("statistics")),
        "referee": _as_dict(detail_data.get("referee")),
        "weather": _as_dict(detail_data.get("weather")),
        "updated_at": now,
    }

    existing_detail = (
        db.query(MatchDetail)
        .filter(MatchDetail.fixture_id == fixture.id)
        .first()
    )
    if existing_detail:
        for key, item_value in item.items():
            setattr(existing_detail, key, item_value)
        return existing_detail

    item["fixture_id"] = fixture.id
    item["created_at"] = now
    match_detail = MatchDetail(**item)
    db.add(match_detail)
    return match_detail


def upsert_match_detail_event_coverage(
    db: Session,
    fixture: Fixture,
    detail_data: dict,
) -> MatchDetailEventCoverage:
    """Store provider-declared event availability in an additive companion table."""
    if fixture.id is None:
        db.flush()

    now = _utc_now_iso()
    provider = _clean_text(detail_data.get("provider"), "unknown") or "unknown"
    coverage = normalize_event_coverage(detail_data.get("event_coverage"))

    existing_coverage = (
        db.query(MatchDetailEventCoverage)
        .filter(MatchDetailEventCoverage.fixture_id == fixture.id)
        .first()
    )
    if existing_coverage:
        existing_coverage.provider = provider
        existing_coverage.event_coverage = coverage
        existing_coverage.updated_at = now
        return existing_coverage

    event_coverage = MatchDetailEventCoverage(
        fixture_id=fixture.id,
        provider=provider,
        event_coverage=coverage,
        created_at=now,
        updated_at=now,
    )
    db.add(event_coverage)
    return event_coverage
