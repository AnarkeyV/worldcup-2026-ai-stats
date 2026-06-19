import app.routes.fixtures as fixtures_routes
from app.providers.api_football import ApiFootballProviderError


def test_list_fixtures_empty_before_sync(client):
    response = client.get("/fixtures")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 0
    assert data["filters"] == {
        "group_name": None,
        "status": None,
        "team": None,
    }
    assert data["fixtures"] == []


def test_sync_sample_fixtures(client):
    response = client.post("/fixtures/sync/sample")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Sample fixtures synced successfully"
    assert data["created"] == 4
    assert data["updated"] == 0
    assert data["total_sample_fixtures"] == 4
    assert data["newly_completed_count"] == 4
    assert data["newly_completed"] == [
        "sample-mex-rsa-2026-06-11",
        "sample-usa-par-2026-06-12",
        "sample-fra-sen-2026-06-16",
        "sample-arg-dza-2026-06-16",
    ]
    assert data["notifications"]["status"] == "skipped"
    assert data["notifications"]["reason"] == "TELEGRAM_BOT_TOKEN is not configured."
    assert data["notifications"]["sent"] == 0


def test_list_fixtures_after_sync(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/fixtures")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 4
    assert data["filters"] == {
        "group_name": None,
        "status": None,
        "team": None,
    }
    assert len(data["fixtures"]) == 4

    first_fixture = data["fixtures"][0]

    assert "external_id" in first_fixture
    assert "home_team" in first_fixture
    assert "away_team" in first_fixture
    assert "status" in first_fixture


def test_list_fixtures_filters_by_group_name(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/fixtures?group_name=Group A")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["filters"]["group_name"] == "Group A"
    assert data["filters"]["status"] is None
    assert data["filters"]["team"] is None

    for fixture in data["fixtures"]:
        assert fixture["group_name"] == "Group A"


def test_list_fixtures_filters_by_status(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/fixtures?status=complete")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 4
    assert data["filters"]["group_name"] is None
    assert data["filters"]["status"] == "complete"
    assert data["filters"]["team"] is None

    for fixture in data["fixtures"]:
        assert fixture["status"] == "complete"


def test_list_fixtures_filters_by_team_name(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/fixtures?team=Mexico")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["filters"]["team"] == "Mexico"

    fixture = data["fixtures"][0]

    assert fixture["home_team"] == "Mexico"
    assert fixture["away_team"] == "South Africa"


def test_list_fixtures_filters_by_team_code(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/fixtures?team=USA")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["filters"]["team"] == "USA"

    fixture = data["fixtures"][0]

    assert fixture["home_team"] == "United States"
    assert fixture["home_team_code"] == "USA"


def test_list_fixtures_filters_by_group_and_status(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/fixtures?group_name=Group A&status=complete")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["filters"]["group_name"] == "Group A"
    assert data["filters"]["status"] == "complete"
    assert data["filters"]["team"] is None

    fixture = data["fixtures"][0]

    assert fixture["group_name"] == "Group A"
    assert fixture["status"] == "complete"
    assert fixture["home_team"] == "Mexico"


def test_list_fixtures_returns_empty_for_no_filter_matches(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/fixtures?team=Brazil")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 0
    assert data["filters"]["team"] == "Brazil"
    assert data["fixtures"] == []


def test_get_fixture_by_id(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    list_response = client.get("/fixtures")
    assert list_response.status_code == 200

    fixtures = list_response.json()["fixtures"]
    fixture_id = fixtures[0]["id"]

    response = client.get(f"/fixtures/{fixture_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == fixture_id
    assert data["competition"] == "FIFA World Cup 2026"


def test_get_missing_fixture_returns_404(client):
    response = client.get("/fixtures/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Fixture not found"


def test_sync_sample_fixtures_is_idempotent(client):
    first_response = client.post("/fixtures/sync/sample")
    assert first_response.status_code == 200

    second_response = client.post("/fixtures/sync/sample")
    assert second_response.status_code == 200

    data = second_response.json()

    assert data["created"] == 0
    assert data["updated"] == 4
    assert data["total_sample_fixtures"] == 4
    assert data["newly_completed_count"] == 0
    assert data["newly_completed"] == []
    assert data["notifications"]["status"] == "skipped"
    assert data["notifications"]["reason"] == "No newly completed fixtures"
    assert data["notifications"]["sent"] == 0

    list_response = client.get("/fixtures")
    assert list_response.status_code == 200

    fixtures_data = list_response.json()

    assert fixtures_data["count"] == 4


def test_sync_provider_fixtures_without_api_key(client):
    response = client.post("/fixtures/sync/provider")

    assert response.status_code == 400
    assert response.json()["detail"] == "API_FOOTBALL_KEY is not configured."


def test_sync_provider_fixtures_with_mocked_provider(client, monkeypatch):
    class MockProvider:
        def get_world_cup_fixtures(self):
            return [
                {
                    "external_id": "provider-mex-rsa-2026-06-11",
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

    response = client.post("/fixtures/sync/provider")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Provider fixtures synced successfully"
    assert data["provider"] == "api_football"
    assert data["created"] == 1
    assert data["updated"] == 0
    assert data["total_provider_fixtures"] == 1
    assert data["newly_completed_count"] == 0
    assert data["newly_completed"] == []
    assert data["notifications"]["status"] == "skipped"
    assert data["notifications"]["reason"] == "No newly completed fixtures"
    assert data["notifications"]["sent"] == 0

    list_response = client.get("/fixtures")
    assert list_response.status_code == 200

    fixtures = list_response.json()["fixtures"]

    assert len(fixtures) == 1
    assert fixtures[0]["external_id"] == "provider-mex-rsa-2026-06-11"
    assert fixtures[0]["status"] == "scheduled"


def test_sync_provider_fixtures_returns_502_when_provider_fails(client, monkeypatch):
    class MockProvider:
        def get_world_cup_fixtures(self):
            raise ApiFootballProviderError(
                "API-Football request failed: network unavailable"
            )

    monkeypatch.setattr(
        fixtures_routes,
        "get_configured_football_provider",
        lambda: ("api_football", MockProvider()),
    )

    response = client.post("/fixtures/sync/provider")

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "API-Football request failed: network unavailable"
    )