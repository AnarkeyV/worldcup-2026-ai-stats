import logging
import threading
import time
from datetime import datetime, timezone
from collections.abc import Callable

from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.providers.api_football import ApiFootballProviderError
from app.providers.factory import get_configured_football_provider
from app.providers.zafronix import ZafronixProviderError
from app.services.fixture_sync_service import sync_fixtures
from app.services.metrics_service import record_fixture_sync_metrics
from app.services.sync_observability_service import (
    record_fixture_sync_status,
    sanitize_sync_error,
)


logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProviderSyncScheduler:
    """
    Small, local-only scheduler for explicitly enabled provider fixture syncs.

    It waits a full interval before the first run and serializes execution with
    a lock. Scheduled runs never dispatch Telegram notifications.
    """

    def __init__(
        self,
        run_sync: Callable[[], dict],
        interval_seconds: int,
    ):
        self.run_sync = run_sync
        self.interval_seconds = max(1, int(interval_seconds))
        self._stop_event = threading.Event()
        self._run_lock = threading.Lock()
        self._thread: threading.Thread | None = None

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
        while not self._stop_event.wait(self.interval_seconds):
            self.run_once()


def run_scheduled_provider_sync() -> dict:
    """
    Execute one provider fixture sync for the scheduler.

    This function deliberately records audit history and metrics only. It never
    invokes completed-match Telegram delivery, rich-detail backfill, or any
    route handler.
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

        return {
            "status": "success",
            "provider": provider_name,
            "result": result,
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
