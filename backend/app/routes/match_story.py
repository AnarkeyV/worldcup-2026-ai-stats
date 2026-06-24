"""Read-only API route for provider-backed match storytelling.

The route queries only local fixture, match-detail, and manually verified
outbound official-video records. It does not call a provider, write to the
database, trigger sync work, scrape video sites, or send messages.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fixture import Fixture
from app.models.match_detail import MatchDetail
from app.models.official_match_video import OfficialMatchVideo
from app.services.match_story_service import build_match_story
from app.services.official_match_video_service import build_official_watch


router = APIRouter(
    tags=["match-story"],
)


def serialize_match_story_fixture(fixture: Fixture) -> dict:
    """Return the fixture fields required to interpret its stored story."""

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
        "updated_at": fixture.updated_at,
    }


@router.get("/fixtures/{fixture_id}/story")
def get_fixture_story(
    fixture_id: int,
    db: Session = Depends(get_db),
):
    """Return a computed story derived only from locally stored match data."""

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
        official_videos = (
            db.query(OfficialMatchVideo)
            .filter(OfficialMatchVideo.fixture_id == fixture.id)
            .all()
        )

        story = build_match_story(fixture, match_detail)
        story["official_watch"] = build_official_watch(official_videos)

        return {
            "fixture": serialize_match_story_fixture(fixture),
            "story": story,
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while getting fixture story: {error}",
        ) from error
