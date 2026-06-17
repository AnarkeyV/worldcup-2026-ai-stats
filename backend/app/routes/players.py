from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.player_stat import PlayerStat
from app.services.player_stats_sample_data import SAMPLE_PLAYER_STATS
from app.services.player_stats_service import (
    serialize_player_stat,
    sort_player_stats,
    sync_player_stats,
)

router = APIRouter(
    prefix="/players",
    tags=["players"],
)

PlayerStatsSortField = Literal[
    "goals",
    "assists",
    "yellow_cards",
    "red_cards",
    "minutes_played",
    "player_name",
    "team",
]


@router.get("/stats")
def list_player_stats(
    team: str | None = Query(
        default=None,
        description="Search by team name or team code",
    ),
    group_name: str | None = Query(
        default=None,
        description="Filter player stats by group name, for example: Group A",
    ),
    sort_by: PlayerStatsSortField = Query(
        default="goals",
        description="Sort player stats by goals, assists, cards, minutes, player name, or team",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of player stat rows to return",
    ),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(PlayerStat)

        if group_name:
            query = query.filter(PlayerStat.group_name == group_name)

        if team:
            team_search = f"%{team}%"
            query = query.filter(
                or_(
                    PlayerStat.team.ilike(team_search),
                    PlayerStat.team_code.ilike(team_search),
                )
            )

        player_stats = [
            serialize_player_stat(player_stat)
            for player_stat in query.all()
        ]

        sorted_stats = sort_player_stats(
            player_stats=player_stats,
            sort_by=sort_by,
            limit=limit,
        )

        return {
            "count": len(sorted_stats),
            "total_available": len(player_stats),
            "filters": {
                "team": team,
                "group_name": group_name,
                "sort_by": sort_by,
                "limit": limit,
            },
            "stats": sorted_stats,
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while listing player stats: {error}",
        ) from error


@router.post("/stats/sync/sample")
def sync_sample_player_stats(db: Session = Depends(get_db)):
    try:
        result = sync_player_stats(db, SAMPLE_PLAYER_STATS)

        return {
            "message": "Sample player stats synced successfully",
            "created": result["created"],
            "updated": result["updated"],
            "total_sample_player_stats": result["total_player_stats"],
        }

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=503,
            detail=f"Database error while syncing sample player stats: {error}",
        ) from error
