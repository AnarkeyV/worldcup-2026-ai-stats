def test_list_player_stats_empty_before_sync(client):
    response = client.get("/players/stats")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "count": 0,
        "total_available": 0,
        "filters": {
            "team": None,
            "group_name": None,
            "sort_by": "goals",
            "limit": 10,
        },
        "stats": [],
    }


def test_sync_sample_player_stats(client):
    response = client.post("/players/stats/sync/sample")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Sample player stats synced successfully"
    assert data["created"] == 8
    assert data["updated"] == 0
    assert data["total_sample_player_stats"] == 8


def test_list_player_stats_after_sample_sync_defaults_to_goals(client):
    sync_response = client.post("/players/stats/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/players/stats")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 8
    assert data["total_available"] == 8
    assert data["filters"] == {
        "team": None,
        "group_name": None,
        "sort_by": "goals",
        "limit": 10,
    }

    assert data["stats"][0]["player_name"] == "United States Forward"
    assert data["stats"][0]["goals"] == 3


def test_list_player_stats_can_filter_by_team(client):
    sync_response = client.post("/players/stats/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/players/stats?team=Mexico")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2
    assert data["total_available"] == 2
    assert data["filters"]["team"] == "Mexico"
    assert {player["team"] for player in data["stats"]} == {"Mexico"}


def test_list_player_stats_can_filter_by_group_name(client):
    sync_response = client.post("/players/stats/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/players/stats?group_name=Group D")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2
    assert data["total_available"] == 2
    assert data["filters"]["group_name"] == "Group D"
    assert {player["group_name"] for player in data["stats"]} == {"Group D"}


def test_list_player_stats_can_sort_by_assists_and_limit(client):
    sync_response = client.post("/players/stats/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/players/stats?sort_by=assists&limit=2")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2
    assert data["total_available"] == 8
    assert data["filters"]["sort_by"] == "assists"
    assert data["filters"]["limit"] == 2
    assert data["stats"][0]["player_name"] == "United States Creator"
    assert data["stats"][0]["assists"] == 3


def test_list_player_stats_rejects_invalid_sort_by(client):
    response = client.get("/players/stats?sort_by=unknown")

    assert response.status_code == 422


def test_root_includes_player_stats_link(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["player_stats"] == "/players/stats"
