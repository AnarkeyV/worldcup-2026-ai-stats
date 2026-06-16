from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.fixture import Fixture


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sync_fixtures(db: Session, fixtures: list[dict]) -> dict:
    """
    Create or update fixtures using external_id as the unique provider identifier.

    Args:
        db (Session): SQLAlchemy database session.
        fixtures (list[dict]): Normalized fixture dictionaries.

    Returns:
        dict: Summary containing created, updated, and total counts.
    """
    created = 0
    updated = 0
    now = _utc_now_iso()

    for item in fixtures:
        external_id = item["external_id"]

        existing_fixture = (
            db.query(Fixture)
            .filter(Fixture.external_id == external_id)
            .first()
        )

        item.setdefault("created_at", now)
        item["updated_at"] = now

        if existing_fixture:
            item.pop("created_at", None)

            for key, value in item.items():
                setattr(existing_fixture, key, value)

            updated += 1

        else:
            fixture = Fixture(**item)
            db.add(fixture)
            created += 1

    db.commit()

    return {
        "created": created,
        "updated": updated,
        "total_fixtures": len(fixtures),
    }