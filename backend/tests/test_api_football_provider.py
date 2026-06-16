import httpx

from app.providers.api_football import ApiFootballProvider


class MockResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "response": [
                {
                    "fixture": {
                        "id": 12345,
                        "date": "2026-06-11T19:00:00+00:00",
                        "venue": {
                            "name": "Estadio Azteca"
                        },
                        "status": {
                            "short": "NS"
                        },
                    },
                    "league": {
                        "name": "FIFA World Cup",
                        "round": "Group Stage - 1",
                    },
                    "teams": {
                        "home": {
                            "name": "Mexico"
                        },
                        "away": {
                            "name": "South Africa"
                        },
                    },
                    "goals": {
                        "home": None,
                        "away": None,
                    },
                }
            ]
        }


def test_api_football_provider_normalizes_fixtures(monkeypatch):
    def mock_get(url, headers, params, timeout):
        assert url == "https://v3.football.api-sports.io/fixtures"
        assert headers["x-apisports-key"] == "test-key"
        assert params["league"] == 1
        assert params["season"] == 2026
        assert timeout == 20.0

        return MockResponse()

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
    assert fixture["home_team_code"] is None
    assert fixture["away_team_code"] is None
    assert fixture["kickoff_time"] == "2026-06-11T19:00:00+00:00"
    assert fixture["venue"] == "Estadio Azteca"
    assert fixture["status"] == "NS"
    assert fixture["home_score"] is None
    assert fixture["away_score"] is None