import time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fixture import Fixture
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
    record_fixture_sync_status,
)
from app.services.telegram_notifier import (
    TelegramNotificationError,
    send_completed_fixture_notifications,
)

router = APIRouter(
    prefix="/fixtures",
    tags=["fixtures"],
)


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


def notify_newly_completed_fixtures(
    db: Session,
    newly_completed_external_ids: list[str],
) -> dict:
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
def get_fixture_sync_runtime_status():
    return get_fixture_sync_status()


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
    start_time = time.perf_counter()

    try:
        result = sync_fixtures(db, SAMPLE_FIXTURES)
        duration_seconds = time.perf_counter() - start_time

        record_fixture_sync_metrics(
            source=source,
            provider=provider_name,
            status="success",
            result=result,
            duration_seconds=duration_seconds,
        )
        record_fixture_sync_status(
            source=source,
            provider=provider_name,
            status="success",
            result=result,
            duration_seconds=duration_seconds,
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
        error_message = f"Database error while syncing sample fixtures: {error}"

        record_fixture_sync_metrics(
            source=source,
            provider=provider_name,
            status="error",
            duration_seconds=duration_seconds,
        )
        record_fixture_sync_status(
            source=source,
            provider=provider_name,
            status="error",
            duration_seconds=duration_seconds,
            error=error_message,
        )

        raise HTTPException(
            status_code=503,
            detail=error_message,
        ) from error


@router.post("/sync/provider")
def sync_provider_fixtures(db: Session = Depends(get_db)):
    source = "provider"
    provider_name = "unknown"
    start_time = time.perf_counter()

    try:
        provider_name, provider = get_configured_football_provider()
        fixtures = provider.get_world_cup_fixtures()
        result = sync_fixtures(db, fixtures)
        duration_seconds = time.perf_counter() - start_time

        record_fixture_sync_metrics(
            source=source,
            provider=provider_name,
            status="success",
            result=result,
            duration_seconds=duration_seconds,
        )
        record_fixture_sync_status(
            source=source,
            provider=provider_name,
            status="success",
            result=result,
            duration_seconds=duration_seconds,
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
        error_message = str(error)

        record_fixture_sync_metrics(
            source=source,
            provider=provider_name,
            status="error",
            duration_seconds=duration_seconds,
        )
        record_fixture_sync_status(
            source=source,
            provider=provider_name,
            status="error",
            duration_seconds=duration_seconds,
            error=error_message,
        )

        raise HTTPException(
            status_code=400,
            detail=error_message,
        ) from error

    except (ApiFootballProviderError, ZafronixProviderError) as error:
        duration_seconds = time.perf_counter() - start_time
        error_message = str(error)

        record_fixture_sync_metrics(
            source=source,
            provider=provider_name,
            status="error",
            duration_seconds=duration_seconds,
        )
        record_fixture_sync_status(
            source=source,
            provider=provider_name,
            status="error",
            duration_seconds=duration_seconds,
            error=error_message,
        )

        raise HTTPException(
            status_code=502,
            detail=error_message,
        ) from error

    except SQLAlchemyError as error:
        db.rollback()
        duration_seconds = time.perf_counter() - start_time
        error_message = f"Database error while syncing provider fixtures: {error}"

        record_fixture_sync_metrics(
            source=source,
            provider=provider_name,
            status="error",
            duration_seconds=duration_seconds,
        )
        record_fixture_sync_status(
            source=source,
            provider=provider_name,
            status="error",
            duration_seconds=duration_seconds,
            error=error_message,
        )

        raise HTTPException(
            status_code=503,
            detail=error_message,
        ) from error
