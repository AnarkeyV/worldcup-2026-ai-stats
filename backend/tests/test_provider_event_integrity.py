import app.routes.fixtures as fixtures_routes

from app.providers.zafronix import ZafronixProvider
from app.services.provider_leaderboard_service import build_provider_player_leaderboards


def test_zafronix_normalizes_events_to_safe_canonical_records():
    provider = ZafronixProvider()

    assert provider._normalize_goals(
        [
            {"minute": "45+2", "team": " HOME ", "scorer": " Alex "},
            {"minute": "45+2", "team": "home", "scorer": "Alex"},
            {"minute": "9", "team": "away", "scorer": "Béla"},
            {"minute": None, "team": "away", "scorer": "No Minute"},
            {"minute": 14, "team": "third", "scorer": "Unknown Side"},
            {"minute": 20, "team": "home", "scorer": "   "},
            None,
        ]
    ) == [
        {"minute": 9, "team": "away", "scorer": "Béla"},
        {"minute": "45+2", "team": "home", "scorer": "Alex"},
        {"minute": None, "team": "away", "scorer": "No Minute"},
    ]

    assert provider._normalize_cards(
        [
            {
                "minute": 90,
                "team": " HOME ",
                "player": " Alex ",
                "color": " RED ",
            },
            {
                "minute": "90",
                "team": "home",
                "player": "Alex",
                "color": "red",
            },
            {
                "minute": 43,
                "team": "away",
                "player": "Béla",
                "color": "yellow",
            },
            {
                "minute": None,
                "team": "away",
                "player": "No Minute",
                "color": "yellow",
            },
            {
                "minute": 14,
                "team": "away",
                "player": None,
                "color": "yellow",
            },
            None,
        ]
    ) == [
        {
            "minute": 43,
            "team": "away",
            "player": "Béla",
            "color": "yellow",
        },
        {
            "minute": 90,
            "team": "home",
            "player": "Alex",
            "color": "red",
        },
        {
            "minute": None,
            "team": "away",
            "player": "No Minute",
            "color": "yellow",
        },
    ]

    assert provider._normalize_substitutions(
        [
            {
                "minute": 71,
                "team": "away",
                "on": "Replacement",
                "off": "Starter",
            },
            {
                "minute": "71",
                "team": " AWAY ",
                "on": " Replacement ",
                "off": " Starter ",
            },
            {
                "minute": 60,
                "team": "home",
                "on": "Incoming",
                "off": "Outgoing",
            },
            {
                "minute": None,
                "team": "home",
                "on": "Untimed On",
                "off": "Untimed Off",
            },
            {
                "minute": 77,
                "team": "home",
                "on": None,
                "off": "Outgoing",
            },
            None,
        ]
    ) == [
        {
            "minute": 60,
            "team": "home",
            "on": "Incoming",
            "off": "Outgoing",
        },
        {
            "minute": 71,
            "team": "away",
            "on": "Replacement",
            "off": "Starter",
        },
        {
            "minute": None,
            "team": "home",
            "on": "Untimed On",
            "off": "Untimed Off",
        },
    ]


def test_provider_sync_persists_canonical_events_and_replaces_corrected_detail(
    client,
    monkeypatch,
):
    provider_payloads = [
        [
            {
                "external_id": "zafronix-event-integrity-001",
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
                "home_score": 1,
                "away_score": 0,
                "match_detail": {
                    "provider": "zafronix",
                    "provider_match_id": "event-integrity-001",
                    "goals": [
                        {
                            "minute": "9",
                            "team": " HOME ",
                            "scorer": " Quiñones ",
                        },
                        {
                            "minute": 9,
                            "team": "home",
                            "scorer": "Quiñones",
                        },
                        {
                            "minute": 20,
                            "team": "home",
                            "scorer": None,
                        },
                    ],
                    "cards": [
                        {
                            "minute": 49,
                            "team": "away",
                            "player": "Sphephelo Sithole",
                            "color": " RED ",
                        },
                        {
                            "minute": "49",
                            "team": " AWAY ",
                            "player": " Sphephelo Sithole ",
                            "color": "red",
                        },
                    ],
                    "substitutions": [],
                    "formations": {},
                    "lineups": {},
                    "statistics": {},
                    "referee": {},
                    "weather": {},
                },
            }
        ],
        [
            {
                "external_id": "zafronix-event-integrity-001",
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
                "home_score": 1,
                "away_score": 1,
                "match_detail": {
                    "provider": "zafronix",
                    "provider_match_id": "event-integrity-001",
                    "goals": [
                        {
                            "minute": 82,
                            "team": "away",
                            "scorer": "Mothiba",
                        }
                    ],
                    "cards": [],
                    "substitutions": [],
                    "formations": {},
                    "lineups": {},
                    "statistics": {},
                    "referee": {},
                    "weather": {},
                },
            }
        ],
    ]

    class MockProvider:
        def get_world_cup_fixtures(self):
            return provider_payloads.pop(0)

    monkeypatch.setattr(
        fixtures_routes,
        "get_configured_football_provider",
        lambda: ("zafronix", MockProvider()),
    )

    first_sync_response = client.post("/fixtures/sync/provider")
    assert first_sync_response.status_code == 200

    fixture_id = client.get("/fixtures").json()["fixtures"][0]["id"]
    first_detail_response = client.get(f"/fixtures/{fixture_id}/detail")
    assert first_detail_response.status_code == 200

    first_detail = first_detail_response.json()["detail"]
    assert first_detail["goals"] == [
        {"minute": 9, "team": "home", "scorer": "Quiñones"}
    ]
    assert first_detail["cards"] == [
        {
            "minute": 49,
            "team": "away",
            "player": "Sphephelo Sithole",
            "color": "red",
        }
    ]

    second_sync_response = client.post("/fixtures/sync/provider")
    assert second_sync_response.status_code == 200

    corrected_detail_response = client.get(f"/fixtures/{fixture_id}/detail")
    assert corrected_detail_response.status_code == 200

    corrected_detail = corrected_detail_response.json()["detail"]
    assert corrected_detail["goals"] == [
        {"minute": 82, "team": "away", "scorer": "Mothiba"}
    ]
    assert corrected_detail["cards"] == []


def test_provider_leaderboards_do_not_double_count_duplicate_or_malformed_events():
    fixtures = [
        {
            "id": 41,
            "status": "complete",
            "home_team": "Mexico",
            "away_team": "South Africa",
            "home_team_code": "MEX",
            "away_team_code": "RSA",
            "group_name": "Group A",
            "kickoff_time": "2026-06-11T19:00:00+00:00",
        }
    ]
    match_details = [
        {
            "fixture_id": 41,
            "provider": "zafronix",
            "goals": [
                {"minute": 9, "team": "home", "scorer": "Quiñones"},
                {"minute": "9", "team": " HOME ", "scorer": " Quiñones "},
                {"minute": 20, "team": "home", "scorer": None},
            ],
            "cards": [
                {
                    "minute": 49,
                    "team": "away",
                    "player": "Sphephelo Sithole",
                    "color": "red",
                },
                {
                    "minute": "49",
                    "team": " AWAY ",
                    "player": " Sphephelo Sithole ",
                    "color": " RED ",
                },
                {
                    "minute": 72,
                    "team": "away",
                    "player": None,
                    "color": "yellow",
                },
            ],
        }
    ]

    result = build_provider_player_leaderboards(fixtures, match_details)

    assert result["leaderboards"]["top_scorers"] == [
        {
            "player_name": "Quiñones",
            "team": "Mexico",
            "team_code": "MEX",
            "group_name": "Group A",
            "goals": 1,
            "yellow_cards": 0,
            "red_cards": 0,
        }
    ]
    assert result["leaderboards"]["yellow_card_leaders"] == []
    assert result["leaderboards"]["red_card_leaders"] == [
        {
            "player_name": "Sphephelo Sithole",
            "team": "South Africa",
            "team_code": "RSA",
            "group_name": "Group A",
            "goals": 0,
            "yellow_cards": 0,
            "red_cards": 1,
        }
    ]
