import app.routes.fixtures as fixtures_routes
from app.providers.api_football import ApiFootballProviderError


def test_fixture_sync_status_defaults_to_not_started(client):
    response = client.get("/fixtures/sync/status")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "not_started"
    assert data["source"] is None
    assert data["provider"] is None
    assert data["trigger_type"] is None
    assert data["last_run_at"] is None
    assert data["last_success_at"] is None
    assert data["duration_seconds"] is None
    assert data["total_fixtures"] == 0
    assert data["created"] == 0
    assert data["updated"] == 0
    assert data["newly_completed_count"] == 0
    assert data["newly_completed"] == []
    assert data["last_error"] is None
    assert data["freshness"]["state"] == "not_started"
    assert data["freshness"]["data_age_seconds"] is None
    assert data["scheduler"]["enabled"] is False
    assert data["completed_match_alerts_enabled"] is False


def test_sample_fixture_sync_persists_runtime_status_and_history(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    status_response = client.get("/fixtures/sync/status")

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["status"] == "success"
    assert data["source"] == "sample"
    assert data["provider"] == "sample_data"
    assert data["trigger_type"] == "manual"
    assert data["last_run_at"] is not None
    assert data["last_success_at"] is not None
    assert data["duration_seconds"] >= 0
    assert data["total_fixtures"] == 4
    assert data["created"] == 4
    assert data["updated"] == 0
    assert data["newly_completed_count"] == 4
    assert data["newly_completed"] == [
        "sample-mex-rsa-2026-06-11",
        "sample-usa-par-2026-06-12",
        "sample-fra-sen-2026-06-16",
        "sample-arg-dza-2026-06-16",
    ]
    assert data["last_error"] is None
    assert data["freshness"]["state"] == "fresh"
    assert data["freshness"]["data_age_seconds"] >= 0

    history_response = client.get("/fixtures/sync/history?limit=10")

    assert history_response.status_code == 200

    history = history_response.json()

    assert history["count"] == 1
    assert len(history["runs"]) == 1

    run = history["runs"][0]
    assert run["source"] == "sample"
    assert run["provider"] == "sample_data"
    assert run["trigger_type"] == "manual"
    assert run["status"] == "success"
    assert run["started_at"] is not None
    assert run["completed_at"] is not None
    assert run["last_error"] is None


def test_fixture_sync_history_keeps_multiple_runs_in_reverse_chronological_order(client):
    first_response = client.post("/fixtures/sync/sample")
    second_response = client.post("/fixtures/sync/sample")

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    history_response = client.get("/fixtures/sync/history?limit=10")

    assert history_response.status_code == 200

    data = history_response.json()

    assert data["count"] == 2
    assert [run["status"] for run in data["runs"]] == ["success", "success"]
    assert data["runs"][0]["id"] > data["runs"][1]["id"]
    assert data["runs"][0]["updated"] == 4
    assert data["runs"][1]["created"] == 4


def test_provider_fixture_sync_persists_status(client, monkeypatch):
    class MockProvider:
        def get_world_cup_fixtures(self):
            return [
                {
                    "external_id": "provider-observability-1",
                    "competition": "FIFA World Cup 2026",
                    "stage": "Group Stage - 1",
                    "group_name": "Group Stage - 1",
                    "home_team": "Mexico",
                    "away_team": "South Africa",
                    "home_team_code": "MEX",
                    "away_team_code": "RSA",
                    "kickoff_time": "2026-06-11T19:00:00+00:00",
                    "venue": "Estadio Azteca",
                    "status": "scheduled",
                    "home_score": None,
                    "away_score": None,
                }
            ]

    monkeypatch.setattr(
        fixtures_routes,
        "get_configured_football_provider",
        lambda: ("api_football", MockProvider()),
    )

    sync_response = client.post("/fixtures/sync/provider")

    assert sync_response.status_code == 200

    status_response = client.get("/fixtures/sync/status")

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["status"] == "success"
    assert data["source"] == "provider"
    assert data["provider"] == "api_football"
    assert data["trigger_type"] == "manual"
    assert data["last_run_at"] is not None
    assert data["last_success_at"] is not None
    assert data["duration_seconds"] >= 0
    assert data["total_fixtures"] == 1
    assert data["created"] == 1
    assert data["updated"] == 0
    assert data["newly_completed_count"] == 0
    assert data["newly_completed"] == []
    assert data["last_error"] is None


def test_failed_sync_keeps_last_success_and_marks_freshness_failed(client, monkeypatch):
    first_response = client.post("/fixtures/sync/sample")
    assert first_response.status_code == 200

    class MockProvider:
        def get_world_cup_fixtures(self):
            raise ApiFootballProviderError("provider unavailable for demo")

    monkeypatch.setattr(
        fixtures_routes,
        "get_configured_football_provider",
        lambda: ("api_football", MockProvider()),
    )

    sync_response = client.post("/fixtures/sync/provider")

    assert sync_response.status_code == 502
    assert sync_response.json()["detail"] == "provider unavailable for demo"

    status_response = client.get("/fixtures/sync/status")

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["status"] == "error"
    assert data["source"] == "provider"
    assert data["provider"] == "api_football"
    assert data["last_run_at"] is not None
    assert data["last_success_at"] is not None
    assert data["duration_seconds"] >= 0
    assert data["total_fixtures"] == 0
    assert data["created"] == 0
    assert data["updated"] == 0
    assert data["newly_completed_count"] == 0
    assert data["newly_completed"] == []
    assert data["last_error"] == "provider unavailable for demo"
    assert data["freshness"]["state"] == "last_sync_failed"


def test_sync_history_redacts_configured_secret_from_error(client, monkeypatch):
    monkeypatch.setattr(
        "app.services.sync_observability_service.settings.api_football_key",
        "very-secret-api-key",
    )

    class MockProvider:
        def get_world_cup_fixtures(self):
            raise ApiFootballProviderError(
                "Provider request rejected token very-secret-api-key"
            )

    monkeypatch.setattr(
        fixtures_routes,
        "get_configured_football_provider",
        lambda: ("api_football", MockProvider()),
    )

    sync_response = client.post("/fixtures/sync/provider")

    assert sync_response.status_code == 502
    assert "very-secret-api-key" not in sync_response.json()["detail"]
    assert "[redacted]" in sync_response.json()["detail"]

    status_response = client.get("/fixtures/sync/status")
    assert status_response.status_code == 200
    assert "very-secret-api-key" not in status_response.json()["last_error"]
    assert "[redacted]" in status_response.json()["last_error"]


def test_sample_fixture_sync_exposes_runtime_metrics(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200

    text = metrics_response.text

    assert "worldcup_fixture_sync_duration_seconds" in text
    assert "worldcup_fixture_sync_fetched_total" in text
    assert "worldcup_fixture_sync_last_run_timestamp_seconds" in text
    assert "worldcup_fixture_sync_last_success_timestamp_seconds" in text
    assert 'source="sample"' in text
    assert 'provider="sample_data"' in text
    assert 'status="success"' in text
