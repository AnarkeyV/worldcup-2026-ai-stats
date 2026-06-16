from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import create_db_and_tables, get_db
from app.models.fixture import Fixture
from app.services.sample_data import SAMPLE_FIXTURES

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


@router.get("")
def list_fixtures(db: Session = Depends(get_db)):
    try:
        create_db_and_tables()

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
        create_db_and_tables()

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
        create_db_and_tables()

        created = 0
        updated = 0

        for item in SAMPLE_FIXTURES:
            existing_fixture = (
                db.query(Fixture)
                .filter(Fixture.external_id == item["external_id"])
                .first()
            )

            if existing_fixture:
                for key, value in item.items():
                    setattr(existing_fixture, key, value)

                updated += 1

            else:
                fixture = Fixture(**item)
                db.add(fixture)
                created += 1

        db.commit()

        return {
            "message": "Sample fixtures synced successfully",
            "created": created,
            "updated": updated,
            "total_sample_fixtures": len(SAMPLE_FIXTURES),
        }

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=503,
            detail=f"Database error while syncing sample fixtures: {error}",
        ) from error