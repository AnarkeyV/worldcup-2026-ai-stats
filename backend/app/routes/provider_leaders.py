from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fixture import Fixture
from app.models.match_detail import MatchDetail
from app.services.provider_leaderboard_service import build_provider_player_leaderboards


router = APIRouter(
    prefix="/players",
    tags=["provider-player-leaders"],
)


@router.get("/leaders")
def list_provider_player_leaders(
    team: str | None = Query(
        default=None,
        description="Filter by team name or team code",
    ),
    group_name: str | None = Query(
        default=None,
        description="Filter by group name, for example: Group A",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum rows to return for each leaderboard",
    ),
    db: Session = Depends(get_db),
):
    """
    Return real scorer and discipline leaders derived from provider match details.

    This intentionally does not read the legacy sample PlayerStat table.
    A team filter scopes the resulting player rows, not merely the fixtures in
    which that team appeared. That prevents opposing players from being shown
    in a selected team's leaderboard.
    """
    try:
        query = db.query(Fixture)

        if group_name:
            query = query.filter(Fixture.group_name == group_name)

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

        fixtures = query.all()
        fixture_ids = [fixture.id for fixture in fixtures]

        match_details = (
            db.query(MatchDetail)
            .filter(MatchDetail.fixture_id.in_(fixture_ids))
            .all()
            if fixture_ids
            else []
        )
        payload = build_provider_player_leaderboards(
            fixtures=fixtures,
            match_details=match_details,
        )

        if team:
            for leaderboard_name, rows in payload["leaderboards"].items():
                payload["leaderboards"][leaderboard_name] = [
                    row
                    for row in rows
                    if _row_matches_team(row=row, team=team)
                ]

        for rows in payload["leaderboards"].values():
            del rows[limit:]

        payload["filters"] = {
            "team": team,
            "group_name": group_name,
            "limit": limit,
        }

        return payload

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while building provider player leaders: {error}",
        ) from error


def _row_matches_team(row: dict, team: str) -> bool:
    team_search = team.strip().casefold()

    if not team_search:
        return True

    values = [
        str(row.get("team") or "").strip().casefold(),
        str(row.get("team_code") or "").strip().casefold(),
    ]

    return any(team_search in value for value in values if value)
