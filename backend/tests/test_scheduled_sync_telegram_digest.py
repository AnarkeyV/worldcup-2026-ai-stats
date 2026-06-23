from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import Settings
from app.services import provider_sync_scheduler
from app.services import telegram_notifier


SINGAPORE = ZoneInfo("Asia/Singapore")
SCHEDULE_TIMES = "03:45,09:45,12:45"
PUBLIC_DASHBOARD_URL = "https://wc2026.khairulrizal.qzz.io/dashboard"
COMPLETED_FIXTURES = [
    {
        "external_id": "france-iraq-2026-06-22",
        "home_team": "France",
        "away_team": "Iraq",
        "home_score": 3,
        "away_score": 0,
        "status": "complete",
        "kickoff_time": "2026-06-22T21:00:00.000Z",
    },
    {
        "external_id": "argentina-austria-2026-06-22",
        "home_team": "Argentina",
        "away_team": "Austria",
        "home_score": 2,
        "away_score": 0,
        "status": "complete",
        "kickoff_time": "2026-06-22T17:00:00.000Z",
    },
]


def _required_callable(module, name):
    value = getattr(module, name, None)

    assert callable(value), (
        f"{module.__name__}.{name} must exist for the scheduled sync and "
        "Telegram digest workflow."
    )

    return value


def test_settings_default_to_singapore_fixed_times_and_digest_opt_in_off():
    settings = Settings(_env_file=None)

    assert settings.provider_sync_scheduler_enabled is False
    assert settings.provider_sync_schedule_timezone == "Asia/Singapore"
    assert settings.provider_sync_schedule_times == SCHEDULE_TIMES
    assert settings.telegram_scheduled_digest_enabled is False


def test_parse_scheduled_sync_times_normalizes_sorts_and_deduplicates_slots():
    parse_times = _required_callable(
        provider_sync_scheduler,
        "parse_scheduled_sync_times",
    )

    parsed = parse_times("12:45, 03:45,09:45,03:45")

    assert [value.strftime("%H:%M") for value in parsed] == [
        "03:45",
        "09:45",
        "12:45",
    ]


def test_next_scheduled_sync_run_uses_next_future_slot_without_restart_catch_up():
    parse_times = _required_callable(
        provider_sync_scheduler,
        "parse_scheduled_sync_times",
    )
    get_next_run = _required_callable(
        provider_sync_scheduler,
        "get_next_scheduled_sync_run_at",
    )
    run_times = parse_times(SCHEDULE_TIMES)

    next_run = get_next_run(
        now=datetime(2026, 6, 24, 9, 50, tzinfo=SINGAPORE),
        schedule_times=run_times,
        timezone_name="Asia/Singapore",
    )

    assert next_run == datetime(2026, 6, 24, 12, 45, tzinfo=SINGAPORE)


def test_scheduled_sync_runtime_status_reports_fixed_times_and_next_run():
    build_status = _required_callable(
        provider_sync_scheduler,
        "get_scheduled_sync_runtime_status",
    )

    status = build_status(
        enabled=True,
        schedule_times_raw=SCHEDULE_TIMES,
        timezone_name="Asia/Singapore",
        now=datetime(2026, 6, 24, 9, 50, tzinfo=SINGAPORE),
    )

    assert status["enabled"] is True
    assert status["mode"] == "fixed_daily_times"
    assert status["timezone"] == "Asia/Singapore"
    assert status["scheduled_times"] == ["03:45", "09:45", "12:45"]
    assert status["next_run_at"] == "2026-06-24T12:45:00+08:00"


def test_scheduled_digest_is_disabled_by_default_and_sends_nothing(monkeypatch):
    send_digest = _required_callable(
        telegram_notifier,
        "send_scheduled_completed_fixture_digest",
    )
    messages = []

    monkeypatch.setattr(
        telegram_notifier,
        "send_telegram_message",
        lambda message: messages.append(message) or {"ok": True},
    )

    result = send_digest(
        COMPLETED_FIXTURES,
        enabled=False,
        public_dashboard_url=PUBLIC_DASHBOARD_URL,
    )

    assert result == {
        "status": "skipped",
        "reason": "Scheduled Telegram digest is disabled by configuration.",
        "sent": 0,
    }
    assert messages == []


def test_scheduled_digest_sends_one_roundup_for_all_newly_completed_fixtures(monkeypatch):
    send_digest = _required_callable(
        telegram_notifier,
        "send_scheduled_completed_fixture_digest",
    )
    messages = []

    monkeypatch.setattr(
        telegram_notifier,
        "send_telegram_message",
        lambda message: messages.append(message) or {"ok": True},
    )

    result = send_digest(
        COMPLETED_FIXTURES,
        enabled=True,
        public_dashboard_url=PUBLIC_DASHBOARD_URL,
    )

    assert result["status"] == "sent"
    assert result["sent"] == 1
    assert result["fixture_count"] == 2
    assert len(messages) == 1
    assert "France 3–0 Iraq" in messages[0]
    assert "Argentina 2–0 Austria" in messages[0]
    assert PUBLIC_DASHBOARD_URL in messages[0]


def test_scheduled_digest_skips_empty_completed_fixture_list(monkeypatch):
    send_digest = _required_callable(
        telegram_notifier,
        "send_scheduled_completed_fixture_digest",
    )
    messages = []

    monkeypatch.setattr(
        telegram_notifier,
        "send_telegram_message",
        lambda message: messages.append(message) or {"ok": True},
    )

    result = send_digest(
        [],
        enabled=True,
        public_dashboard_url=PUBLIC_DASHBOARD_URL,
    )

    assert result == {
        "status": "skipped",
        "reason": "No newly completed fixtures",
        "sent": 0,
    }
    assert messages == []
