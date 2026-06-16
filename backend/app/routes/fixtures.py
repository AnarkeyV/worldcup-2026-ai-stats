from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fixture import Fixture
from app.providers.api_football import ApiFootballProvider
from app.services.fixture_sync_service import sync_fixtures
from app.services.sample_data import SAMPLE_FIXTURES
from app.services.telegram_notifier import send_completed_fixture_notifications

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

        return {
            "status": "sent",
            "sent": result["sent"],
        }

    except ValueError as error:
        return {
            "status": "skipped",
            "reason": str(error),
            "sent": 0,
        }

@router.get("")
def list_fixtures(db: Session = Depends(get_db)):
    try:
        fixtures = (
            db.query(Fixture)
            .order_by(Fixture.kickoff_time.asc())
            .all()
        )

        return {
            "count": len(fixtures),
            "fixtures": [serialize_fixture(fixture) for fixture in fixtures],
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while listing fixtures: {error}",
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
    try:
        result = sync_fixtures(db, SAMPLE_FIXTURES)
        notification_result = notify_newly_completed_fixtures(
            db,
            result["newly_completed"],
        )

        return {
            "message": "Sample fixtures synced successfully",
            "created": result["created"],
            "updated": result["updated"],
            "total_sample_fixtures": result["total_fixtures"],
            "newly_completed_count": result["newly_completed_count"],
            "newly_completed": result["newly_completed"],
            "notifications": notification_result,
        }

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=503,
            detail=f"Database error while syncing sample fixtures: {error}",
        ) from error
    
@router.post("/sync/provider")
def sync_provider_fixtures(db: Session = Depends(get_db)):
    try:
        provider = ApiFootballProvider()
        fixtures = provider.get_world_cup_fixtures()
        result = sync_fixtures(db, fixtures)
        notification_result = notify_newly_completed_fixtures(
            db,
            result["newly_completed"],
        )

        return {
            "message": "Provider fixtures synced successfully",
            "provider": "api_football",
            "created": result["created"],
            "updated": result["updated"],
            "total_provider_fixtures": result["total_fixtures"],
            "newly_completed_count": result["newly_completed_count"],
            "newly_completed": result["newly_completed"],
            "notifications": notification_result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=503,
            detail=f"Database error while syncing provider fixtures: {error}",
        ) from error