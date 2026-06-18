from types import SimpleNamespace
from app.services.sync_observability_service import reset_fixture_sync_status

from app.routes.ai import (
    build_deterministic_fixture_summary,
    build_deterministic_tournament_summary,
)


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


def make_completed_fixture(
    *,
    fixture_id=1,
    group_name="Group A",
    home_team="Mexico",
    away_team="South Africa",
    home_team_code="MEX",
    away_team_code="RSA",
    home_score=2,
    away_score=0,
    status="complete",
):
    return SimpleNamespace(
        id=fixture_id,
        competition="FIFA World Cup 2026",
        stage="Group Stage",
        group_name=group_name,
        home_team=home_team,
        away_team=away_team,
        home_team_code=home_team_code,
        away_team_code=away_team_code,
        kickoff_time="2026-06-11T15:00:00-04:00",
        venue="Estadio Azteca",
        status=status,
        home_score=home_score,
        away_score=away_score,
    )


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
    assert data["model"] == "rules_based_v3"
    assert isinstance(data["summary"], str)

    summary = data["summary"].lower()

    assert "4 fixtures have been completed" in summary
    assert "mexico defeated south africa" in summary
    assert "united states defeated paraguay" in summary
    assert "current group leaders based on completed fixtures include" in summary
    assert "mexico (group a, 3 pts, +2 gd)" in summary
    assert "united states (group d, 3 pts, +3 gd)" in summary
    assert "france (group i, 3 pts, +2 gd)" in summary
    assert "argentina (group j, 3 pts, +3 gd)" in summary
    assert "strongest attacks based on completed fixtures include" in summary
    assert "united states (group d, 4 gf)" in summary
    assert "argentina (group j, 3 gf)" in summary
    assert "best defences based on completed fixtures include" in summary
    assert "argentina (group j, 0 ga)" in summary
    assert "mexico (group a, 0 ga)" in summary
    assert "unbeaten teams include" in summary
    assert "upcoming" not in summary


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
    assert data["model"] == "rules_based_v3"


def test_deterministic_tournament_summary_includes_standings_leaders():
    fixtures = [
        make_completed_fixture(
            fixture_id=1,
            group_name="Group A",
            home_team="Mexico",
            away_team="South Africa",
            home_team_code="MEX",
            away_team_code="RSA",
            home_score=2,
            away_score=0,
        ),
        make_completed_fixture(
            fixture_id=2,
            group_name="Group A",
            home_team="South Korea",
            away_team="Czechia",
            home_team_code="KOR",
            away_team_code="CZE",
            home_score=2,
            away_score=1,
        ),
    ]

    summary = build_deterministic_tournament_summary(fixtures).lower()

    assert "2 fixtures have been completed" in summary
    assert "current group leaders based on completed fixtures include" in summary
    assert "mexico (group a, 3 pts, +2 gd)" in summary


def test_deterministic_tournament_summary_includes_group_analytics():
    fixtures = [
        make_completed_fixture(
            fixture_id=1,
            group_name="Group A",
            home_team="Mexico",
            away_team="South Africa",
            home_team_code="MEX",
            away_team_code="RSA",
            home_score=2,
            away_score=0,
        ),
        make_completed_fixture(
            fixture_id=2,
            group_name="Group D",
            home_team="United States",
            away_team="Paraguay",
            home_team_code="USA",
            away_team_code="PAR",
            home_score=4,
            away_score=1,
        ),
        make_completed_fixture(
            fixture_id=3,
            group_name="Group J",
            home_team="Argentina",
            away_team="Algeria",
            home_team_code="ARG",
            away_team_code="DZA",
            home_score=3,
            away_score=0,
        ),
    ]

    summary = build_deterministic_tournament_summary(fixtures).lower()

    assert "strongest attacks based on completed fixtures include" in summary
    assert "united states (group d, 4 gf)" in summary
    assert "argentina (group j, 3 gf)" in summary
    assert "best defences based on completed fixtures include" in summary
    assert "argentina (group j, 0 ga)" in summary
    assert "mexico (group a, 0 ga)" in summary
    assert "unbeaten teams include" in summary


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
    assert data["model"] == "rules_based_v2"
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


def test_ai_insights_empty_before_sync(client):
    reset_fixture_sync_status()
    response = client.get("/ai/insights")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["mode"] == "fallback"
    assert data["provider"] == "rules_based_ai_insights"
    assert data["model"] == "rules_based_v1"
    assert data["filters"] == {
        "group_name": None,
        "team": None,
        "limit": 5,
    }
    assert data["metadata"]["fixture_count"] == 0
    assert data["metadata"]["completed_count"] == 0
    assert data["metadata"]["sync_status"] == "not_started"

    titles = [insight["title"] for insight in data["insights"]]

    assert "No fixture data available" in titles
    assert "Provider sync runtime status" in titles


def test_ai_insights_after_sample_sync(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/ai/insights")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["mode"] == "fallback"
    assert data["metadata"]["fixture_count"] == 4
    assert data["metadata"]["completed_count"] == 4
    assert data["metadata"]["teams_analyzed"] == 8
    assert data["metadata"]["groups_analyzed"] == 4
    assert data["metadata"]["sync_status"] == "success"

    titles = [insight["title"] for insight in data["insights"]]

    assert "Fixture data available" in titles
    assert "Completed results detected" in titles
    assert "Group leaders available" in titles
    assert "Strongest attacks identified" in titles
    assert "Provider sync runtime status" in titles

    summary = data["summary"].lower()

    assert "4 fixtures are available for ai insights" in summary
    assert "4 completed" in summary
    assert "latest provider sync completed successfully" in summary


def test_ai_insights_can_filter_by_group_name(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/ai/insights?group_name=Group A&limit=3")

    assert response.status_code == 200

    data = response.json()

    assert data["filters"] == {
        "group_name": "Group A",
        "team": None,
        "limit": 3,
    }
    assert data["metadata"]["fixture_count"] == 1
    assert data["metadata"]["completed_count"] == 1
    assert data["metadata"]["teams_analyzed"] == 2
    assert data["metadata"]["groups_analyzed"] == 1
    assert len(data["insights"]) == 3
    assert "for Group A" in data["summary"]


def test_ai_insights_can_filter_by_team_name_or_code(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    response_by_name = client.get("/ai/insights?team=Mexico")
    response_by_code = client.get("/ai/insights?team=MEX")

    assert response_by_name.status_code == 200
    assert response_by_code.status_code == 200

    data_by_name = response_by_name.json()
    data_by_code = response_by_code.json()

    assert data_by_name["metadata"]["fixture_count"] == 1
    assert data_by_code["metadata"]["fixture_count"] == 1
    assert data_by_name["metadata"]["completed_count"] == 1
    assert data_by_code["metadata"]["completed_count"] == 1
    assert "for Mexico" in data_by_name["summary"]
    assert "for MEX" in data_by_code["summary"]


def test_ai_insights_rejects_invalid_limit(client):
    response = client.get("/ai/insights?limit=0")

    assert response.status_code == 422
