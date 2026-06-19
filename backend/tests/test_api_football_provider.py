import httpx
import pytest

from app.providers.api_football import ApiFootballProvider, ApiFootballProviderError


class MockResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_api_football_provider_normalizes_scheduled_fixture(monkeypatch):
    def mock_get(url, headers, params, timeout):
        assert url == "https://v3.football.api-sports.io/fixtures"
        assert headers["x-apisports-key"] == "test-key"
        assert params["league"] == 1
        assert params["season"] == 2026
        assert timeout == 20.0

        return MockResponse(
            {
                "response": [
                    {
                        "fixture": {
                            "id": 12345,
                            "date": "2026-06-11T19:00:00+00:00",
                            "venue": {
                                "name": "Estadio Azteca",
                            },
                            "status": {
                                "short": "NS",
                            },
                        },
                        "league": {
                            "name": "FIFA World Cup",
                            "round": "Group Stage - 1",
                        },
                        "teams": {
                            "home": {
                                "name": "Mexico",
                            },
                            "away": {
                                "name": "South Africa",
                            },
                        },
                        "goals": {
                            "home": None,
                            "away": None,
                        },
                    }
                ]
            }
        )

    monkeypatch.setattr(httpx, "get", mock_get)

    provider = ApiFootballProvider()
    provider.api_key = "test-key"

    fixtures = provider.get_world_cup_fixtures()

    assert len(fixtures) == 1

    fixture = fixtures[0]

    assert fixture["external_id"] == "12345"
    assert fixture["competition"] == "FIFA World Cup"
    assert fixture["stage"] == "Group Stage - 1"
    assert fixture["group_name"] == "Group Stage - 1"
    assert fixture["home_team"] == "Mexico"
    assert fixture["away_team"] == "South Africa"
    assert fixture["home_team_code"] == "MEX"
    assert fixture["away_team_code"] == "RSA"
    assert fixture["kickoff_time"] == "2026-06-11T19:00:00+00:00"
    assert fixture["venue"] == "Estadio Azteca"
    assert fixture["status"] == "scheduled"
    assert fixture["home_score"] is None
    assert fixture["away_score"] is None


def test_api_football_provider_normalizes_completed_fixture(monkeypatch):
    def mock_get(url, headers, params, timeout):
        return MockResponse(
            {
                "response": [
                    {
                        "fixture": {
                            "id": 98765,
                            "date": "2026-06-16T19:00:00+00:00",
                            "venue": {
                                "name": "MetLife Stadium",
                            },
                            "status": {
                                "short": "FT",
                            },
                        },
                        "league": {
                            "name": "FIFA World Cup",
                            "round": "Group Stage - 2",
                        },
                        "teams": {
                            "home": {
                                "name": "France",
                                "code": "FRA",
                            },
                            "away": {
                                "name": "Senegal",
                                "code": "SEN",
                            },
                        },
                        "goals": {
                            "home": 3,
                            "away": 1,
                        },
                    }
                ]
            }
        )

    monkeypatch.setattr(httpx, "get", mock_get)

    provider = ApiFootballProvider()
    provider.api_key = "test-key"

    fixtures = provider.get_world_cup_fixtures()

    assert len(fixtures) == 1

    fixture = fixtures[0]

    assert fixture["external_id"] == "98765"
    assert fixture["home_team_code"] == "FRA"
    assert fixture["away_team_code"] == "SEN"
    assert fixture["status"] == "complete"
    assert fixture["home_score"] == 3
    assert fixture["away_score"] == 1


def test_api_football_provider_skips_incomplete_fixtures(monkeypatch):
    def mock_get(url, headers, params, timeout):
        return MockResponse(
            {
                "response": [
                    {
                        "fixture": {
                            "id": None,
                            "date": "2026-06-11T19:00:00+00:00",
                            "status": {
                                "short": "NS",
                            },
                        },
                        "league": {
                            "name": "FIFA World Cup",
                            "round": "Group Stage - 1",
                        },
                        "teams": {
                            "home": {
                                "name": "Mexico",
                            },
                            "away": {
                                "name": "South Africa",
                            },
                        },
                        "goals": {
                            "home": None,
                            "away": None,
                        },
                    },
                    {
                        "fixture": {
                            "id": 22222,
                            "date": "2026-06-12T21:00:00+00:00",
                            "status": {
                                "short": "NS",
                            },
                        },
                        "league": {
                            "name": "FIFA World Cup",
                            "round": "Group Stage - 1",
                        },
                        "teams": {
                            "home": {
                                "name": "United States",
                            },
                            "away": {
                                "name": "Paraguay",
                            },
                        },
                        "goals": {
                            "home": None,
                            "away": None,
                        },
                    },
                ]
            }
        )

    monkeypatch.setattr(httpx, "get", mock_get)

    provider = ApiFootballProvider()
    provider.api_key = "test-key"

    fixtures = provider.get_world_cup_fixtures()

    assert len(fixtures) == 1
    assert fixtures[0]["external_id"] == "22222"
    assert fixtures[0]["home_team"] == "United States"
    assert fixtures[0]["away_team"] == "Paraguay"
    assert fixtures[0]["home_team_code"] == "USA"
    assert fixtures[0]["away_team_code"] == "PAR"
    assert fixtures[0]["status"] == "scheduled"


def test_api_football_provider_requires_api_key():
    provider = ApiFootballProvider()
    provider.api_key = ""

    with pytest.raises(ValueError, match="API_FOOTBALL_KEY is not configured."):
        provider.get_world_cup_fixtures()


def test_api_football_provider_wraps_request_errors(monkeypatch):
    def mock_get(url, headers, params, timeout):
        raise httpx.RequestError("network unavailable")

    monkeypatch.setattr(httpx, "get", mock_get)

    provider = ApiFootballProvider()
    provider.api_key = "test-key"

    with pytest.raises(
        ApiFootballProviderError,
        match="API-Football request failed",
    ):
        provider.get_world_cup_fixtures()


def test_api_football_provider_rejects_invalid_payload(monkeypatch):
    def mock_get(url, headers, params, timeout):
        return MockResponse(
            {
                "response": {
                    "unexpected": "not-a-list",
                }
            }
        )

    monkeypatch.setattr(httpx, "get", mock_get)

    provider = ApiFootballProvider()
    provider.api_key = "test-key"

    with pytest.raises(
        ApiFootballProviderError,
        match="API-Football returned an invalid fixture list.",
    ):
        provider.get_world_cup_fixtures()

def test_api_football_provider_reports_provider_errors(monkeypatch):
    def fake_get(url, headers, params, timeout):
        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "errors": {
                        "plan": "Free plans do not have access to this season."
                    },
                    "response": [],
                }

        return FakeResponse()

    monkeypatch.setattr("app.providers.api_football.httpx.get", fake_get)

    provider = ApiFootballProvider()
    provider.api_key = "test-key"

    with pytest.raises(
        ApiFootballProviderError,
        match="Free plans do not have access to this season",
    ):
        provider.get_world_cup_fixtures()

