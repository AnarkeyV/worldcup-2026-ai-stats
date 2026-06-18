from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


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


def _default_fixture_sync_status() -> dict:
    return {
        "status": "not_started",
        "source": None,
        "provider": None,
        "last_run_at": None,
        "last_success_at": None,
        "duration_seconds": None,
        "total_fixtures": 0,
        "created": 0,
        "updated": 0,
        "newly_completed_count": 0,
        "newly_completed": [],
        "last_error": None,
    }


_fixture_sync_status = _default_fixture_sync_status()


def reset_fixture_sync_status() -> None:
    """
    Reset the in-memory fixture sync runtime status.

    This is mainly useful for tests because the application keeps this state in
    process memory rather than storing it in the database.
    """
    global _fixture_sync_status

    _fixture_sync_status = _default_fixture_sync_status()


def get_fixture_sync_status() -> dict:
    """
    Return the latest fixture sync runtime status.

    The returned value is a defensive copy so callers cannot accidentally mutate
    the process-level state.
    """
    return deepcopy(_fixture_sync_status)


def record_fixture_sync_status(
    source: str,
    provider: str,
    status: str,
    result: dict | None = None,
    duration_seconds: float | None = None,
    error: str | None = None,
) -> dict:
    """
    Record the latest fixture sync runtime status for demo and dashboard usage.
    """
    global _fixture_sync_status

    now = _utc_now_iso()
    previous_last_success_at = _fixture_sync_status.get("last_success_at")

    if status == "success":
        last_success_at = now
    else:
        last_success_at = previous_last_success_at

    result = result or {}

    duration_value = _to_float(duration_seconds)

    _fixture_sync_status = {
        "status": status,
        "source": source,
        "provider": provider,
        "last_run_at": now,
        "last_success_at": last_success_at,
        "duration_seconds": duration_value,
        "total_fixtures": _to_int(result.get("total_fixtures")),
        "created": _to_int(result.get("created")),
        "updated": _to_int(result.get("updated")),
        "newly_completed_count": _to_int(result.get("newly_completed_count")),
        "newly_completed": list(result.get("newly_completed", [])),
        "last_error": str(error) if error else None,
    }

    return get_fixture_sync_status()
