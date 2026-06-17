def find_team(standings: list[dict], team_name: str) -> dict:
    return next(team for team in standings if team["team"] == team_name)


def test_list_standings_empty_before_sync(client):
    response = client.get("/standings")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "count": 0,
        "filters": {
            "group_name": None,
        },
        "standings": [],
    }


def test_list_standings_after_sample_sync(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/standings")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 8
    assert data["filters"] == {
        "group_name": None,
    }

    mexico = find_team(data["standings"], "Mexico")
    south_africa = find_team(data["standings"], "South Africa")

    assert mexico == {
        "group_name": "Group A",
        "team": "Mexico",
        "team_code": "MEX",
        "played": 1,
        "wins": 1,
        "draws": 0,
        "losses": 0,
        "goals_for": 2,
        "goals_against": 0,
        "goal_difference": 2,
        "points": 3,
    }

    assert south_africa == {
        "group_name": "Group A",
        "team": "South Africa",
        "team_code": "RSA",
        "played": 1,
        "wins": 0,
        "draws": 0,
        "losses": 1,
        "goals_for": 0,
        "goals_against": 2,
        "goal_difference": -2,
        "points": 0,
    }

    assert all(team["played"] == 1 for team in data["standings"])


def test_list_standings_can_filter_by_group_name(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/standings?group_name=Group A")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2
    assert data["filters"] == {
        "group_name": "Group A",
    }

    assert [team["team"] for team in data["standings"]] == [
        "Mexico",
        "South Africa",
    ]

    assert {team["group_name"] for team in data["standings"]} == {"Group A"}


def test_list_standings_unknown_group_returns_empty_list(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/standings?group_name=Group Z")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "count": 0,
        "filters": {
            "group_name": "Group Z",
        },
        "standings": [],
    }
