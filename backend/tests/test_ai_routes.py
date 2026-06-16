class FakeLlamaClient:
    def health_check(self):
        return {
            "available": True,
            "provider": "local_llama",
            "base_url": "http://127.0.0.1:11434",
            "configured_model": "llama3.2:1b",
            "models": ["llama3.2:1b"],
        }

    def generate_summary(self, prompt: str):
        return {
            "provider": "local_llama",
            "model": "llama3.2:1b",
            "summary": "This is a test AI summary for the fixture data.",
        }


def test_ai_health_returns_local_llama_status(client, monkeypatch):
    monkeypatch.setattr("app.routes.ai.LocalLlamaClient", lambda: FakeLlamaClient())

    response = client.get("/ai/health")

    assert response.status_code == 200

    data = response.json()

    assert data["available"] is True
    assert data["provider"] == "local_llama"
    assert data["configured_model"] == "llama3.2:1b"
    assert "llama3.2:1b" in data["models"]


def test_ai_fixture_summary_requires_fixtures(client, monkeypatch):
    monkeypatch.setattr("app.routes.ai.LocalLlamaClient", lambda: FakeLlamaClient())

    response = client.get("/ai/fixtures/summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "No fixtures available to summarize."


def test_ai_fixture_summary_returns_summary(client, monkeypatch):
    monkeypatch.setattr("app.routes.ai.LocalLlamaClient", lambda: FakeLlamaClient())

    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/ai/fixtures/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["fixture_count"] == 4
    assert data["provider"] == "local_llama"
    assert data["model"] == "llama3.2:1b"
    assert data["summary"] == "This is a test AI summary for the fixture data."


def test_ai_single_fixture_summary_returns_summary(client, monkeypatch):
    monkeypatch.setattr("app.routes.ai.LocalLlamaClient", lambda: FakeLlamaClient())

    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    fixtures_response = client.get("/fixtures")
    assert fixtures_response.status_code == 200

    fixture_id = fixtures_response.json()["fixtures"][0]["id"]

    response = client.get(f"/ai/fixtures/{fixture_id}/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["fixture_id"] == fixture_id
    assert data["provider"] == "local_llama"
    assert data["model"] == "llama3.2:1b"
    assert data["summary"] == "This is a test AI summary for the fixture data."


def test_ai_single_fixture_summary_returns_404_for_missing_fixture(client, monkeypatch):
    monkeypatch.setattr("app.routes.ai.LocalLlamaClient", lambda: FakeLlamaClient())

    response = client.get("/ai/fixtures/999999/summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "Fixture not found."