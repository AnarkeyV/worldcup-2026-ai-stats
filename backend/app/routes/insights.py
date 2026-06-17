from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fixture import Fixture
from app.services.insights_service import build_group_insights

router = APIRouter(
    prefix="/insights",
    tags=["insights"],
)


@router.get("/groups")
def list_group_insights(
    group_name: str | None = Query(
        default=None,
        description="Filter insights by group name, for example: Group A",
    ),
    limit: int = Query(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of teams to return for ranked insight lists",
    ),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(Fixture)

        if group_name:
            query = query.filter(Fixture.group_name == group_name)

        fixtures = query.order_by(Fixture.kickoff_time.asc()).all()
        insights = build_group_insights(
            fixtures=fixtures,
            group_name=group_name,
            limit=limit,
        )

        return {
            "filters": {
                "group_name": group_name,
                "limit": limit,
            },
            "insights": insights,
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while listing group insights: {error}",
        ) from error
