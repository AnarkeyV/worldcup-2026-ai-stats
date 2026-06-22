import app.routes.fixtures as fixtures_routes


def install_rich_fixture_provider(monkeypatch):
    class MockProvider:
        def get_world_cup_fixtures(self):
            return [
                {
                    "external_id": "zafronix-provider-leaders-001",
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
                    "away_score": 1,
                    "match_detail": {
                        "provider": "zafronix",
                        "provider_match_id": "leaders-001",
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
                            {
                                "minute": 82,
                                "team": "away",
                                "scorer": "Mothiba",
                            },
                        ],
                        "cards": [
                            {
                                "minute": 31,
                                "team": "home",
                                "player": "César Montes",
                                "color": "yellow",
                            },
                            {
                                "minute": 49,
                                "team": "away",
                                "player": "Sphephelo Sithole",
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
            ]

    monkeypatch.setattr(
        fixtures_routes,
        "get_configured_football_provider",
        lambda: ("zafronix", MockProvider()),
    )


def test_provider_player_leaders_use_stored_match_detail_events(client, monkeypatch):
    install_rich_fixture_provider(monkeypatch)

    sync_response = client.post("/fixtures/sync/provider")
    assert sync_response.status_code == 200

    response = client.get("/players/leaders")
    assert response.status_code == 200

    data = response.json()

    assert data["provider"] == "zafronix"
    assert data["source"] == "provider_backed_match_details"
    assert data["coverage"] == {
        "completed_fixture_count": 1,
        "detailed_fixture_count": 1,
    }
    assert data["assist_data"]["available"] is False
    assert "does not include assist events" in data["assist_data"]["message"]

    top_scorers = data["leaderboards"]["top_scorers"]
    assert [row["player_name"] for row in top_scorers] == [
        "Jiménez",
        "Mothiba",
        "Quiñones",
    ]
    assert {row["team"] for row in top_scorers} == {"Mexico", "South Africa"}
    assert all(row["goals"] == 1 for row in top_scorers)

    yellow_cards = data["leaderboards"]["yellow_card_leaders"]
    assert yellow_cards == [
        {
            "player_name": "César Montes",
            "team": "Mexico",
            "team_code": "MEX",
            "group_name": "Group A",
            "goals": 0,
            "yellow_cards": 1,
            "red_cards": 0,
        }
    ]

    red_cards = data["leaderboards"]["red_card_leaders"]
    assert red_cards == [
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


def test_provider_player_leaders_can_filter_by_team(client, monkeypatch):
    install_rich_fixture_provider(monkeypatch)

    sync_response = client.post("/fixtures/sync/provider")
    assert sync_response.status_code == 200

    response = client.get("/players/leaders?team=Mexico&limit=1")
    assert response.status_code == 200

    data = response.json()

    assert data["filters"] == {
        "team": "Mexico",
        "group_name": None,
        "limit": 1,
    }
    assert len(data["leaderboards"]["top_scorers"]) == 1
    assert data["leaderboards"]["top_scorers"][0]["team"] == "Mexico"
    assert data["leaderboards"]["red_card_leaders"] == []


def test_latest_completed_summary_prioritizes_red_card_then_result_and_scorers(
    client,
    monkeypatch,
):
    install_rich_fixture_provider(monkeypatch)

    sync_response = client.post("/fixtures/sync/provider")
    assert sync_response.status_code == 200

    response = client.get("/ai/latest-completed/summary")
    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["mode"] == "provider_backed"
    assert data["provider"] == "zafronix"
    assert data["detail_available"] is True
    assert data["fixture"]["home_team"] == "Mexico"
    assert data["fixture"]["away_team"] == "South Africa"

    summary = data["summary"]
    assert summary.index("Major incident") < summary.index("Mexico beat South Africa 2-1")
    assert summary.index("Mexico beat South Africa 2-1") < summary.index("Scorers")
    assert "Sphephelo Sithole received a red card" in summary
    assert "Quiñones (9')" in summary
    assert "Jiménez (67')" in summary
    assert "Mothiba (82')" in summary


def test_latest_completed_summary_uses_fixture_data_without_detail(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/ai/latest-completed/summary")
    assert response.status_code == 200

    data = response.json()

    assert data["mode"] == "fixture_data"
    assert data["detail_available"] is False
    assert data["provider"] == "fixture_data"
    assert "Major incident" not in data["summary"]
    assert "Scorers" not in data["summary"]


def test_latest_completed_summary_returns_404_without_completed_fixtures(client):
    response = client.get("/ai/latest-completed/summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "No completed fixtures available to summarize."


def test_root_includes_provider_leaders_and_latest_summary_links(client):
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()

    assert data["player_leaders"] == "/players/leaders"
    assert data["latest_completed_summary"] == "/ai/latest-completed/summary"
