from copy import deepcopy
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.models.fixture_sync_change_set import FixtureSyncChangeSet
from app.models.fixture_sync_run import FixtureSyncRun
from app.services.scheduled_sync_schedule import (
    get_scheduled_sync_runtime_status,
)


def _utc_now() -> datetime:
    """Return the UTC reference time used for one freshness calculation."""
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


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
        round((_utc_now() - completed_at).total_seconds()),
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


def _build_scheduler_status() -> dict:
    """Return safe, read-only scheduling metadata for the dashboard and API."""
    try:
        status = get_scheduled_sync_runtime_status(
            enabled=settings.provider_sync_scheduler_enabled,
            schedule_times_raw=settings.provider_sync_schedule_times,
            timezone_name=settings.provider_sync_schedule_timezone,
        )
    except ValueError:
        status = {
            "enabled": bool(settings.provider_sync_scheduler_enabled),
            "mode": "fixed_daily_times",
            "timezone": (
                str(settings.provider_sync_schedule_timezone or "").strip() or None
            ),
            "scheduled_times": [],
            "next_run_at": None,
            "configuration_error": "Invalid fixed-time provider sync schedule.",
        }

    # Preserve this legacy field for dashboard compatibility while the runtime
    # uses fixed daily slots.
    status["interval_minutes"] = int(settings.provider_sync_interval_minutes)
    return status


def _as_timezone_iso(value: str | None, timezone_name: str | None) -> str | None:
    """Convert a stored ISO timestamp to the configured display timezone.

    Stored timestamps remain untouched. This helper returns a derived display value
    only when both the timestamp and timezone are valid.
    """
    parsed = _parse_iso(value)
    cleaned_timezone = str(timezone_name or "").strip()
    if parsed is None or not cleaned_timezone:
        return None

    try:
        return parsed.astimezone(ZoneInfo(cleaned_timezone)).isoformat()
    except ZoneInfoNotFoundError:
        return None


def _build_freshness_context(
    *,
    freshness: dict[str, Any],
    last_success_at: str | None,
    scheduler: dict[str, Any],
) -> dict[str, Any]:
    """Explain snapshot freshness relative to the configured refresh schedule.

    This is additive read-only metadata. It never changes provider state, fixture
    state, scheduling, or the stored timestamps used as the source of truth.
    """
    state = str(freshness.get("state") or "unavailable")
    timezone_name = str(scheduler.get("timezone") or "").strip() or None
    next_scheduled_run_at = scheduler.get("next_run_at")
    next_scheduled_run = _parse_iso(next_scheduled_run_at)
    last_successful_run = _parse_iso(last_success_at)

    snapshot_becomes_stale_at: str | None = None
    stale_before_next_scheduled_run: bool | None = None
    if last_successful_run is not None:
        stale_after_seconds = freshness.get("stale_after_seconds")
        try:
            stale_after_seconds = int(stale_after_seconds)
        except (TypeError, ValueError):
            stale_after_seconds = None

        if stale_after_seconds is not None and stale_after_seconds >= 0:
            snapshot_becomes_stale = last_successful_run + timedelta(
                seconds=stale_after_seconds
            )
            snapshot_becomes_stale_at = snapshot_becomes_stale.isoformat()
            if next_scheduled_run is not None:
                stale_before_next_scheduled_run = (
                    snapshot_becomes_stale < next_scheduled_run
                )

    diagnostic, message = _freshness_context_message(
        state=state,
        last_successful_run=last_successful_run,
        next_scheduled_run=next_scheduled_run,
        stale_before_next_scheduled_run=stale_before_next_scheduled_run,
    )

    return {
        "state": state,
        "schedule_timezone": timezone_name,
        "last_success_at": last_success_at,
        "last_success_at_local": _as_timezone_iso(last_success_at, timezone_name),
        "next_scheduled_run_at": next_scheduled_run_at,
        "snapshot_becomes_stale_at": snapshot_becomes_stale_at,
        "snapshot_becomes_stale_at_local": _as_timezone_iso(
            snapshot_becomes_stale_at,
            timezone_name,
        ),
        "stale_before_next_scheduled_run": stale_before_next_scheduled_run,
        "diagnostic": diagnostic,
        "message": message,
    }


def _freshness_context_message(
    *,
    state: str,
    last_successful_run: datetime | None,
    next_scheduled_run: datetime | None,
    stale_before_next_scheduled_run: bool | None,
) -> tuple[str, str]:
    if state == "last_sync_failed":
        return (
            "latest_sync_failed",
            "The latest provider refresh failed; displayed data is from the last "
            "successful stored snapshot.",
        )

    if last_successful_run is None:
        if state == "not_started":
            return (
                "no_successful_snapshot",
                "No successful provider snapshot has been stored yet.",
            )
        return (
            "last_success_timestamp_unavailable",
            "Stored provider freshness cannot be determined from the latest "
            "successful snapshot timestamp.",
        )

    if stale_before_next_scheduled_run is True:
        if state == "stale":
            return (
                "snapshot_stale_before_next_scheduled_refresh",
                "The latest provider refresh succeeded, but its stored snapshot is "
                "stale before the next scheduled refresh.",
            )
        return (
            "snapshot_will_be_stale_before_next_scheduled_refresh",
            "The latest provider refresh succeeded; its stored snapshot will become "
            "stale before the next scheduled refresh.",
        )

    if state == "stale":
        if next_scheduled_run is None:
            return (
                "stale_without_next_scheduled_refresh",
                "The latest provider refresh succeeded, but its stored snapshot is "
                "stale and no next scheduled refresh is available.",
            )
        return (
            "stale_snapshot",
            "The latest provider refresh succeeded, but its stored snapshot is stale.",
        )

    if next_scheduled_run is None:
        return (
            "no_next_scheduled_refresh",
            "The latest provider refresh succeeded; no next scheduled refresh is "
            "currently available.",
        )

    return (
        "snapshot_within_freshness_window",
        "The latest provider refresh succeeded; the stored snapshot is within its "
        "current freshness window.",
    )


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
    freshness = {
        "state": "not_started",
        "data_age_seconds": None,
        "fresh_after_seconds": fresh_after_seconds,
        "stale_after_seconds": stale_after_seconds,
    }
    scheduler = _build_scheduler_status()
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
        "freshness": freshness,
        "freshness_context": _build_freshness_context(
            freshness=freshness,
            last_success_at=None,
            scheduler=scheduler,
        ),
        "scheduler": scheduler,
        "completed_match_alerts_enabled": bool(
            settings.telegram_completed_match_alerts_enabled
        ),
        "scheduled_telegram_digest_enabled": bool(
            settings.telegram_scheduled_digest_enabled
        ),
    }


def reset_fixture_sync_status() -> None:
    """Compatibility helper retained for older tests and local scripts.

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

    last_success_at = (
        last_successful_run.completed_at
        if last_successful_run is not None
        else None
    )
    freshness = _build_freshness(latest_run, last_successful_run)
    scheduler = _build_scheduler_status()

    return {
        "status": latest_run.status,
        "source": latest_run.source,
        "provider": latest_run.provider,
        "trigger_type": latest_run.trigger_type,
        "last_run_at": latest_run.completed_at,
        "last_success_at": last_success_at,
        "duration_seconds": latest_run.duration_seconds,
        "total_fixtures": latest_run.total_fixtures,
        "created": latest_run.created,
        "updated": latest_run.updated,
        "newly_completed_count": latest_run.newly_completed_count,
        "newly_completed": list(latest_run.newly_completed or []),
        "last_error": latest_run.last_error,
        "freshness": freshness,
        "freshness_context": _build_freshness_context(
            freshness=freshness,
            last_success_at=last_success_at,
            scheduler=scheduler,
        ),
        "scheduler": scheduler,
        "completed_match_alerts_enabled": bool(
            settings.telegram_completed_match_alerts_enabled
        ),
        "scheduled_telegram_digest_enabled": bool(
            settings.telegram_scheduled_digest_enabled
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


def _extract_change_summaries(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Keep only the internal factual summaries produced by Phase 1 contracts."""
    raw_summaries = result.get("change_summaries")
    if not isinstance(raw_summaries, list):
        return []

    summaries: list[dict[str, Any]] = []
    for summary in raw_summaries:
        if not isinstance(summary, dict):
            continue

        external_id = str(summary.get("external_id") or "").strip()
        changes = summary.get("changes")
        if not external_id or not isinstance(changes, list) or not changes:
            continue

        summaries.append(deepcopy(summary))

    return summaries


def _record_fixture_sync_change_set(
    db: Session,
    run: FixtureSyncRun,
    result: dict[str, Any],
) -> None:
    summaries = _extract_change_summaries(result)
    total_change_count = sum(
        len(summary.get("changes", []))
        for summary in summaries
        if isinstance(summary.get("changes"), list)
    )

    change_set = FixtureSyncChangeSet(
        sync_run_id=run.id,
        capture_state="recorded",
        compared_fixture_count=max(
            0,
            _to_int(result.get("compared_fixture_count")),
        ),
        changed_fixture_count=len(summaries),
        total_change_count=total_change_count,
        changes=summaries,
        created_at=_utc_now_iso(),
    )
    db.add(change_set)


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
    """Persist one terminal fixture sync result for dashboard and API audit history.

    Only safe, normalized run metadata is stored. Configured secrets are redacted
    from provider or runtime error messages before persistence. A successful v1.18+
    run also receives one additive companion change set; pre-v1.18 history has no
    such row and will later be presented as not recorded rather than empty.
    """
    result = result or {}
    completed_at = _utc_now_iso()
    normalized_status = "success" if status == "success" else "error"
    run = FixtureSyncRun(
        source=_clean_text(source, "unknown"),
        provider=_clean_text(provider, "unknown"),
        trigger_type=_clean_trigger_type(trigger_type),
        status=normalized_status,
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
    db.flush()

    if normalized_status == "success":
        _record_fixture_sync_change_set(db=db, run=run, result=result)

    db.commit()
    return _serialize_sync_run(run)


def sanitize_sync_error(error: str | None) -> str | None:
    """Return a redacted, bounded error suitable for API responses and logs."""
    return _sanitize_error_message(error)
