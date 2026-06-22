from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.models.fixture_sync_run import FixtureSyncRun


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default

        return int(value)

    except (TypeError, ValueError):
        return default


def _to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


def _clean_text(value: Any, fallback: str) -> str:
    cleaned = str(value or "").strip()
    return cleaned or fallback


def _clean_trigger_type(value: Any) -> str:
    trigger_type = _clean_text(value, "manual").lower()

    if trigger_type in {"manual", "scheduled"}:
        return trigger_type

    return "manual"


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def _sanitize_error_message(error: str | None) -> str | None:
    if not error:
        return None

    sanitized = " ".join(str(error).split())

    for secret in (
        settings.api_football_key,
        settings.zafronix_api_key,
        settings.telegram_bot_token,
        settings.telegram_chat_id,
    ):
        if secret and secret != "replace_me":
            sanitized = sanitized.replace(secret, "[redacted]")

    return sanitized[:500] or None


def _freshness_thresholds() -> tuple[int, int]:
    fresh_after_seconds = max(60, int(settings.fixture_sync_fresh_after_minutes) * 60)
    stale_after_seconds = max(
        fresh_after_seconds + 60,
        int(settings.fixture_sync_stale_after_minutes) * 60,
    )

    return fresh_after_seconds, stale_after_seconds


def _build_freshness(
    latest_run: FixtureSyncRun | None,
    last_successful_run: FixtureSyncRun | None,
) -> dict:
    fresh_after_seconds, stale_after_seconds = _freshness_thresholds()

    if last_successful_run is None:
        return {
            "state": "not_started",
            "data_age_seconds": None,
            "fresh_after_seconds": fresh_after_seconds,
            "stale_after_seconds": stale_after_seconds,
        }

    completed_at = _parse_iso(last_successful_run.completed_at)
    if completed_at is None:
        return {
            "state": "unavailable",
            "data_age_seconds": None,
            "fresh_after_seconds": fresh_after_seconds,
            "stale_after_seconds": stale_after_seconds,
        }

    data_age_seconds = max(
        0,
        round((datetime.now(timezone.utc) - completed_at).total_seconds()),
    )

    if latest_run is not None and latest_run.status == "error":
        state = "last_sync_failed"
    elif data_age_seconds <= fresh_after_seconds:
        state = "fresh"
    elif data_age_seconds <= stale_after_seconds:
        state = "aging"
    else:
        state = "stale"

    return {
        "state": state,
        "data_age_seconds": data_age_seconds,
        "fresh_after_seconds": fresh_after_seconds,
        "stale_after_seconds": stale_after_seconds,
    }


def _serialize_sync_run(run: FixtureSyncRun) -> dict:
    return {
        "id": run.id,
        "source": run.source,
        "provider": run.provider,
        "trigger_type": run.trigger_type,
        "status": run.status,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "duration_seconds": run.duration_seconds,
        "total_fixtures": run.total_fixtures,
        "created": run.created,
        "updated": run.updated,
        "newly_completed_count": run.newly_completed_count,
        "newly_completed": list(run.newly_completed or []),
        "last_error": run.last_error,
    }


def _default_fixture_sync_status() -> dict:
    fresh_after_seconds, stale_after_seconds = _freshness_thresholds()

    return {
        "status": "not_started",
        "source": None,
        "provider": None,
        "trigger_type": None,
        "last_run_at": None,
        "last_success_at": None,
        "duration_seconds": None,
        "total_fixtures": 0,
        "created": 0,
        "updated": 0,
        "newly_completed_count": 0,
        "newly_completed": [],
        "last_error": None,
        "freshness": {
            "state": "not_started",
            "data_age_seconds": None,
            "fresh_after_seconds": fresh_after_seconds,
            "stale_after_seconds": stale_after_seconds,
        },
        "scheduler": {
            "enabled": bool(settings.provider_sync_scheduler_enabled),
            "interval_minutes": int(settings.provider_sync_interval_minutes),
        },
        "completed_match_alerts_enabled": bool(
            settings.telegram_completed_match_alerts_enabled
        ),
    }


def reset_fixture_sync_status() -> None:
    """
    Compatibility helper retained for older tests and local scripts.

    Sync state is now persisted per database, so callers should reset their test
    database rather than relying on process-memory state.
    """


def get_fixture_sync_status(db: Session) -> dict:
    latest_run = (
        db.query(FixtureSyncRun)
        .order_by(FixtureSyncRun.id.desc())
        .first()
    )
    last_successful_run = (
        db.query(FixtureSyncRun)
        .filter(FixtureSyncRun.status == "success")
        .order_by(FixtureSyncRun.id.desc())
        .first()
    )

    if latest_run is None:
        return _default_fixture_sync_status()

    return {
        "status": latest_run.status,
        "source": latest_run.source,
        "provider": latest_run.provider,
        "trigger_type": latest_run.trigger_type,
        "last_run_at": latest_run.completed_at,
        "last_success_at": (
            last_successful_run.completed_at if last_successful_run is not None else None
        ),
        "duration_seconds": latest_run.duration_seconds,
        "total_fixtures": latest_run.total_fixtures,
        "created": latest_run.created,
        "updated": latest_run.updated,
        "newly_completed_count": latest_run.newly_completed_count,
        "newly_completed": list(latest_run.newly_completed or []),
        "last_error": latest_run.last_error,
        "freshness": _build_freshness(latest_run, last_successful_run),
        "scheduler": {
            "enabled": bool(settings.provider_sync_scheduler_enabled),
            "interval_minutes": int(settings.provider_sync_interval_minutes),
        },
        "completed_match_alerts_enabled": bool(
            settings.telegram_completed_match_alerts_enabled
        ),
    }


def list_fixture_sync_runs(db: Session, limit: int = 10) -> list[dict]:
    runs = (
        db.query(FixtureSyncRun)
        .order_by(FixtureSyncRun.id.desc())
        .limit(limit)
        .all()
    )

    return [_serialize_sync_run(run) for run in runs]


def record_fixture_sync_status(
    db: Session,
    source: str,
    provider: str,
    status: str,
    result: dict | None = None,
    duration_seconds: float | None = None,
    error: str | None = None,
    trigger_type: str = "manual",
    started_at: str | None = None,
) -> dict:
    """
    Persist one terminal fixture sync result for dashboard and API audit history.

    Only safe, normalized run metadata is stored. Configured secrets are
    redacted from provider or runtime error messages before persistence.
    """
    result = result or {}
    completed_at = _utc_now_iso()

    run = FixtureSyncRun(
        source=_clean_text(source, "unknown"),
        provider=_clean_text(provider, "unknown"),
        trigger_type=_clean_trigger_type(trigger_type),
        status="success" if status == "success" else "error",
        started_at=started_at or completed_at,
        completed_at=completed_at,
        duration_seconds=_to_float(duration_seconds),
        total_fixtures=_to_int(result.get("total_fixtures")),
        created=_to_int(result.get("created")),
        updated=_to_int(result.get("updated")),
        newly_completed_count=_to_int(result.get("newly_completed_count")),
        newly_completed=list(result.get("newly_completed", [])),
        last_error=_sanitize_error_message(error),
    )

    db.add(run)
    db.commit()

    return _serialize_sync_run(run)


def sanitize_sync_error(error: str | None) -> str | None:
    """Return a redacted, bounded error suitable for API responses and logs."""
    return _sanitize_error_message(error)
