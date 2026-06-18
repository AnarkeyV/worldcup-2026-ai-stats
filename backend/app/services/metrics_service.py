import time
from typing import Any

from prometheus_client import Counter, Gauge, Histogram

from app.config import settings


APP_INFO = Gauge(
    "worldcup_app_info",
    "World Cup 2026 AI Stats application information.",
    ["version", "environment"],
)

HTTP_REQUESTS_TOTAL = Counter(
    "worldcup_http_requests_total",
    "Total HTTP requests handled by the backend.",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "worldcup_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "path", "status_code"],
)

FIXTURE_SYNC_RUNS_TOTAL = Counter(
    "worldcup_fixture_sync_runs_total",
    "Total fixture sync runs.",
    ["source", "status"],
)

FIXTURE_SYNC_CREATED_TOTAL = Counter(
    "worldcup_fixture_sync_created_total",
    "Total fixtures created during sync.",
    ["source"],
)

FIXTURE_SYNC_UPDATED_TOTAL = Counter(
    "worldcup_fixture_sync_updated_total",
    "Total fixtures updated during sync.",
    ["source"],
)

FIXTURE_SYNC_NEWLY_COMPLETED_TOTAL = Counter(
    "worldcup_fixture_sync_newly_completed_total",
    "Total newly completed fixtures detected during sync.",
    ["source"],
)

FIXTURE_SYNC_DURATION_SECONDS = Histogram(
    "worldcup_fixture_sync_duration_seconds",
    "Fixture sync duration in seconds.",
    ["source", "provider", "status"],
)

FIXTURE_SYNC_FETCHED_TOTAL = Counter(
    "worldcup_fixture_sync_fetched_total",
    "Total fixtures fetched from the sync source before database upsert.",
    ["source", "provider"],
)

FIXTURE_SYNC_LAST_RUN_TIMESTAMP_SECONDS = Gauge(
    "worldcup_fixture_sync_last_run_timestamp_seconds",
    "Unix timestamp of the last fixture sync run.",
    ["source", "provider", "status"],
)

FIXTURE_SYNC_LAST_SUCCESS_TIMESTAMP_SECONDS = Gauge(
    "worldcup_fixture_sync_last_success_timestamp_seconds",
    "Unix timestamp of the last successful fixture sync run.",
    ["source", "provider"],
)

PLAYER_STATS_SYNC_RUNS_TOTAL = Counter(
    "worldcup_player_stats_sync_runs_total",
    "Total player stats sync runs.",
    ["source", "status"],
)

PLAYER_STATS_SYNC_CREATED_TOTAL = Counter(
    "worldcup_player_stats_sync_created_total",
    "Total player stat rows created during sync.",
    ["source"],
)

PLAYER_STATS_SYNC_UPDATED_TOTAL = Counter(
    "worldcup_player_stats_sync_updated_total",
    "Total player stat rows updated during sync.",
    ["source"],
)

NOTIFICATION_RESULTS_TOTAL = Counter(
    "worldcup_notification_results_total",
    "Total notification results.",
    ["channel", "status"],
)

AI_SUMMARY_REQUESTS_TOTAL = Counter(
    "worldcup_ai_summary_requests_total",
    "Total AI summary requests.",
    ["summary_type", "status"],
)


def _safe_metric_value(value: Any) -> float:
    try:
        if value is None:
            return 0.0

        numeric_value = float(value)

        if numeric_value < 0:
            return 0.0

        return numeric_value

    except (TypeError, ValueError):
        return 0.0


def _safe_label(value: str | None, fallback: str = "unknown") -> str:
    if value is None:
        return fallback

    cleaned_value = str(value).strip()

    if not cleaned_value:
        return fallback

    return cleaned_value


def initialize_app_info_metric() -> None:
    APP_INFO.labels(
        version=settings.app_version,
        environment=settings.app_env,
    ).set(1)


def get_request_path(request) -> str:
    route = request.scope.get("route")

    if route is not None and getattr(route, "path", None):
        return route.path

    return request.url.path


def record_http_request_metrics(
    request,
    status_code: int,
    duration_seconds: float,
) -> None:
    path = get_request_path(request)
    status_code_text = str(status_code)

    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        path=path,
        status_code=status_code_text,
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=request.method,
        path=path,
        status_code=status_code_text,
    ).observe(duration_seconds)


def record_fixture_sync_metrics(
    source: str,
    status: str,
    result: dict | None = None,
    provider: str | None = None,
    duration_seconds: float | None = None,
) -> None:
    source_label = _safe_label(source)
    status_label = _safe_label(status)
    provider_label = _safe_label(provider)

    run_timestamp = time.time()

    FIXTURE_SYNC_RUNS_TOTAL.labels(
        source=source_label,
        status=status_label,
    ).inc()

    FIXTURE_SYNC_LAST_RUN_TIMESTAMP_SECONDS.labels(
        source=source_label,
        provider=provider_label,
        status=status_label,
    ).set(run_timestamp)

    if duration_seconds is not None:
        FIXTURE_SYNC_DURATION_SECONDS.labels(
            source=source_label,
            provider=provider_label,
            status=status_label,
        ).observe(_safe_metric_value(duration_seconds))

    if status_label == "success":
        FIXTURE_SYNC_LAST_SUCCESS_TIMESTAMP_SECONDS.labels(
            source=source_label,
            provider=provider_label,
        ).set(run_timestamp)

    if result is None:
        return

    FIXTURE_SYNC_CREATED_TOTAL.labels(source=source_label).inc(
        _safe_metric_value(result.get("created", 0))
    )
    FIXTURE_SYNC_UPDATED_TOTAL.labels(source=source_label).inc(
        _safe_metric_value(result.get("updated", 0))
    )
    FIXTURE_SYNC_NEWLY_COMPLETED_TOTAL.labels(
        source=source_label,
    ).inc(_safe_metric_value(result.get("newly_completed_count", 0)))

    FIXTURE_SYNC_FETCHED_TOTAL.labels(
        source=source_label,
        provider=provider_label,
    ).inc(_safe_metric_value(result.get("total_fixtures", 0)))


def record_player_stats_sync_metrics(
    source: str,
    status: str,
    result: dict | None = None,
) -> None:
    PLAYER_STATS_SYNC_RUNS_TOTAL.labels(
        source=source,
        status=status,
    ).inc()

    if result is None:
        return

    PLAYER_STATS_SYNC_CREATED_TOTAL.labels(source=source).inc(result.get("created", 0))
    PLAYER_STATS_SYNC_UPDATED_TOTAL.labels(source=source).inc(result.get("updated", 0))


def record_notification_result(channel: str, status: str) -> None:
    NOTIFICATION_RESULTS_TOTAL.labels(
        channel=channel,
        status=status,
    ).inc()


def record_ai_summary_request(summary_type: str, status: str) -> None:
    AI_SUMMARY_REQUESTS_TOTAL.labels(
        summary_type=summary_type,
        status=status,
    ).inc()


initialize_app_info_metric()
