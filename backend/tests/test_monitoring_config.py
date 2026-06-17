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
