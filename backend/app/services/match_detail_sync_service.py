from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.fixture import Fixture
from app.models.match_detail import MatchDetail


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_dict(value: Any) -> dict:
    return value.copy() if isinstance(value, dict) else {}


def _as_list(value: Any) -> list:
    return value.copy() if isinstance(value, list) else []


def _clean_text(value: Any, fallback: str | None = None) -> str | None:
    if value is None:
        return fallback

    cleaned = str(value).strip()
    return cleaned or fallback


def upsert_match_detail(
    db: Session,
    fixture: Fixture,
    detail_data: dict,
) -> MatchDetail:
    if fixture.id is None:
        db.flush()

    now = _utc_now_iso()

    item = {
        "provider": _clean_text(detail_data.get("provider"), "unknown"),
        "provider_match_id": _clean_text(detail_data.get("provider_match_id")),
        "goals": _as_list(detail_data.get("goals")),
        "cards": _as_list(detail_data.get("cards")),
        "substitutions": _as_list(detail_data.get("substitutions")),
        "formations": _as_dict(detail_data.get("formations")),
        "lineups": _as_dict(detail_data.get("lineups")),
        "statistics": _as_dict(detail_data.get("statistics")),
        "referee": _as_dict(detail_data.get("referee")),
        "weather": _as_dict(detail_data.get("weather")),
        "updated_at": now,
    }

    existing_detail = (
        db.query(MatchDetail)
        .filter(MatchDetail.fixture_id == fixture.id)
        .first()
    )

    if existing_detail:
        for key, value in item.items():
            setattr(existing_detail, key, value)

        return existing_detail

    item["fixture_id"] = fixture.id
    item["created_at"] = now

    match_detail = MatchDetail(**item)
    db.add(match_detail)

    return match_detail
