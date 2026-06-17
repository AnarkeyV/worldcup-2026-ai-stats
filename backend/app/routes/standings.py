from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fixture import Fixture
from app.services.standings_service import build_group_standings

router = APIRouter(
    prefix="/standings",
    tags=["standings"],
)


@router.get("")
def list_standings(
    group_name: str | None = Query(
        default=None,
        description="Filter standings by group name, for example: Group A",
    ),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(Fixture)

        if group_name:
            query = query.filter(Fixture.group_name == group_name)

        fixtures = query.order_by(Fixture.kickoff_time.asc()).all()
        standings = build_group_standings(
            fixtures=fixtures,
            group_name=group_name,
        )

        return {
            "count": len(standings),
            "filters": {
                "group_name": group_name,
            },
            "standings": standings,
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while listing standings: {error}",
        ) from error
