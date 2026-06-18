import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_prometheus_config_exists():
    prometheus_config = PROJECT_ROOT / "monitoring" / "prometheus.yml"

    assert prometheus_config.exists()


def test_prometheus_config_scrapes_backend_metrics_endpoint():
    prometheus_config = PROJECT_ROOT / "monitoring" / "prometheus.yml"
    text = prometheus_config.read_text()

    assert 'job_name: "worldcup-backend"' in text
    assert 'metrics_path: "/metrics"' in text
    assert '"backend:8000"' in text


def test_docker_compose_includes_prometheus_service():
    compose_file = PROJECT_ROOT / "docker-compose.yml"
    text = compose_file.read_text()

    assert "prometheus:" in text
    assert "prom/prometheus:v2.55.1" in text
    assert "worldcup-prometheus" in text
    assert '"9090:9090"' in text


def test_docker_compose_mounts_prometheus_config():
    compose_file = PROJECT_ROOT / "docker-compose.yml"
    text = compose_file.read_text()

    assert "./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro" in text
    assert "worldcup_prometheus_data" in text


def test_grafana_dashboard_json_exists_and_is_valid():
    dashboard_file = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "dashboards"
        / "worldcup-overview.json"
    )

    assert dashboard_file.exists()

    dashboard = json.loads(dashboard_file.read_text())

    assert dashboard["uid"] == "worldcup-2026-overview"
    assert dashboard["title"] == "World Cup 2026 AI Stats - Provider Sync Observability"
    assert dashboard["version"] == 3


def test_grafana_dashboard_includes_provider_sync_panels():
    dashboard_file = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "dashboards"
        / "worldcup-overview.json"
    )
    dashboard = json.loads(dashboard_file.read_text())
    panel_titles = {panel["title"] for panel in dashboard["panels"]}

    assert "Fixture Sync Runs" in panel_titles
    assert "Last Successful Fixture Sync" in panel_titles
    assert "Fixture Sync Duration" in panel_titles
    assert "Fixtures Fetched by Sync Source" in panel_titles
    assert "Fixtures Created vs Updated" in panel_titles
    assert "Newly Completed Fixtures Detected" in panel_titles


def test_grafana_dashboard_uses_fixture_sync_metrics():
    dashboard_file = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "dashboards"
        / "worldcup-overview.json"
    )
    text = dashboard_file.read_text()

    assert "worldcup_fixture_sync_runs_total" in text
    assert "worldcup_fixture_sync_duration_seconds" in text
    assert "worldcup_fixture_sync_fetched_total" in text
    assert "worldcup_fixture_sync_created_total" in text
    assert "worldcup_fixture_sync_updated_total" in text
    assert "worldcup_fixture_sync_newly_completed_total" in text
    assert "worldcup_fixture_sync_last_success_timestamp_seconds" in text
    assert "worldcup_fixture_sync_last_success_timestamp_seconds * 1000" in text


def test_grafana_provisioning_files_exist():
    datasource_file = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "provisioning"
        / "datasources"
        / "prometheus.yml"
    )
    dashboard_provider_file = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "provisioning"
        / "dashboards"
        / "dashboards.yml"
    )

    assert datasource_file.exists()
    assert dashboard_provider_file.exists()


def test_grafana_datasource_points_to_prometheus_service():
    datasource_file = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "provisioning"
        / "datasources"
        / "prometheus.yml"
    )
    text = datasource_file.read_text()

    assert "name: Prometheus" in text
    assert "uid: Prometheus" in text
    assert "url: http://prometheus:9090" in text


def test_grafana_dashboard_provider_loads_dashboard_directory():
    dashboard_provider_file = (
        PROJECT_ROOT
        / "monitoring"
        / "grafana"
        / "provisioning"
        / "dashboards"
        / "dashboards.yml"
    )
    text = dashboard_provider_file.read_text()

    assert "World Cup 2026 AI Stats Dashboards" in text
    assert "path: /var/lib/grafana/dashboards" in text
