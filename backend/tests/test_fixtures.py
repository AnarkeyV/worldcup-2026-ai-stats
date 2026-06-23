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
    assert data["notifications"]["reason"] == "Completed-match Telegram alerts are disabled by configuration."
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
    assert data["notifications"]["reason"] == "Completed-match Telegram alerts are disabled by configuration."
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
    assert data["notifications"]["reason"] == "Completed-match Telegram alerts are disabled by configuration."
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

def test_get_fixture_detail_returns_unavailable_without_provider_detail(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    fixture_id = client.get("/fixtures").json()["fixtures"][0]["id"]

    response = client.get(f"/fixtures/{fixture_id}/detail")

    assert response.status_code == 200

    data = response.json()

    assert data["fixture"]["id"] == fixture_id
    assert data["detail_available"] is False
    assert data["detail"] is None
    assert data["stored_event_coverage"] == {
        "detail_state": "unavailable",
        "provider": None,
        "stored_detail_updated_at": None,
        "event_types": {
            "goals": {
                "state": "unavailable",
                "count": None,
                "message": "Goal event coverage is unavailable because no stored provider detail exists.",
            },
            "cards": {
                "state": "unavailable",
                "count": None,
                "message": "Card event coverage is unavailable because no stored provider detail exists.",
            },
            "substitutions": {
                "state": "unavailable",
                "count": None,
                "message": "Substitution event coverage is unavailable because no stored provider detail exists.",
            },
        },
        "message": (
            "No stored provider match detail is available for this fixture. "
            "No live provider lookup was attempted."
        ),
    }


def test_provider_sync_persists_rich_match_detail(client, monkeypatch):
    class MockProvider:
        def get_world_cup_fixtures(self):
            return [
                {
                    "external_id": "zafronix-rich-detail-001",
                    "competition": "FIFA World Cup 2026",
                    "stage": "Group Stage",
                    "group_name": "Group A",
                    "home_team": "Mexico",
                    "away_team": "South Africa",
                    "home_team_code": "MEX",
                    "away_team_code": "RSA",
                    "kickoff_time": "2026-06-11T19:00:00+00:00",
                    "venue": "Mexico City Stadium",
                    "status": "complete",
                    "home_score": 2,
                    "away_score": 0,
                    "match_detail": {
                        "provider": "zafronix",
                        "provider_match_id": "2026-001",
                        "goals": [
                            {
                                "minute": 9,
                                "team": "home",
                                "scorer": "Quiñones",
                            },
                            {
                                "minute": 67,
                                "team": "home",
                                "scorer": "Jiménez",
                            },
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
                                    "captain": False,
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
                    },
                }
            ]

    monkeypatch.setattr(
        fixtures_routes,
        "get_configured_football_provider",
        lambda: ("zafronix", MockProvider()),
    )

    sync_response = client.post("/fixtures/sync/provider")
    assert sync_response.status_code == 200

    fixture_id = client.get("/fixtures").json()["fixtures"][0]["id"]

    response = client.get(f"/fixtures/{fixture_id}/detail")

    assert response.status_code == 200

    data = response.json()

    assert data["detail_available"] is True
    assert data["fixture"]["external_id"] == "zafronix-rich-detail-001"
    assert data["detail"]["provider"] == "zafronix"
    assert data["detail"]["provider_match_id"] == "2026-001"
    assert data["detail"]["goals"][0]["scorer"] == "Quiñones"
    assert data["detail"]["goals"][1]["minute"] == 67
    assert data["detail"]["cards"][0]["color"] == "red"
    assert data["detail"]["formations"]["home"] == "4-3-3"
    assert data["detail"]["lineups"]["home"][0]["player"] == "Raúl Rangel"
    assert data["detail"]["statistics"]["home"]["possessionPct"] == 61
    assert data["detail"]["statistics"]["away"]["expectedGoals"] == 0.07
    assert data["detail"]["referee"]["name"] == "Test Referee"
    assert data["detail"]["weather"]["tempC"] == 24
    assert data["stored_event_coverage"] == {
        "detail_state": "available",
        "provider": "zafronix",
        "stored_detail_updated_at": data["detail"]["updated_at"],
        "event_types": {
            "goals": {
                "state": "recorded",
                "count": 2,
                "message": "2 stored goal events are available in the last provider payload.",
            },
            "cards": {
                "state": "recorded",
                "count": 1,
                "message": "1 stored card event is available in the last provider payload.",
            },
            "substitutions": {
                "state": "recorded",
                "count": 1,
                "message": "1 stored substitution event is available in the last provider payload.",
            },
        },
        "message": (
            "Stored provider match detail is available. Event counts describe only "
            "the last stored provider payload and do not confirm match completeness."
        ),
    }

def test_get_fixture_detail_marks_empty_stored_event_arrays_as_no_stored_events(
    client,
    monkeypatch,
):
    class MockProvider:
        def get_world_cup_fixtures(self):
            return [
                {
                    "external_id": "zafronix-empty-events-001",
                    "competition": "FIFA World Cup 2026",
                    "stage": "Group Stage",
                    "group_name": "Group B",
                    "home_team": "Canada",
                    "away_team": "Japan",
                    "home_team_code": "CAN",
                    "away_team_code": "JPN",
                    "kickoff_time": "2026-06-12T19:00:00+00:00",
                    "venue": "Toronto Stadium",
                    "status": "complete",
                    "home_score": 0,
                    "away_score": 0,
                    "match_detail": {
                        "provider": "zafronix",
                        "provider_match_id": "empty-events-001",
                        "goals": [],
                        "cards": [],
                        "substitutions": [],
                        "formations": {},
                        "lineups": {},
                        "statistics": {},
                        "referee": {},
                        "weather": {},
                    },
                }
            ]

    monkeypatch.setattr(
        fixtures_routes,
        "get_configured_football_provider",
        lambda: ("zafronix", MockProvider()),
    )

    sync_response = client.post("/fixtures/sync/provider")
    assert sync_response.status_code == 200

    fixture_id = client.get("/fixtures").json()["fixtures"][0]["id"]
    response = client.get(f"/fixtures/{fixture_id}/detail")

    assert response.status_code == 200

    coverage = response.json()["stored_event_coverage"]

    assert coverage["detail_state"] == "available"
    assert coverage["provider"] == "zafronix"
    assert coverage["stored_detail_updated_at"] is not None
    assert coverage["message"] == (
        "Stored provider match detail is available. Event counts describe only "
        "the last stored provider payload and do not confirm match completeness."
    )
    assert coverage["event_types"] == {
        "goals": {
            "state": "no_stored_events",
            "count": 0,
            "message": (
                "No stored goal events are present in the last provider payload. "
                "This does not confirm that none occurred."
            ),
        },
        "cards": {
            "state": "no_stored_events",
            "count": 0,
            "message": (
                "No stored card events are present in the last provider payload. "
                "This does not confirm that none occurred."
            ),
        },
        "substitutions": {
            "state": "no_stored_events",
            "count": 0,
            "message": (
                "No stored substitution events are present in the last provider payload. "
                "This does not confirm that none occurred."
            ),
        },
    }



def test_sync_generated_completed_match_alerts_are_disabled_by_default(client, monkeypatch):
    notification_calls = []

    def fail_if_called(fixtures):
        notification_calls.append(fixtures)
        raise AssertionError("Sync-generated Telegram alerts must remain disabled.")

    monkeypatch.setattr(
        fixtures_routes,
        "send_completed_fixture_notifications",
        fail_if_called,
    )
    monkeypatch.setattr(
        fixtures_routes.settings,
        "telegram_completed_match_alerts_enabled",
        False,
    )

    response = client.post("/fixtures/sync/sample")

    assert response.status_code == 200
    assert notification_calls == []
    assert response.json()["notifications"] == {
        "status": "skipped",
        "reason": "Completed-match Telegram alerts are disabled by configuration.",
        "sent": 0,
    }


def test_sync_generated_completed_match_alerts_require_explicit_opt_in(client, monkeypatch):
    sent_fixtures = []

    def fake_send_completed_fixture_notifications(fixtures):
        sent_fixtures.extend(fixtures)
        return {
            "sent": len(fixtures),
            "messages": [],
        }

    monkeypatch.setattr(
        fixtures_routes,
        "send_completed_fixture_notifications",
        fake_send_completed_fixture_notifications,
    )
    monkeypatch.setattr(
        fixtures_routes.settings,
        "telegram_completed_match_alerts_enabled",
        True,
    )

    response = client.post("/fixtures/sync/sample")

    assert response.status_code == 200

    data = response.json()

    assert data["notifications"] == {
        "status": "sent",
        "sent": 4,
    }
    assert len(sent_fixtures) == 4
    assert sent_fixtures[0]["status"] == "complete"
