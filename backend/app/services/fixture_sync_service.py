from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.fixture import Fixture
from app.services.match_detail_sync_service import upsert_match_detail


COMPLETED_STATUSES = {
    "complete",
    "completed",
    "finished",
    "final",
    "ft",
    "full-time",
    "full_time",
    "match finished",
    "aet",
    "pen",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_status(status: Any) -> str:
    if status is None:
        return ""

    return str(status).strip().lower()


def _is_completed_status(status: Any) -> bool:
    return _normalize_status(status) in COMPLETED_STATUSES


def _clean_external_id(value: Any) -> str:
    if value is None:
        raise ValueError("Fixture external_id is required.")

    external_id = str(value).strip()

    if not external_id:
        raise ValueError("Fixture external_id is required.")

    return external_id


def sync_fixtures(db: Session, fixtures: list[dict]) -> dict:
    """
    Create or update fixtures using external_id as the unique provider identifier.

    This service also detects fixtures that have newly changed into a completed
    match status during this sync.

    Args:
        db (Session): SQLAlchemy database session.
        fixtures (list[dict]): Normalized fixture dictionaries.

    Returns:
        dict: Summary containing created, updated, total, and newly completed counts.
    """
    created = 0
    updated = 0
    newly_completed = []
    now = _utc_now_iso()

    for fixture_data in fixtures:
        item = fixture_data.copy()
        match_detail_data = item.pop("match_detail", None)
        external_id = _clean_external_id(item.get("external_id"))
        item["external_id"] = external_id

        existing_fixture = (
            db.query(Fixture)
            .filter(Fixture.external_id == external_id)
            .first()
        )

        previous_status = existing_fixture.status if existing_fixture else None
        new_status = item.get("status")

        was_completed = _is_completed_status(previous_status)
        is_completed = _is_completed_status(new_status)

        item.setdefault("created_at", now)
        item["updated_at"] = now

        if existing_fixture:
            item.pop("created_at", None)

            for key, value in item.items():
                setattr(existing_fixture, key, value)

            fixture_record = existing_fixture

            if not was_completed and is_completed:
                newly_completed.append(external_id)

            updated += 1

        else:
            fixture_record = Fixture(**item)
            db.add(fixture_record)
            db.flush()
            created += 1

            if is_completed:
                newly_completed.append(external_id)

        if isinstance(match_detail_data, dict):
            upsert_match_detail(
                db=db,
                fixture=fixture_record,
                detail_data=match_detail_data,
            )

    db.commit()

    return {
        "created": created,
        "updated": updated,
        "total_fixtures": len(fixtures),
        "newly_completed": newly_completed,
        "newly_completed_count": len(newly_completed),
    }