from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.fixture import Fixture
from app.models.match_detail import MatchDetail
from app.models.match_detail_event_coverage import MatchDetailEventCoverage
from app.services.live_match_contracts import (
    COMPARISON_AVAILABLE,
    build_fixture_change_summary,
)
from app.services.match_detail_sync_service import (
    upsert_match_detail,
    upsert_match_detail_event_coverage,
)

COMPLETED_STATUSES = {
    "complete",
    "completed",
    "finished",
    "final",
    "ft",
    "full-time",
    "full_time",
    "match finished",
    "aet",
    "pen",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_status(status: Any) -> str:
    if status is None:
        return ""

    return str(status).strip().lower()


def _is_completed_status(status: Any) -> bool:
    return _normalize_status(status) in COMPLETED_STATUSES


def _clean_external_id(value: Any) -> str:
    if value is None:
        raise ValueError("Fixture external_id is required.")

    external_id = str(value).strip()
    if not external_id:
        raise ValueError("Fixture external_id is required.")

    return external_id


def _fixture_snapshot(fixture: Fixture | None) -> dict[str, Any] | None:
    if fixture is None:
        return None

    return {
        "external_id": fixture.external_id,
        "status": fixture.status,
        "home_score": fixture.home_score,
        "away_score": fixture.away_score,
    }


def _match_detail_snapshot(
    match_detail: MatchDetail | None,
    event_coverage: MatchDetailEventCoverage | None,
) -> dict[str, Any] | None:
    if match_detail is None:
        return None

    return {
        "goals": deepcopy(match_detail.goals or []),
        "cards": deepcopy(match_detail.cards or []),
        "substitutions": deepcopy(match_detail.substitutions or []),
        "event_coverage": (
            deepcopy(event_coverage.event_coverage or {})
            if event_coverage is not None
            else None
        ),
    }


def _read_detail_snapshot(
    db: Session,
    fixture_id: int | None,
) -> dict[str, Any] | None:
    if fixture_id is None:
        return None

    match_detail = (
        db.query(MatchDetail)
        .filter(MatchDetail.fixture_id == fixture_id)
        .first()
    )
    if match_detail is None:
        return None

    event_coverage = (
        db.query(MatchDetailEventCoverage)
        .filter(MatchDetailEventCoverage.fixture_id == fixture_id)
        .first()
    )
    return _match_detail_snapshot(match_detail, event_coverage)


def _record_changed_fixture_summary(
    summaries: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    """Retain only factual deltas; first observations remain intentionally absent."""
    if summary.get("comparison_status") != COMPARISON_AVAILABLE:
        return

    changes = summary.get("changes")
    if not isinstance(changes, list) or not changes:
        return

    summaries.append(deepcopy(summary))


def sync_fixtures(db: Session, fixtures: list[dict]) -> dict:
    """Create or update provider fixtures and capture factual stored-state deltas.

    The returned change summaries are internal run data. They are persisted only
    after the caller creates the terminal successful sync-audit record, allowing
    the companion change set to reference that exact run. This function makes no
    provider call, does not send notifications, and does not alter scheduler
    behaviour.
    """
    created = 0
    updated = 0
    newly_completed = []
    compared_fixture_count = 0
    change_summaries: list[dict[str, Any]] = []
    now = _utc_now_iso()

    for fixture_data in fixtures:
        item = fixture_data.copy()
        match_detail_data = item.pop("match_detail", None)
        external_id = _clean_external_id(item.get("external_id"))
        item["external_id"] = external_id

        existing_fixture = (
            db.query(Fixture)
            .filter(Fixture.external_id == external_id)
            .first()
        )
        previous_fixture = _fixture_snapshot(existing_fixture)
        previous_detail = (
            _read_detail_snapshot(db, existing_fixture.id)
            if existing_fixture is not None
            else None
        )

        previous_status = existing_fixture.status if existing_fixture else None
        new_status = item.get("status")
        was_completed = _is_completed_status(previous_status)
        is_completed = _is_completed_status(new_status)

        item.setdefault("created_at", now)
        item["updated_at"] = now

        if existing_fixture:
            item.pop("created_at", None)
            for key, value in item.items():
                setattr(existing_fixture, key, value)
            fixture_record = existing_fixture

            if not was_completed and is_completed:
                newly_completed.append(external_id)
            updated += 1
        else:
            fixture_record = Fixture(**item)
            db.add(fixture_record)
            db.flush()
            created += 1

            if is_completed:
                newly_completed.append(external_id)

        current_detail = None
        if isinstance(match_detail_data, dict):
            match_detail = upsert_match_detail(
                db=db,
                fixture=fixture_record,
                detail_data=match_detail_data,
            )
            event_coverage = upsert_match_detail_event_coverage(
                db=db,
                fixture=fixture_record,
                detail_data=match_detail_data,
            )
            current_detail = _match_detail_snapshot(match_detail, event_coverage)

        summary = build_fixture_change_summary(
            previous_fixture,
            _fixture_snapshot(fixture_record) or {},
            previous_detail=previous_detail,
            current_detail=current_detail,
        )
        if previous_fixture is not None:
            compared_fixture_count += 1
        _record_changed_fixture_summary(change_summaries, summary)

    db.commit()

    return {
        "created": created,
        "updated": updated,
        "total_fixtures": len(fixtures),
        "newly_completed": newly_completed,
        "newly_completed_count": len(newly_completed),
        "compared_fixture_count": compared_fixture_count,
        "change_summaries": change_summaries,
    }
