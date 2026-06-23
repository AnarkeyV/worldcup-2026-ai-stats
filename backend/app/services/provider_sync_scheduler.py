import logging
import threading
import time
from collections.abc import Callable
from datetime import datetime, time as clock_time

from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import SessionLocal
from app.models.fixture import Fixture
from app.providers.api_football import ApiFootballProviderError
from app.providers.factory import get_configured_football_provider
from app.providers.zafronix import ZafronixProviderError
from app.services.fixture_sync_service import sync_fixtures
from app.services.metrics_service import (
    record_fixture_sync_metrics,
    record_notification_result,
)
from app.services.scheduled_sync_schedule import (
    get_next_scheduled_sync_run_at,
    get_scheduled_sync_runtime_status,
    parse_scheduled_sync_times,
)
from app.services.sync_observability_service import (
    record_fixture_sync_status,
    sanitize_sync_error,
)
from app.services.telegram_notifier import (
    TelegramNotificationError,
    send_scheduled_completed_fixture_digest,
)


logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    from datetime import timezone

    return datetime.now(timezone.utc).isoformat()


class ProviderSyncScheduler:
    """
    Local-only provider-sync scheduler.

    The production path uses fixed daily local-time slots. `interval_seconds`
    remains accepted only for compatibility with older tests and local scripts;
    it is not used by the configured application startup path.
    """

    def __init__(
        self,
        run_sync: Callable[[], dict],
        interval_seconds: int | None = None,
        *,
        schedule_times: str | list[clock_time] | None = None,
        timezone_name: str = "Asia/Singapore",
    ):
        self.run_sync = run_sync
        self.timezone_name = timezone_name
        self._stop_event = threading.Event()
        self._run_lock = threading.Lock()
        self._thread: threading.Thread | None = None

        if schedule_times is None:
            if interval_seconds is None:
                raise ValueError(
                    "Either interval_seconds or fixed schedule_times is required."
                )

            self.mode = "interval_legacy"
            self.interval_seconds = max(1, int(interval_seconds))
            self.schedule_times: list[clock_time] = []
        else:
            self.mode = "fixed_daily_times"
            self.interval_seconds = None
            self.schedule_times = (
                parse_scheduled_sync_times(schedule_times)
                if isinstance(schedule_times, str)
                else sorted(set(schedule_times))
            )

            if not self.schedule_times:
                raise ValueError("Provider sync schedule times are required.")

    def start(self) -> bool:
        if self._thread is not None and self._thread.is_alive():
            return False

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            name="worldcup-provider-sync-scheduler",
            daemon=True,
        )
        self._thread.start()
        return True

    def stop(self, timeout_seconds: float = 5.0) -> None:
        self._stop_event.set()

        if self._thread is not None:
            self._thread.join(timeout=timeout_seconds)

    def run_once(self) -> bool:
        if not self._run_lock.acquire(blocking=False):
            logger.warning("Skipping scheduled provider sync because another run is active.")
            return False

        try:
            self.run_sync()
            return True
        except Exception:
            logger.exception("Scheduled provider sync failed unexpectedly.")
            return True
        finally:
            self._run_lock.release()

    def _run_loop(self) -> None:
        if self.mode == "interval_legacy":
            self._run_interval_loop()
            return

        self._run_fixed_daily_times_loop()

    def _run_interval_loop(self) -> None:
        while not self._stop_event.wait(self.interval_seconds):
            self.run_once()

    def _run_fixed_daily_times_loop(self) -> None:
        while not self._stop_event.is_set():
            next_run_at = get_next_scheduled_sync_run_at(
                now=None,
                schedule_times=self.schedule_times,
                timezone_name=self.timezone_name,
            )
            wait_seconds = max(
                0.0,
                (next_run_at - datetime.now(next_run_at.tzinfo)).total_seconds(),
            )

            if self._stop_event.wait(wait_seconds):
                return

            self.run_once()


def _serialize_digest_fixture(fixture: Fixture) -> dict:
    return {
        "external_id": fixture.external_id,
        "home_team": fixture.home_team,
        "away_team": fixture.away_team,
        "home_score": fixture.home_score,
        "away_score": fixture.away_score,
        "status": fixture.status,
        "kickoff_time": fixture.kickoff_time,
    }


def _dispatch_scheduled_telegram_digest(
    db,
    newly_completed_external_ids: list[str],
) -> dict:
    fixtures: list[Fixture] = []

    if newly_completed_external_ids:
        fixtures = (
            db.query(Fixture)
            .filter(Fixture.external_id.in_(newly_completed_external_ids))
            .order_by(Fixture.kickoff_time.asc())
            .all()
        )

    serialized_fixtures = [
        _serialize_digest_fixture(fixture)
        for fixture in fixtures
    ]

    try:
        result = send_scheduled_completed_fixture_digest(
            fixtures=serialized_fixtures,
            enabled=settings.telegram_scheduled_digest_enabled,
            public_dashboard_url=settings.public_dashboard_url,
        )
        record_notification_result(
            channel="telegram",
            status=result["status"],
        )
        return result

    except ValueError as error:
        record_notification_result(
            channel="telegram",
            status="skipped",
        )
        return {
            "status": "skipped",
            "reason": str(error),
            "sent": 0,
        }

    except TelegramNotificationError as error:
        record_notification_result(
            channel="telegram",
            status="failed",
        )
        logger.warning("Scheduled Telegram digest failed: %s", error)
        return {
            "status": "failed",
            "reason": str(error),
            "sent": 0,
        }

    except SQLAlchemyError:
        db.rollback()
        record_notification_result(
            channel="telegram",
            status="failed",
        )
        logger.warning("Unable to read newly completed fixtures for Telegram digest.")
        return {
            "status": "failed",
            "reason": "Unable to prepare the scheduled Telegram digest.",
            "sent": 0,
        }

    except Exception:
        record_notification_result(
            channel="telegram",
            status="failed",
        )
        logger.warning("Scheduled Telegram digest failed unexpectedly.")
        return {
            "status": "failed",
            "reason": "Unexpected scheduled Telegram digest failure.",
            "sent": 0,
        }


def run_scheduled_provider_sync() -> dict:
    """
    Execute one scheduled provider fixture sync.

    The sync always records audit history and metrics. One Telegram digest is
    attempted only for the fixtures that transitioned to completed in this
    specific sync run, and only when the separate digest setting is enabled.
    """
    source = "provider"
    provider_name = "unknown"
    started_at = None
    start_time = time.perf_counter()
    db = SessionLocal()

    try:
        started_at = _utc_now_iso()
        provider_name, provider = get_configured_football_provider()
        fixtures = provider.get_world_cup_fixtures()
        result = sync_fixtures(db, fixtures)
        duration_seconds = time.perf_counter() - start_time

        record_fixture_sync_metrics(
            source=source,
            provider=provider_name,
            status="success",
            result=result,
            duration_seconds=duration_seconds,
        )
        record_fixture_sync_status(
            db=db,
            source=source,
            provider=provider_name,
            status="success",
            result=result,
            duration_seconds=duration_seconds,
            trigger_type="scheduled",
            started_at=started_at,
        )

        notification_result = _dispatch_scheduled_telegram_digest(
            db=db,
            newly_completed_external_ids=result["newly_completed"],
        )

        return {
            "status": "success",
            "provider": provider_name,
            "result": result,
            "notifications": notification_result,
        }

    except (ValueError, ApiFootballProviderError, ZafronixProviderError) as error:
        duration_seconds = time.perf_counter() - start_time
        error_message = sanitize_sync_error(str(error)) or "Provider sync failed."

        record_fixture_sync_metrics(
            source=source,
            provider=provider_name,
            status="error",
            duration_seconds=duration_seconds,
        )
        record_fixture_sync_status(
            db=db,
            source=source,
            provider=provider_name,
            status="error",
            duration_seconds=duration_seconds,
            error=error_message,
            trigger_type="scheduled",
            started_at=started_at,
        )

        logger.warning("Scheduled provider sync failed: %s", error_message)
        return {
            "status": "error",
            "provider": provider_name,
            "error": error_message,
        }

    except SQLAlchemyError as error:
        db.rollback()
        duration_seconds = time.perf_counter() - start_time
        error_message = sanitize_sync_error(
            f"Database error while syncing provider fixtures: {error}"
        ) or "Database error while syncing provider fixtures."

        try:
            record_fixture_sync_metrics(
                source=source,
                provider=provider_name,
                status="error",
                duration_seconds=duration_seconds,
            )
            record_fixture_sync_status(
                db=db,
                source=source,
                provider=provider_name,
                status="error",
                duration_seconds=duration_seconds,
                error=error_message,
                trigger_type="scheduled",
                started_at=started_at,
            )
        except SQLAlchemyError:
            db.rollback()
            logger.exception("Unable to persist scheduled provider sync failure.")

        logger.warning("Scheduled provider sync failed: %s", error_message)
        return {
            "status": "error",
            "provider": provider_name,
            "error": error_message,
        }

    except Exception as error:
        db.rollback()
        duration_seconds = time.perf_counter() - start_time
        error_message = sanitize_sync_error(
            f"Unexpected provider sync error: {error}"
        ) or "Unexpected provider sync error."

        try:
            record_fixture_sync_metrics(
                source=source,
                provider=provider_name,
                status="error",
                duration_seconds=duration_seconds,
            )
            record_fixture_sync_status(
                db=db,
                source=source,
                provider=provider_name,
                status="error",
                duration_seconds=duration_seconds,
                error=error_message,
                trigger_type="scheduled",
                started_at=started_at,
            )
        except SQLAlchemyError:
            db.rollback()
            logger.exception("Unable to persist scheduled provider sync failure.")

        logger.exception("Scheduled provider sync failed unexpectedly.")
        return {
            "status": "error",
            "provider": provider_name,
            "error": error_message,
        }

    finally:
        db.close()
