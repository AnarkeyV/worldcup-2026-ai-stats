def test_ai_insights_returns_top_two_group_race_after_sample_sync(client):
    sync_response = client.post("/fixtures/sync/sample")
    assert sync_response.status_code == 200

    response = client.get("/ai/insights")

    assert response.status_code == 200

    data = response.json()
    group_race = data["group_race"]

    assert group_race["teams_per_group"] == 2
    assert data["metadata"]["group_race_group_count"] == 4

    groups = {
        group["group_name"]: group["teams"]
        for group in group_race["groups"]
    }

    assert list(groups) == ["Group A", "Group D", "Group I", "Group J"]
    assert [team["team"] for team in groups["Group A"]] == [
        "Mexico",
        "South Africa",
    ]
    assert groups["Group A"][0] == {
        "rank": 1,
        "team": "Mexico",
        "team_code": "MEX",
        "played": 1,
        "points": 3,
        "goal_difference": 2,
        "goals_for": 2,
        "goals_against": 0,
    }

    titles = [insight["title"] for insight in data["insights"]]

    assert "Top two group positions" in titles
    assert "Strongest attacks identified" not in titles
