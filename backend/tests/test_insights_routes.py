def test_list_group_insights_empty_before_sync(client):
    response = client.get("/insights/groups")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "filters": {
            "group_name": None,
            "limit": 5,
        },
        "insights": {
            "summary": {
                "teams_analyzed": 0,
                "groups_analyzed": 0,
                "has_data": False,
            },
            "group_leaders": [],
            "strongest_attacks": [],
            "best_defences": [],
            "unbeaten_teams": [],
            "winless_teams": [],
        },
    }


def test_list_group_insights_after_sample_sync(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/insights/groups")

    assert response.status_code == 200

    data = response.json()
    insights = data["insights"]

    assert data["filters"] == {
        "group_name": None,
        "limit": 5,
    }

    assert insights["summary"] == {
        "teams_analyzed": 8,
        "groups_analyzed": 4,
        "has_data": True,
    }

    assert [team["team"] for team in insights["group_leaders"]] == [
        "Mexico",
        "United States",
        "France",
        "Argentina",
    ]

    assert [team["team"] for team in insights["strongest_attacks"][:2]] == [
        "United States",
        "Argentina",
    ]

    assert [team["team"] for team in insights["best_defences"][:2]] == [
        "Argentina",
        "Mexico",
    ]


def test_list_group_insights_can_filter_by_group_name(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/insights/groups?group_name=Group A")

    assert response.status_code == 200

    data = response.json()
    insights = data["insights"]

    assert data["filters"] == {
        "group_name": "Group A",
        "limit": 5,
    }

    assert insights["summary"] == {
        "teams_analyzed": 2,
        "groups_analyzed": 1,
        "has_data": True,
    }

    assert [team["team"] for team in insights["group_leaders"]] == [
        "Mexico",
    ]

    assert {team["group_name"] for team in insights["strongest_attacks"]} == {
        "Group A",
    }


def test_list_group_insights_unknown_group_returns_empty_insights(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/insights/groups?group_name=Group Z")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "filters": {
            "group_name": "Group Z",
            "limit": 5,
        },
        "insights": {
            "summary": {
                "teams_analyzed": 0,
                "groups_analyzed": 0,
                "has_data": False,
            },
            "group_leaders": [],
            "strongest_attacks": [],
            "best_defences": [],
            "unbeaten_teams": [],
            "winless_teams": [],
        },
    }


def test_list_group_insights_limit_parameter_controls_ranked_lists(client):
    sync_response = client.post("/fixtures/sync/sample")

    assert sync_response.status_code == 200

    response = client.get("/insights/groups?limit=2")

    assert response.status_code == 200

    data = response.json()
    insights = data["insights"]

    assert data["filters"] == {
        "group_name": None,
        "limit": 2,
    }

    assert len(insights["strongest_attacks"]) == 2
    assert len(insights["best_defences"]) == 2
    assert len(insights["unbeaten_teams"]) == 2
    assert len(insights["winless_teams"]) == 2


def test_list_group_insights_rejects_invalid_limit(client):
    response = client.get("/insights/groups?limit=0")

    assert response.status_code == 422
