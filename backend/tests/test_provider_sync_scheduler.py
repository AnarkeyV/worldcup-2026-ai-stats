import threading
import time

from app.models.fixture_sync_run import FixtureSyncRun
from app.services import provider_sync_scheduler


def test_scheduler_waits_before_its_first_run():
    calls = []
    scheduler = provider_sync_scheduler.ProviderSyncScheduler(
        run_sync=lambda: calls.append("run") or {},
        interval_seconds=60,
    )

    started = scheduler.start()

    try:
        time.sleep(0.02)
    finally:
        scheduler.stop()

    assert started is True
    assert calls == []


def test_scheduler_prevents_overlapping_runs():
    entered = threading.Event()
    release = threading.Event()
    results = []

    def blocking_run():
        entered.set()
        release.wait(timeout=1)
        return {}

    scheduler = provider_sync_scheduler.ProviderSyncScheduler(
        run_sync=blocking_run,
        interval_seconds=60,
    )

    worker = threading.Thread(target=lambda: results.append(scheduler.run_once()))
    worker.start()

    assert entered.wait(timeout=1) is True
    assert scheduler.run_once() is False

    release.set()
    worker.join(timeout=1)

    assert results == [True]


def test_scheduler_runs_one_controlled_sync_when_invoked():
    calls = []
    scheduler = provider_sync_scheduler.ProviderSyncScheduler(
        run_sync=lambda: calls.append("run") or {"status": "success"},
        interval_seconds=60,
    )

    assert scheduler.run_once() is True
    assert calls == ["run"]


def test_scheduled_provider_sync_records_audit_history_without_telegram(
    db_session,
    monkeypatch,
):
    class MockProvider:
        def get_world_cup_fixtures(self):
            return [
                {
                    "external_id": "scheduled-completed-001",
                    "competition": "FIFA World Cup 2026",
                    "stage": "Group Stage",
                    "group_name": "Group A",
                    "home_team": "Mexico",
                    "away_team": "South Africa",
                    "home_team_code": "MEX",
                    "away_team_code": "RSA",
                    "kickoff_time": "2026-06-11T19:00:00+00:00",
                    "venue": "Mexico City Stadium",
                    "status": "complete",
                    "home_score": 2,
                    "away_score": 0,
                }
            ]

    telegram_calls = []

    monkeypatch.setattr(
        provider_sync_scheduler,
        "SessionLocal",
        lambda: db_session,
    )
    monkeypatch.setattr(
        provider_sync_scheduler,
        "get_configured_football_provider",
        lambda: ("api_football", MockProvider()),
    )
    monkeypatch.setattr(
        "app.services.telegram_notifier.send_completed_fixture_notifications",
        lambda fixtures: telegram_calls.append(fixtures),
    )

    result = provider_sync_scheduler.run_scheduled_provider_sync()

    assert result["status"] == "success"
    assert result["provider"] == "api_football"
    assert telegram_calls == []

    runs = db_session.query(FixtureSyncRun).all()

    assert len(runs) == 1
    assert runs[0].trigger_type == "scheduled"
    assert runs[0].status == "success"
    assert runs[0].newly_completed == ["scheduled-completed-001"]
