from datetime import datetime, time as clock_time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def get_schedule_timezone(timezone_name: str) -> ZoneInfo:
    cleaned_timezone_name = str(timezone_name or "").strip()

    if not cleaned_timezone_name:
        raise ValueError("Provider sync schedule timezone is required.")

    try:
        return ZoneInfo(cleaned_timezone_name)
    except ZoneInfoNotFoundError as error:
        raise ValueError(
            f"Provider sync schedule timezone is invalid: {cleaned_timezone_name}"
        ) from error


def parse_scheduled_sync_times(schedule_times_raw: str) -> list[clock_time]:
    """
    Parse comma-separated daily HH:MM provider-sync times.

    Values are normalized, sorted, and deduplicated so the scheduler can make
    one deterministic decision for every configured daily slot.
    """
    raw_values = [
        value.strip()
        for value in str(schedule_times_raw or "").split(",")
        if value.strip()
    ]

    if not raw_values:
        raise ValueError("Provider sync schedule times are required.")

    parsed_times: set[clock_time] = set()

    for raw_value in raw_values:
        try:
            parsed_time = datetime.strptime(raw_value, "%H:%M").time()
        except ValueError as error:
            raise ValueError(
                "Provider sync schedule times must use 24-hour HH:MM values."
            ) from error

        parsed_times.add(parsed_time)

    return sorted(parsed_times)


def get_next_scheduled_sync_run_at(
    now: datetime | None,
    schedule_times: list[clock_time],
    timezone_name: str,
) -> datetime:
    """
    Return the first configured daily slot strictly after `now`.

    The strict comparison deliberately prevents an immediate catch-up sync when
    the backend starts after a configured time or restarts at a slot boundary.
    """
    timezone = get_schedule_timezone(timezone_name)

    if not schedule_times:
        raise ValueError("Provider sync schedule times are required.")

    if now is None:
        localized_now = datetime.now(timezone)
    elif now.tzinfo is None:
        localized_now = now.replace(tzinfo=timezone)
    else:
        localized_now = now.astimezone(timezone)

    normalized_times = sorted(set(schedule_times))

    for day_offset in range(0, 2):
        run_date = localized_now.date() + timedelta(days=day_offset)

        for scheduled_time in normalized_times:
            candidate = datetime.combine(
                run_date,
                scheduled_time,
                tzinfo=timezone,
            )

            if candidate > localized_now:
                return candidate

    raise RuntimeError("Unable to determine the next provider sync run.")


def get_scheduled_sync_runtime_status(
    enabled: bool,
    schedule_times_raw: str,
    timezone_name: str,
    now: datetime | None = None,
) -> dict:
    schedule_times = parse_scheduled_sync_times(schedule_times_raw)
    timezone = get_schedule_timezone(timezone_name)
    next_run_at = get_next_scheduled_sync_run_at(
        now=now,
        schedule_times=schedule_times,
        timezone_name=timezone.key,
    )

    return {
        "enabled": bool(enabled),
        "mode": "fixed_daily_times",
        "timezone": timezone.key,
        "scheduled_times": [
            scheduled_time.strftime("%H:%M")
            for scheduled_time in schedule_times
        ],
        "next_run_at": next_run_at.isoformat(),
    }
