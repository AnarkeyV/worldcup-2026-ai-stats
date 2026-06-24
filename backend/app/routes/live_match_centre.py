"""Read-only Live Match Centre API route.

The endpoint aggregates only stored fixtures, stored detail, stored event
coverage, and stored sync audit records. It never calls a provider, triggers a
sync, sends notifications, or writes to the database.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.live_match_centre_service import build_live_match_centre

router = APIRouter(tags=["live-match-centre"])


@router.get("/live-match-centre")
def get_live_match_centre(db: Session = Depends(get_db)):
    """Return the factual current Live Match Centre snapshot from local storage."""
    try:
        return build_live_match_centre(db)
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while reading live match centre: {error}",
        ) from error
