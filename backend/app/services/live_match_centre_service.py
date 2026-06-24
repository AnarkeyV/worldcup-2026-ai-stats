"""Read-only aggregation for the factual Live Match Centre API.

This service reads only stored application records. It does not call a provider,
trigger a sync, send notifications, or write to the database. A match is exposed
as live only when its already-normalized stored status is explicitly classified
as live by the Phase 1 contract.
"""

from __future__ import annotations
from datetime import datetime, timezone

from typing import Any

from sqlalchemy.orm import Session

from app.models.fixture import Fixture
from app.models.fixture_sync_change_set import FixtureSyncChangeSet
from app.models.fixture_sync_run import FixtureSyncRun
from app.models.match_detail import MatchDetail
from app.models.match_detail_event_coverage import MatchDetailEventCoverage
from app.services.live_match_contracts import (
    MATCH_STATE_COMPLETED,
    MATCH_STATE_LIVE,
    MATCH_STATE_SCHEDULED,
    MATCH_STATE_UNAVAILABLE,
    DISPLAY_STATE_SOURCE_STORED_KICKOFF,
    DISPLAY_STATE_SOURCE_STORED_STATUS,
    derive_fixture_display_state,
)
from app.services.sync_observability_service import get_fixture_sync_status

EVENT_TYPES = ("goals", "cards", "substitutions")
EVENT_COVERAGE_AVAILABLE = "available"
EVENT_COVERAGE_NOT_PROVIDED = "not_provided"
EVENT_COVERAGE_UNKNOWN = "coverage_unknown"
DETAIL_AVAILABLE = "available"
DETAIL_NOT_AVAILABLE = "detail_not_available"
REFRESH_RECORDED = "recorded"
REFRESH_HISTORICAL_NOT_RECORDED = "not_recorded_before_v1_18"
REFRESH_NOT_STARTED = "not_started"

SCHEDULED_SOURCE_PROVIDER_STATUS = "provider_status"
SCHEDULED_SOURCE_STORED_KICKOFF = "stored_kickoff"


def build_live_match_centre(db: Session) -> dict[str, Any]:
    """Build a provider-free view of the current stored live-match state."""
    fixtures = db.query(Fixture).order_by(Fixture.kickoff_time.asc(), Fixture.id.asc()).all()
    fixture_ids = [fixture.id for fixture in fixtures if fixture.id is not None]

    details_by_fixture_id = _details_by_fixture_id(db, fixture_ids)
    coverage_by_fixture_id = _coverage_by_fixture_id(db, fixture_ids)

    counts = {
        MATCH_STATE_LIVE: 0,
        MATCH_STATE_COMPLETED: 0,
        MATCH_STATE_SCHEDULED: 0,
        MATCH_STATE_UNAVAILABLE: 0,
    }
    live_matches: list[dict[str, Any]] = []
    scheduled_sources = {
        SCHEDULED_SOURCE_PROVIDER_STATUS: 0,
        SCHEDULED_SOURCE_STORED_KICKOFF: 0,
    }
    reference_time = _utc_now()

    for fixture in fixtures:
        display_state = derive_fixture_display_state(
            fixture.status,
            fixture.kickoff_time,
            fixture.home_score,
            fixture.away_score,
            now=reference_time,
        )
        match_state = display_state["match_state"]
        counts[match_state] += 1

        if match_state == MATCH_STATE_SCHEDULED:
            state_source = display_state["state_source"]
            if state_source == DISPLAY_STATE_SOURCE_STORED_STATUS:
                scheduled_sources[SCHEDULED_SOURCE_PROVIDER_STATUS] += 1
            elif state_source == DISPLAY_STATE_SOURCE_STORED_KICKOFF:
                scheduled_sources[SCHEDULED_SOURCE_STORED_KICKOFF] += 1

        if match_state != MATCH_STATE_LIVE:
            continue

        match_detail = details_by_fixture_id.get(fixture.id)
        event_coverage = coverage_by_fixture_id.get(fixture.id)
        live_matches.append(
            _serialize_live_match(
                fixture=fixture,
                match_detail=match_detail,
                event_coverage=event_coverage,
            )
        )

    sync_status = get_fixture_sync_status(db)
    latest_successful_run = _latest_successful_run(db)

    return {
        "data_freshness": _build_data_freshness(sync_status),
        "latest_successful_refresh": _build_latest_successful_refresh(
            db=db,
            latest_successful_run=latest_successful_run,
        ),
        "matches": live_matches,
        "counts": counts,
        "scheduled_sources": scheduled_sources,
    }


def _utc_now() -> datetime:
    """Return the single UTC reference time for one read-only response."""
    return datetime.now(timezone.utc)


def _details_by_fixture_id(
    db: Session,
    fixture_ids: list[int],
) -> dict[int, MatchDetail]:
    if not fixture_ids:
        return {}

    details = (
        db.query(MatchDetail)
        .filter(MatchDetail.fixture_id.in_(fixture_ids))
        .all()
    )
    return {detail.fixture_id: detail for detail in details}


def _coverage_by_fixture_id(
    db: Session,
    fixture_ids: list[int],
) -> dict[int, MatchDetailEventCoverage]:
    if not fixture_ids:
        return {}

    coverage_records = (
        db.query(MatchDetailEventCoverage)
        .filter(MatchDetailEventCoverage.fixture_id.in_(fixture_ids))
        .all()
    )
    return {coverage.fixture_id: coverage for coverage in coverage_records}


def _serialize_live_match(
    *,
    fixture: Fixture,
    match_detail: MatchDetail | None,
    event_coverage: MatchDetailEventCoverage | None,
) -> dict[str, Any]:
    return {
        "fixture_id": fixture.id,
        "external_id": fixture.external_id,
        "competition": fixture.competition,
        "stage": fixture.stage,
        "group_name": fixture.group_name,
        "home_team": fixture.home_team,
        "away_team": fixture.away_team,
        "home_team_code": fixture.home_team_code,
        "away_team_code": fixture.away_team_code,
        "status": fixture.status,
        "match_state": MATCH_STATE_LIVE,
        "home_score": fixture.home_score,
        "away_score": fixture.away_score,
        "kickoff_time": fixture.kickoff_time,
        "stored_fixture_updated_at": fixture.updated_at,
        "event_data": _build_event_data(match_detail, event_coverage),
    }


def _build_event_data(
    match_detail: MatchDetail | None,
    event_coverage: MatchDetailEventCoverage | None,
) -> dict[str, Any]:
    if match_detail is None:
        return {
            "availability": DETAIL_NOT_AVAILABLE,
            "provider": None,
            "stored_detail_updated_at": None,
            "event_coverage": {
                event_type: DETAIL_NOT_AVAILABLE for event_type in EVENT_TYPES
            },
        }

    raw_coverage = (
        event_coverage.event_coverage
        if event_coverage is not None and isinstance(event_coverage.event_coverage, dict)
        else None
    )
    return {
        "availability": DETAIL_AVAILABLE,
        "provider": match_detail.provider,
        "stored_detail_updated_at": match_detail.updated_at,
        "event_coverage": {
            event_type: _event_coverage_state(raw_coverage, event_type)
            for event_type in EVENT_TYPES
        },
    }


def _event_coverage_state(
    raw_coverage: dict[str, Any] | None,
    event_type: str,
) -> str:
    if raw_coverage is None:
        return EVENT_COVERAGE_UNKNOWN

    value = raw_coverage.get(event_type)
    if not isinstance(value, str):
        return EVENT_COVERAGE_UNKNOWN

    normalized = value.strip().casefold()
    if normalized == EVENT_COVERAGE_AVAILABLE:
        return EVENT_COVERAGE_AVAILABLE
    if normalized == EVENT_COVERAGE_NOT_PROVIDED:
        return EVENT_COVERAGE_NOT_PROVIDED
    return EVENT_COVERAGE_UNKNOWN


def _latest_successful_run(db: Session) -> FixtureSyncRun | None:
    return (
        db.query(FixtureSyncRun)
        .filter(FixtureSyncRun.status == "success")
        .order_by(FixtureSyncRun.id.desc())
        .first()
    )


def _build_latest_successful_refresh(
    *,
    db: Session,
    latest_successful_run: FixtureSyncRun | None,
) -> dict[str, Any]:
    if latest_successful_run is None:
        return {
            "availability": REFRESH_NOT_STARTED,
            "sync_run_id": None,
            "completed_at": None,
            "compared_fixture_count": 0,
            "changed_fixture_count": 0,
            "change_count": 0,
            "changes": [],
        }

    change_set = (
        db.query(FixtureSyncChangeSet)
        .filter(FixtureSyncChangeSet.sync_run_id == latest_successful_run.id)
        .first()
    )
    if change_set is None:
        return {
            "availability": REFRESH_HISTORICAL_NOT_RECORDED,
            "sync_run_id": latest_successful_run.id,
            "completed_at": latest_successful_run.completed_at,
            "compared_fixture_count": None,
            "changed_fixture_count": None,
            "change_count": None,
            "changes": [],
        }

    return {
        "availability": (
            change_set.capture_state
            if str(change_set.capture_state or "").strip()
            else REFRESH_RECORDED
        ),
        "sync_run_id": latest_successful_run.id,
        "completed_at": latest_successful_run.completed_at,
        "compared_fixture_count": change_set.compared_fixture_count,
        "changed_fixture_count": change_set.changed_fixture_count,
        "change_count": change_set.total_change_count,
        "changes": list(change_set.changes or []),
    }


def _build_data_freshness(sync_status: dict[str, Any]) -> dict[str, Any]:
    freshness = sync_status.get("freshness")
    freshness = freshness if isinstance(freshness, dict) else {}
    state = str(freshness.get("state") or "unavailable")

    return {
        "state": state,
        "last_success_at": sync_status.get("last_success_at"),
        "data_age_seconds": freshness.get("data_age_seconds"),
        "fresh_after_seconds": freshness.get("fresh_after_seconds"),
        "stale_after_seconds": freshness.get("stale_after_seconds"),
        "message": _freshness_message(state),
    }


def _freshness_message(state: str) -> str:
    messages = {
        "fresh": "Stored provider snapshot is fresh.",
        "aging": "Stored provider snapshot is aging.",
        "stale": "Stored provider snapshot is stale.",
        "last_sync_failed": (
            "The latest provider refresh failed; displayed data is from the last "
            "successful stored snapshot."
        ),
        "not_started": "No successful provider snapshot has been stored yet.",
        "unavailable": "Stored provider freshness cannot be determined.",
    }
    return messages.get(state, "Stored provider freshness cannot be determined.")
