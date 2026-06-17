from types import SimpleNamespace

from app.routes.ai import build_deterministic_fixture_summary


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


def test_ai_fixture_summary_returns_deterministic_tournament_summary(client, monkeypatch):
    monkeypatch.setattr("app.routes.ai.LocalLlamaClient", lambda: FakeLlamaClient())

    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/ai/fixtures/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["fixture_count"] == 4
    assert data["provider"] == "deterministic_tournament_summary"
    assert data["model"] == "rules_based_v1"
    assert isinstance(data["summary"], str)
    assert "4 fixtures have been completed" in data["summary"].lower()
    assert "mexico defeated south africa" in data["summary"].lower()
    assert "united states defeated paraguay" in data["summary"].lower()
    assert "upcoming" not in data["summary"].lower()


def test_ai_fixture_summary_does_not_depend_on_llama_generation(client, monkeypatch):
    class BrokenLlamaClient(FakeLlamaClient):
        def generate_summary(self, prompt: str):
            raise RuntimeError("Llama should not be called for tournament summary.")

    monkeypatch.setattr("app.routes.ai.LocalLlamaClient", lambda: BrokenLlamaClient())

    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/ai/fixtures/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["provider"] == "deterministic_tournament_summary"
    assert data["model"] == "rules_based_v1"


def test_ai_single_fixture_summary_returns_deterministic_summary(client, monkeypatch):
    monkeypatch.setattr("app.routes.ai.LocalLlamaClient", lambda: FakeLlamaClient())

    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    fixtures_response = client.get("/fixtures")
    assert fixtures_response.status_code == 200

    fixture = fixtures_response.json()["fixtures"][0]
    fixture_id = fixture["id"]

    response = client.get(f"/ai/fixtures/{fixture_id}/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["fixture_id"] == fixture_id
    assert data["provider"] == "deterministic_fixture_summary"
    assert data["model"] == "rules_based_v1"
    assert isinstance(data["summary"], str)
    assert fixture["home_team"] in data["summary"]
    assert fixture["away_team"] in data["summary"]


def test_ai_single_completed_fixture_summary_is_factual(client, monkeypatch):
    monkeypatch.setattr("app.routes.ai.LocalLlamaClient", lambda: FakeLlamaClient())

    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    fixtures_response = client.get("/fixtures?status=complete")
    assert fixtures_response.status_code == 200

    completed_fixture = fixtures_response.json()["fixtures"][0]
    fixture_id = completed_fixture["id"]

    response = client.get(f"/ai/fixtures/{fixture_id}/summary")

    assert response.status_code == 200

    data = response.json()
    summary = data["summary"].lower()

    assert data["provider"] == "deterministic_fixture_summary"
    assert "complete" in summary
    assert str(completed_fixture["home_score"]) in data["summary"]
    assert str(completed_fixture["away_score"]) in data["summary"]
    assert "upcoming fixture" not in summary
    assert "has not been played" not in summary


def test_deterministic_scheduled_fixture_summary_does_not_invent_score():
    scheduled_fixture = SimpleNamespace(
        home_team="France",
        away_team="Senegal",
        group_name="Group I",
        kickoff_time="2026-06-16T15:00:00-04:00",
        venue="MetLife Stadium",
        status="scheduled",
        home_score=None,
        away_score=None,
    )

    summary = build_deterministic_fixture_summary(scheduled_fixture)
    normalized_summary = summary.lower()

    assert "upcoming fixture" in normalized_summary
    assert "no score is available yet" in normalized_summary
    assert "has not been played" in normalized_summary
    assert "3-1" not in normalized_summary


def test_ai_single_fixture_summary_returns_404_for_missing_fixture(client, monkeypatch):
    monkeypatch.setattr("app.routes.ai.LocalLlamaClient", lambda: FakeLlamaClient())

    response = client.get("/ai/fixtures/999999/summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "Fixture not found."
