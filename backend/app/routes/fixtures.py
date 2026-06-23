from datetime import datetime, timezone
import time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.fixture import Fixture
from app.models.match_detail import MatchDetail
from app.providers.api_football import ApiFootballProviderError
from app.providers.factory import get_configured_football_provider
from app.providers.zafronix import ZafronixProviderError
from app.services.fixture_sync_service import sync_fixtures
from app.services.metrics_service import (
    record_fixture_sync_metrics,
    record_notification_result,
)
from app.services.sample_data import SAMPLE_FIXTURES
from app.services.sync_observability_service import (
    get_fixture_sync_status,
    list_fixture_sync_runs,
    record_fixture_sync_status,
    sanitize_sync_error,
)
from app.services.telegram_notifier import (
    TelegramNotificationError,
    send_completed_fixture_notifications,
)

router = APIRouter(
    prefix="/fixtures",
    tags=["fixtures"],
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def serialize_fixture(fixture: Fixture) -> dict:
    return {
        "id": fixture.id,
        "external_id": fixture.external_id,
        "competition": fixture.competition,
        "stage": fixture.stage,
        "group_name": fixture.group_name,
        "home_team": fixture.home_team,
        "away_team": fixture.away_team,
        "home_team_code": fixture.home_team_code,
        "away_team_code": fixture.away_team_code,
        "kickoff_time": fixture.kickoff_time,
        "venue": fixture.venue,
        "status": fixture.status,
        "home_score": fixture.home_score,
        "away_score": fixture.away_score,
        "created_at": fixture.created_at,
        "updated_at": fixture.updated_at,
    }


def serialize_match_detail(match_detail: MatchDetail) -> dict:
    return {
        "id": match_detail.id,
        "fixture_id": match_detail.fixture_id,
        "provider": match_detail.provider,
        "provider_match_id": match_detail.provider_match_id,
        "goals": match_detail.goals or [],
        "cards": match_detail.cards or [],
        "substitutions": match_detail.substitutions or [],
        "formations": match_detail.formations or {},
        "lineups": match_detail.lineups or {},
        "statistics": match_detail.statistics or {},
        "referee": match_detail.referee or {},
        "weather": match_detail.weather or {},
        "created_at": match_detail.created_at,
        "updated_at": match_detail.updated_at,
    }


def _build_unavailable_event_coverage(event_label: str) -> dict:
    return {
        "state": "unavailable",
        "count": None,
        "message": (
            f"{event_label.capitalize()} event coverage is unavailable because no "
            "stored provider detail exists."
        ),
    }


def _build_stored_event_type_coverage(
    event_label: str,
    raw_events: object,
) -> dict:
    event_count = len(raw_events) if isinstance(raw_events, list) else 0

    if event_count == 0:
        return {
            "state": "no_stored_events",
            "count": 0,
            "message": (
                f"No stored {event_label} events are present in the last provider "
                "payload. This does not confirm that none occurred."
            ),
        }

    event_word = "event" if event_count == 1 else "events"
    return {
        "state": "recorded",
        "count": event_count,
        "message": (
            f"{event_count} stored {event_label} {event_word} "
            "are available in the last provider payload."
            if event_count != 1
            else (
                f"{event_count} stored {event_label} event "
                "is available in the last provider payload."
            )
        ),
    }


def build_stored_event_coverage(match_detail: MatchDetail | None) -> dict:
    """
    Describe only the stored provider event payload for one fixture.

    This is read-only coverage metadata. It does not trigger a provider request,
    infer missing events, or claim a provider payload is match-complete.
    """
    if match_detail is None:
        return {
            "detail_state": "unavailable",
            "provider": None,
            "stored_detail_updated_at": None,
            "event_types": {
                "goals": _build_unavailable_event_coverage("goal"),
                "cards": _build_unavailable_event_coverage("card"),
                "substitutions": _build_unavailable_event_coverage(
                    "substitution"
                ),
            },
            "message": (
                "No stored provider match detail is available for this fixture. "
                "No live provider lookup was attempted."
            ),
        }

    return {
        "detail_state": "available",
        "provider": match_detail.provider or None,
        "stored_detail_updated_at": match_detail.updated_at,
        "event_types": {
            "goals": _build_stored_event_type_coverage(
                "goal",
                match_detail.goals,
            ),
            "cards": _build_stored_event_type_coverage(
                "card",
                match_detail.cards,
            ),
            "substitutions": _build_stored_event_type_coverage(
                "substitution",
                match_detail.substitutions,
            ),
        },
        "message": (
            "Stored provider match detail is available. Event counts describe only "
            "the last stored provider payload and do not confirm match completeness."
        ),
    }


def notify_newly_completed_fixtures(
    db: Session,
    newly_completed_external_ids: list[str],
) -> dict:
    """
    Dispatch completed-match Telegram alerts only when explicitly enabled.

    Manual Telegram test notifications remain available at
    /notifications/telegram/test. This policy only controls alerts generated by
    fixture syncs.
    """
    if not settings.telegram_completed_match_alerts_enabled:
        record_notification_result(
            channel="telegram",
            status="skipped",
        )

        return {
            "status": "skipped",
            "reason": "Completed-match Telegram alerts are disabled by configuration.",
            "sent": 0,
        }

    if not newly_completed_external_ids:
        record_notification_result(
            channel="telegram",
            status="skipped",
        )

        return {
            "status": "skipped",
            "reason": "No newly completed fixtures",
            "sent": 0,
        }

    fixtures = (
        db.query(Fixture)
        .filter(Fixture.external_id.in_(newly_completed_external_ids))
        .all()
    )

    serialized_fixtures = [serialize_fixture(fixture) for fixture in fixtures]

    try:
        result = send_completed_fixture_notifications(serialized_fixtures)

        record_notification_result(
            channel="telegram",
            status="sent",
        )

        return {
            "status": "sent",
            "sent": result["sent"],
        }

    except ValueError as error:
        record_notification_result(
            channel="telegram",
            status="skipped",
        )

        return {
            "status": "skipped",
            "reason": str(error),
            "sent": 0,
        }

    except TelegramNotificationError as error:
        record_notification_result(
            channel="telegram",
            status="failed",
        )

        return {
            "status": "failed",
            "reason": str(error),
            "sent": 0,
        }


def _record_sync_success(
    db: Session,
    source: str,
    provider_name: str,
    result: dict,
    duration_seconds: float,
    started_at: str,
) -> None:
    record_fixture_sync_metrics(
        source=source,
        provider=provider_name,
        status="success",
        result=result,
        duration_seconds=duration_seconds,
    )
    record_fixture_sync_status(
        db=db,
        source=source,
        provider=provider_name,
        status="success",
        result=result,
        duration_seconds=duration_seconds,
        trigger_type="manual",
        started_at=started_at,
    )


def _record_sync_failure(
    db: Session,
    source: str,
    provider_name: str,
    duration_seconds: float,
    error_message: str,
    started_at: str,
) -> None:
    record_fixture_sync_metrics(
        source=source,
        provider=provider_name,
        status="error",
        duration_seconds=duration_seconds,
    )
    record_fixture_sync_status(
        db=db,
        source=source,
        provider=provider_name,
        status="error",
        duration_seconds=duration_seconds,
        error=error_message,
        trigger_type="manual",
        started_at=started_at,
    )


@router.get("")
def list_fixtures(
    group_name: str | None = Query(
        default=None,
        description="Filter fixtures by group name, for example: Group A",
    ),
    status: str | None = Query(
        default=None,
        description="Filter fixtures by status, for example: scheduled, complete, or live",
    ),
    team: str | None = Query(
        default=None,
        description="Search fixtures by team name or team code",
    ),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(Fixture)

        if group_name:
            query = query.filter(Fixture.group_name == group_name)

        if status:
            query = query.filter(Fixture.status == status)

        if team:
            team_search = f"%{team}%"
            query = query.filter(
                or_(
                    Fixture.home_team.ilike(team_search),
                    Fixture.away_team.ilike(team_search),
                    Fixture.home_team_code.ilike(team_search),
                    Fixture.away_team_code.ilike(team_search),
                )
            )

        fixtures = query.order_by(Fixture.kickoff_time.asc()).all()

        return {
            "count": len(fixtures),
            "filters": {
                "group_name": group_name,
                "status": status,
                "team": team,
            },
            "fixtures": [serialize_fixture(fixture) for fixture in fixtures],
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while listing fixtures: {error}",
        ) from error


@router.get("/sync/status")
def get_fixture_sync_runtime_status(db: Session = Depends(get_db)):
    return get_fixture_sync_status(db)


@router.get("/sync/history")
def get_fixture_sync_history(
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of recent persisted fixture sync runs",
    ),
    db: Session = Depends(get_db),
):
    runs = list_fixture_sync_runs(db, limit=limit)

    return {
        "count": len(runs),
        "runs": runs,
    }


@router.get("/{fixture_id}/detail")
def get_fixture_detail(fixture_id: int, db: Session = Depends(get_db)):
    try:
        fixture = db.query(Fixture).filter(Fixture.id == fixture_id).first()

        if fixture is None:
            raise HTTPException(
                status_code=404,
                detail="Fixture not found",
            )

        match_detail = (
            db.query(MatchDetail)
            .filter(MatchDetail.fixture_id == fixture.id)
            .first()
        )

        return {
            "fixture": serialize_fixture(fixture),
            "detail_available": match_detail is not None,
            "detail": (
                serialize_match_detail(match_detail)
                if match_detail is not None
                else None
            ),
            "stored_event_coverage": build_stored_event_coverage(match_detail),
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while getting fixture detail: {error}",
        ) from error


@router.get("/{fixture_id}")
def get_fixture(fixture_id: int, db: Session = Depends(get_db)):
    try:
        fixture = db.query(Fixture).filter(Fixture.id == fixture_id).first()

        if fixture is None:
            raise HTTPException(
                status_code=404,
                detail="Fixture not found",
            )

        return serialize_fixture(fixture)

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while getting fixture: {error}",
        ) from error


@router.post("/sync/sample")
def sync_sample_fixtures(db: Session = Depends(get_db)):
    source = "sample"
    provider_name = "sample_data"
    started_at = _utc_now_iso()
    start_time = time.perf_counter()

    try:
        result = sync_fixtures(db, SAMPLE_FIXTURES)
        duration_seconds = time.perf_counter() - start_time

        _record_sync_success(
            db=db,
            source=source,
            provider_name=provider_name,
            result=result,
            duration_seconds=duration_seconds,
            started_at=started_at,
        )

        notification_result = notify_newly_completed_fixtures(
            db,
            result["newly_completed"],
        )

        return {
            "message": "Sample fixtures synced successfully",
            "provider": provider_name,
            "created": result["created"],
            "updated": result["updated"],
            "total_sample_fixtures": result["total_fixtures"],
            "newly_completed_count": result["newly_completed_count"],
            "newly_completed": result["newly_completed"],
            "duration_seconds": duration_seconds,
            "notifications": notification_result,
        }

    except SQLAlchemyError as error:
        db.rollback()
        duration_seconds = time.perf_counter() - start_time
        error_message = sanitize_sync_error(
            f"Database error while syncing sample fixtures: {error}"
        ) or "Database error while syncing sample fixtures."

        try:
            _record_sync_failure(
                db=db,
                source=source,
                provider_name=provider_name,
                duration_seconds=duration_seconds,
                error_message=error_message,
                started_at=started_at,
            )
        except SQLAlchemyError:
            db.rollback()

        raise HTTPException(
            status_code=503,
            detail=error_message,
        ) from error


@router.post("/sync/provider")
def sync_provider_fixtures(db: Session = Depends(get_db)):
    source = "provider"
    provider_name = "unknown"
    started_at = _utc_now_iso()
    start_time = time.perf_counter()

    try:
        provider_name, provider = get_configured_football_provider()
        fixtures = provider.get_world_cup_fixtures()
        result = sync_fixtures(db, fixtures)
        duration_seconds = time.perf_counter() - start_time

        _record_sync_success(
            db=db,
            source=source,
            provider_name=provider_name,
            result=result,
            duration_seconds=duration_seconds,
            started_at=started_at,
        )

        notification_result = notify_newly_completed_fixtures(
            db,
            result["newly_completed"],
        )

        return {
            "message": "Provider fixtures synced successfully",
            "provider": provider_name,
            "created": result["created"],
            "updated": result["updated"],
            "total_provider_fixtures": result["total_fixtures"],
            "newly_completed_count": result["newly_completed_count"],
            "newly_completed": result["newly_completed"],
            "duration_seconds": duration_seconds,
            "notifications": notification_result,
        }

    except ValueError as error:
        duration_seconds = time.perf_counter() - start_time
        error_message = sanitize_sync_error(str(error)) or "Provider sync failed."

        _record_sync_failure(
            db=db,
            source=source,
            provider_name=provider_name,
            duration_seconds=duration_seconds,
            error_message=error_message,
            started_at=started_at,
        )

        raise HTTPException(
            status_code=400,
            detail=error_message,
        ) from error

    except (ApiFootballProviderError, ZafronixProviderError) as error:
        duration_seconds = time.perf_counter() - start_time
        error_message = sanitize_sync_error(str(error)) or "Provider sync failed."

        _record_sync_failure(
            db=db,
            source=source,
            provider_name=provider_name,
            duration_seconds=duration_seconds,
            error_message=error_message,
            started_at=started_at,
        )

        raise HTTPException(
            status_code=502,
            detail=error_message,
        ) from error

    except SQLAlchemyError as error:
        db.rollback()
        duration_seconds = time.perf_counter() - start_time
        error_message = sanitize_sync_error(
            f"Database error while syncing provider fixtures: {error}"
        ) or "Database error while syncing provider fixtures."

        try:
            _record_sync_failure(
                db=db,
                source=source,
                provider_name=provider_name,
                duration_seconds=duration_seconds,
                error_message=error_message,
                started_at=started_at,
            )
        except SQLAlchemyError:
            db.rollback()

        raise HTTPException(
            status_code=503,
            detail=error_message,
        ) from error
