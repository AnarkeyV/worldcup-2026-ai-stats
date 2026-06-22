from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fixture import Fixture
from app.models.match_detail import MatchDetail
from app.services.provider_leaderboard_service import build_latest_completed_match_summary


router = APIRouter(
    prefix="/ai",
    tags=["provider-ai"],
)


@router.get("/latest-completed/summary")
def get_latest_completed_match_summary(db: Session = Depends(get_db)):
    """
    Return a deterministic summary of the latest completed fixture.

    Provider red cards are mentioned before the score and scorer list when the
    stored rich match detail contains them. No player events are invented when
    details are unavailable.
    """
    try:
        fixtures = db.query(Fixture).all()
        match_details = db.query(MatchDetail).all()
        summary = build_latest_completed_match_summary(
            fixtures=fixtures,
            match_details=match_details,
        )

        if summary is None:
            raise HTTPException(
                status_code=404,
                detail="No completed fixtures available to summarize.",
            )

        return {
            "status": "ok",
            "mode": "provider_backed" if summary["detail_available"] else "fixture_data",
            **summary,
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while building latest completed summary: {error}",
        ) from error
