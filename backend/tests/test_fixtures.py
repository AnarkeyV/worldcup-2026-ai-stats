def test_list_fixtures_empty_before_sync(client):
    response = client.get("/fixtures")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 0
    assert data["fixtures"] == []


def test_sync_sample_fixtures(client):
    response = client.post("/fixtures/sync/sample")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Sample fixtures synced successfully"
    assert data["created"] == 4
    assert data["updated"] == 0
    assert data["total_sample_fixtures"] == 4


def test_list_fixtures_after_sync(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/fixtures")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 4
    assert len(data["fixtures"]) == 4

    first_fixture = data["fixtures"][0]

    assert "external_id" in first_fixture
    assert "home_team" in first_fixture
    assert "away_team" in first_fixture
    assert "status" in first_fixture


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

    list_response = client.get("/fixtures")
    assert list_response.status_code == 200

    fixtures_data = list_response.json()

    assert fixtures_data["count"] == 4

def test_sync_provider_fixtures_without_api_key(client):
    response = client.post("/fixtures/sync/provider")

    assert response.status_code == 400
    assert response.json()["detail"] == "API_FOOTBALL_KEY is not configured."