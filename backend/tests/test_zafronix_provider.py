import httpx
import pytest

from app.providers.zafronix import ZafronixProvider, ZafronixProviderError


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "error",
                request=httpx.Request("GET", "https://example.test"),
                response=httpx.Response(self.status_code),
            )

    def json(self):
        return self.payload


def test_zafronix_provider_normalizes_completed_fixture(monkeypatch):
    def fake_get(url, headers, params, timeout):
        assert url == "https://api.zafronix.com/fifa/worldcup/v1/matches"
        assert headers == {"X-API-Key": "test-key"}
        assert params == {"year": 2026}

        return FakeResponse(
            {
                "data": [
                    {
                        "id": "2026-001",
                        "kickoffUtc": "2026-06-11T19:00:00.000Z",
                        "stage": "group_a",
                        "stageNormalized": "group_a",
                        "homeTeam": "Mexico",
                        "awayTeam": "South Africa",
                        "homeScore": 2,
                        "awayScore": 0,
                        "stadium": "Mexico City Stadium",
                        "city": "Ciudad de México",
                        "country": "Mexico",
                        "status": "finished",
                        "goals": [
                            {
                                "minute": 9,
                                "team": "home",
                                "scorer": "Quiñones",
                            }
                        ],
                        "cards": [
                            {
                                "minute": 49,
                                "team": "away",
                                "player": "Sphephelo Sithole",
                                "color": "red",
                            }
                        ],
                        "substitutions": [
                            {
                                "minute": 66,
                                "team": "home",
                                "on": "Gilberto Mora",
                                "off": "Álvaro Fidalgo",
                            }
                        ],
                        "formations": {
                            "home": "4-3-3",
                            "away": "5-3-2",
                        },
                        "lineups": {
                            "home": [
                                {
                                    "player": "Raúl Rangel",
                                    "number": 1,
                                    "position": "GK",
                                    "starter": True,
                                }
                            ],
                            "away": [],
                        },
                        "statistics": {
                            "home": {
                                "possessionPct": 61,
                                "shotsTotal": 16,
                                "expectedGoals": 1.41,
                            },
                            "away": {
                                "possessionPct": 39,
                                "shotsTotal": 3,
                                "expectedGoals": 0.07,
                            },
                        },
                        "referee": {
                            "name": "Test Referee",
                            "country": "Test Country",
                        },
                        "weather": {
                            "tempC": 24,
                            "windKmh": 12,
                        },
                    }
                ]
            }
        )

    monkeypatch.setattr("app.providers.zafronix.httpx.get", fake_get)

    provider = ZafronixProvider()
    provider.api_key = "test-key"

    fixtures = provider.get_world_cup_fixtures()

    assert len(fixtures) == 1

    fixture = fixtures[0]

    assert fixture["external_id"] == "zafronix-2026-001"
    assert fixture["competition"] == "FIFA World Cup 2026"
    assert fixture["stage"] == "Group Stage"
    assert fixture["group_name"] == "Group A"
    assert fixture["home_team"] == "Mexico"
    assert fixture["away_team"] == "South Africa"
    assert fixture["home_team_code"] == "MEX"
    assert fixture["away_team_code"] == "RSA"
    assert fixture["kickoff_time"] == "2026-06-11T19:00:00.000Z"
    assert fixture["venue"] == "Mexico City Stadium, Ciudad de México, Mexico"
    assert fixture["status"] == "complete"
    assert fixture["home_score"] == 2
    assert fixture["away_score"] == 0

    detail = fixture["match_detail"]

    assert detail["provider"] == "zafronix"
    assert detail["provider_match_id"] == "2026-001"
    assert detail["goals"] == [
        {
            "minute": 9,
            "team": "home",
            "scorer": "Quiñones",
        }
    ]
    assert detail["cards"][0]["color"] == "red"
    assert detail["substitutions"][0]["on"] == "Gilberto Mora"
    assert detail["formations"] == {
        "home": "4-3-3",
        "away": "5-3-2",
    }
    assert detail["lineups"]["home"][0]["player"] == "Raúl Rangel"
    assert detail["lineups"]["home"][0]["captain"] is False
    assert detail["statistics"]["home"]["expectedGoals"] == 1.41
    assert detail["referee"]["name"] == "Test Referee"
    assert detail["weather"]["tempC"] == 24

def test_zafronix_provider_normalizes_scheduled_fixture(monkeypatch):
    def fake_get(url, headers, params, timeout):
        return FakeResponse(
            [
                {
                    "id": "2026-044",
                    "kickoffUtc": "2026-06-19T19:00:00.000Z",
                    "stage": "group_d",
                    "homeTeam": "United States",
                    "awayTeam": "Australia",
                    "homeScore": None,
                    "awayScore": None,
                    "stadium": "Seattle Stadium",
                    "city": "Seattle",
                    "country": "United States",
                    "status": "scheduled",
                }
            ]
        )

    monkeypatch.setattr("app.providers.zafronix.httpx.get", fake_get)

    provider = ZafronixProvider()
    provider.api_key = "test-key"

    fixtures = provider.get_world_cup_fixtures()

    assert fixtures[0]["external_id"] == "zafronix-2026-044"
    assert fixtures[0]["group_name"] == "Group D"
    assert fixtures[0]["home_team_code"] == "USA"
    assert fixtures[0]["away_team_code"] == "AUS"
    assert fixtures[0]["status"] == "scheduled"
    assert fixtures[0]["home_score"] is None
    assert fixtures[0]["away_score"] is None


def test_zafronix_provider_requires_api_key():
    provider = ZafronixProvider()
    provider.api_key = ""

    with pytest.raises(ValueError, match="ZAFRONIX_API_KEY is not configured."):
        provider.get_world_cup_fixtures()


def test_zafronix_provider_wraps_request_errors(monkeypatch):
    def fake_get(url, headers, params, timeout):
        raise httpx.ConnectError("network unavailable")

    monkeypatch.setattr("app.providers.zafronix.httpx.get", fake_get)

    provider = ZafronixProvider()
    provider.api_key = "test-key"

    with pytest.raises(ZafronixProviderError, match="Zafronix request failed"):
        provider.get_world_cup_fixtures()


def test_zafronix_provider_rejects_invalid_payload(monkeypatch):
    def fake_get(url, headers, params, timeout):
        return FakeResponse({"unexpected": []})

    monkeypatch.setattr("app.providers.zafronix.httpx.get", fake_get)

    provider = ZafronixProvider()
    provider.api_key = "test-key"

    with pytest.raises(ZafronixProviderError, match="invalid fixture list"):
        provider.get_world_cup_fixtures()
