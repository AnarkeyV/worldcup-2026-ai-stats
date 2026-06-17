def test_metrics_endpoint_loads(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "worldcup_app_info" in response.text
    assert "worldcup_http_requests_total" in response.text


def test_root_includes_metrics_link(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["metrics"] == "/metrics"


def test_metrics_records_http_requests(client):
    health_response = client.get("/health")

    assert health_response.status_code == 200

    metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200
    assert "worldcup_http_requests_total" in metrics_response.text
    assert 'method="GET"' in metrics_response.text
    assert 'path="/health"' in metrics_response.text
    assert 'status_code="200"' in metrics_response.text


def test_fixture_sample_sync_records_metrics(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200
    assert "worldcup_fixture_sync_runs_total" in metrics_response.text
    assert 'source="sample"' in metrics_response.text
    assert 'status="success"' in metrics_response.text
    assert "worldcup_fixture_sync_created_total" in metrics_response.text
    assert "worldcup_fixture_sync_newly_completed_total" in metrics_response.text


def test_player_stats_sample_sync_records_metrics(client):
    sync_response = client.post("/players/stats/sync/sample")

    assert sync_response.status_code == 200

    metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200
    assert "worldcup_player_stats_sync_runs_total" in metrics_response.text
    assert 'source="sample"' in metrics_response.text
    assert 'status="success"' in metrics_response.text
    assert "worldcup_player_stats_sync_created_total" in metrics_response.text


def test_ai_summary_records_metrics(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    summary_response = client.get("/ai/fixtures/summary")

    assert summary_response.status_code == 200

    metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200
    assert "worldcup_ai_summary_requests_total" in metrics_response.text
    assert 'summary_type="tournament"' in metrics_response.text
    assert 'status="success"' in metrics_response.text


def test_notification_test_endpoint_records_skipped_metric_when_credentials_missing(client):
    notification_response = client.post("/notifications/telegram/test")

    assert notification_response.status_code == 400

    metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200
    assert "worldcup_notification_results_total" in metrics_response.text
    assert 'channel="telegram"' in metrics_response.text
    assert 'status="skipped"' in metrics_response.text
