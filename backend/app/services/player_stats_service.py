from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.player_stat import PlayerStat


PLAYER_STATS_SORT_FIELDS = {
    "goals",
    "assists",
    "yellow_cards",
    "red_cards",
    "minutes_played",
    "player_name",
    "team",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def serialize_player_stat(player_stat: PlayerStat) -> dict[str, Any]:
    return {
        "id": player_stat.id,
        "external_id": player_stat.external_id,
        "competition": player_stat.competition,
        "stage": player_stat.stage,
        "group_name": player_stat.group_name,
        "team": player_stat.team,
        "team_code": player_stat.team_code,
        "player_name": player_stat.player_name,
        "position": player_stat.position,
        "shirt_number": player_stat.shirt_number,
        "appearances": player_stat.appearances,
        "goals": player_stat.goals,
        "assists": player_stat.assists,
        "yellow_cards": player_stat.yellow_cards,
        "red_cards": player_stat.red_cards,
        "minutes_played": player_stat.minutes_played,
        "created_at": player_stat.created_at,
        "updated_at": player_stat.updated_at,
    }


def sync_player_stats(db: Session, player_stats: list[dict]) -> dict:
    created = 0
    updated = 0
    now = _utc_now_iso()

    for player_data in player_stats:
        item = player_data.copy()
        external_id = item["external_id"]

        existing_player_stat = (
            db.query(PlayerStat)
            .filter(PlayerStat.external_id == external_id)
            .first()
        )

        item.setdefault("created_at", now)
        item["updated_at"] = now

        if existing_player_stat:
            item.pop("created_at", None)

            for key, value in item.items():
                setattr(existing_player_stat, key, value)

            updated += 1

        else:
            player_stat = PlayerStat(**item)
            db.add(player_stat)
            created += 1

    db.commit()

    return {
        "created": created,
        "updated": updated,
        "total_player_stats": len(player_stats),
    }


def sort_player_stats(
    player_stats: list[dict[str, Any]],
    sort_by: str = "goals",
    limit: int = 10,
) -> list[dict[str, Any]]:
    if sort_by not in PLAYER_STATS_SORT_FIELDS:
        raise ValueError(f"Unsupported player stats sort field: {sort_by}")

    sorted_player_stats = sorted(
        player_stats,
        key=lambda player: _sort_key(player, sort_by),
    )

    if limit <= 0:
        return []

    return sorted_player_stats[:limit]


def _sort_key(player: dict[str, Any], sort_by: str):
    if sort_by == "goals":
        return (
            -_safe_int(player, "goals"),
            -_safe_int(player, "assists"),
            -_safe_int(player, "minutes_played"),
            _safe_str(player, "player_name"),
        )

    if sort_by == "assists":
        return (
            -_safe_int(player, "assists"),
            -_safe_int(player, "goals"),
            -_safe_int(player, "minutes_played"),
            _safe_str(player, "player_name"),
        )

    if sort_by == "yellow_cards":
        return (
            -_safe_int(player, "yellow_cards"),
            _safe_str(player, "player_name"),
        )

    if sort_by == "red_cards":
        return (
            -_safe_int(player, "red_cards"),
            _safe_str(player, "player_name"),
        )

    if sort_by == "minutes_played":
        return (
            -_safe_int(player, "minutes_played"),
            _safe_str(player, "player_name"),
        )

    if sort_by == "player_name":
        return (
            _safe_str(player, "player_name"),
            _safe_str(player, "team"),
        )

    if sort_by == "team":
        return (
            _safe_str(player, "team"),
            _safe_str(player, "player_name"),
        )

    return (_safe_str(player, "player_name"),)


def _safe_int(player: dict[str, Any], key: str) -> int:
    value = player.get(key)

    if value is None:
        return 0

    return int(value)


def _safe_str(player: dict[str, Any], key: str) -> str:
    value = player.get(key)

    if value is None:
        return ""

    return str(value)
