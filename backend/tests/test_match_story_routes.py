from app.models.fixture import Fixture
from app.models.official_match_video import OfficialMatchVideo
from app.routes import fixtures as fixtures_routes


def test_get_fixture_story_returns_unavailable_without_stored_detail(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    fixture = client.get("/fixtures").json()["fixtures"][0]

    response = client.get(f"/fixtures/{fixture['id']}/story")

    assert response.status_code == 200

    data = response.json()

    assert data["fixture"]["id"] == fixture["id"]
    assert data["fixture"]["home_team"] == fixture["home_team"]
    assert data["fixture"]["away_team"] == fixture["away_team"]
    assert data["story"]["state"] == "unavailable"
    assert data["story"]["source"] == {
        "mode": "stored_provider_match_detail",
        "detail_available": False,
        "provider": None,
        "provider_match_id": None,
        "stored_detail_updated_at": None,
    }
    assert data["story"]["score_progression"]["state"] == "unavailable"
    assert data["story"]["timeline"]["state"] == "unavailable"
    assert data["story"]["statistics"]["state"] == "unavailable"
    assert data["story"]["official_watch"]["state"] == "not_available_yet"
    assert data["story"]["official_watch"]["links"] == []


def test_get_fixture_story_returns_computed_stored_detail_without_provider_call(
    client,
    monkeypatch,
):
    class MockProvider:
        def get_world_cup_fixtures(self):
            return [
                {
                    "external_id": "zafronix-story-route-001",
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
                        "provider_match_id": "2026-story-001",
                        "goals": [
                            {
                                "minute": 9,
                                "team": "home",
                                "scorer": "Quiñones",
                            },
                            {
                                "minute": "45+2",
                                "team": "away",
                                "scorer": "Mokwana",
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
                        "formations": {},
                        "lineups": {},
                        "statistics": {
                            "home": {
                                "possessionPct": 61,
                                "shotsTotal": 16,
                                "shotsOnGoal": 6,
                                "corners": 4,
                            },
                            "away": {
                                "possessionPct": 39,
                                "shotsTotal": 3,
                                "shotsOnGoal": 1,
                                "corners": 0,
                            },
                        },
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

    response = client.get(f"/fixtures/{fixture_id}/story")

    assert response.status_code == 200

    data = response.json()

    assert data["fixture"] == {
        "id": fixture_id,
        "external_id": "zafronix-story-route-001",
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
        "updated_at": data["fixture"]["updated_at"],
    }
    assert data["fixture"]["updated_at"] is not None
    assert data["story"]["state"] == "available"
    assert data["story"]["source"]["mode"] == "stored_provider_match_detail"
    assert data["story"]["source"]["detail_available"] is True
    assert data["story"]["source"]["provider"] == "zafronix"
    assert data["story"]["source"]["provider_match_id"] == "2026-story-001"
    assert data["story"]["score_progression"]["events"] == [
        {
            "minute": 9,
            "team": "home",
            "scorer": "Quiñones",
            "home_score": 1,
            "away_score": 0,
        },
        {
            "minute": "45+2",
            "team": "away",
            "scorer": "Mokwana",
            "home_score": 1,
            "away_score": 1,
        },
        {
            "minute": 67,
            "team": "home",
            "scorer": "Jiménez",
            "home_score": 2,
            "away_score": 1,
        },
    ]
    assert [metric["key"] for metric in data["story"]["statistics"]["metrics"]] == [
        "possessionPct",
        "shotsTotal",
        "shotsOnGoal",
        "corners",
    ]
    assert data["story"]["official_watch"]["state"] == "not_available_yet"


def test_get_fixture_story_includes_only_verified_official_video_links(client, db_session):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    fixture = db_session.query(Fixture).order_by(Fixture.id).first()
    assert fixture is not None

    db_session.add(
        OfficialMatchVideo(
            fixture_id=fixture.id,
            source_key="fifa_web",
            content_type="highlights",
            title="Mexico vs South Africa | Highlights",
            external_url=(
                "https://www.fifa.com/en/tournaments/mens/worldcup/"
                "canadamexicousa2026/highlights/mexico-south-africa"
            ),
            territory="global",
            is_match_specific=True,
            published_at="2026-06-12T21:00:00+00:00",
            verified_at="2026-06-12T22:00:00+00:00",
        )
    )
    db_session.commit()

    response = client.get(f"/fixtures/{fixture.id}/story")

    assert response.status_code == 200

    watch = response.json()["story"]["official_watch"]

    assert watch["state"] == "available"
    assert watch["links"] == [
        {
            "source_key": "fifa_web",
            "source_name": "FIFA",
            "title": "Mexico vs South Africa | Highlights",
            "content_type": "highlights",
            "url": (
                "https://www.fifa.com/en/tournaments/mens/worldcup/"
                "canadamexicousa2026/highlights/mexico-south-africa"
            ),
            "territory": "Global",
            "territory_note": "Availability may still vary by territory.",
            "is_match_specific": True,
            "published_at": "2026-06-12T21:00:00+00:00",
            "verified_at": "2026-06-12T22:00:00+00:00",
            "external": True,
            "link_target": "_blank",
            "link_rel": "noopener noreferrer",
        }
    ]


def test_get_fixture_story_returns_not_found_for_unknown_fixture(client):
    response = client.get("/fixtures/999999/story")

    assert response.status_code == 404
    assert response.json() == {"detail": "Fixture not found"}
