from types import SimpleNamespace

from app.services.ai_insights_service import build_ai_insights


def make_fixture(
    *,
    group_name="Group A",
    home_team="Mexico",
    away_team="South Africa",
    home_team_code="MEX",
    away_team_code="RSA",
    home_score=2,
    away_score=0,
    status="complete",
):
    return SimpleNamespace(
        competition="FIFA World Cup 2026",
        stage="Group Stage",
        group_name=group_name,
        home_team=home_team,
        away_team=away_team,
        home_team_code=home_team_code,
        away_team_code=away_team_code,
        kickoff_time="2026-06-11T15:00:00-04:00",
        venue="Estadio Azteca",
        status=status,
        home_score=home_score,
        away_score=away_score,
    )


def test_build_ai_insights_empty_fixture_list():
    result = build_ai_insights([])

    assert result["status"] == "ok"
    assert result["mode"] == "fallback"
    assert result["provider"] == "rules_based_ai_insights"
    assert result["model"] == "rules_based_v1"
    assert result["summary"] == "No fixture data is available for AI insights yet."
    assert result["filters"] == {
        "group_name": None,
        "team": None,
        "limit": 5,
    }
    assert result["metadata"] == {
        "fixture_count": 0,
        "completed_count": 0,
        "live_count": 0,
        "scheduled_count": 0,
        "other_status_count": 0,
        "teams_analyzed": 0,
        "groups_analyzed": 0,
        "sync_status": None,
    }
    assert result["insights"] == [
        {
            "title": "No fixture data available",
            "category": "fixtures",
            "message": "No fixture data is available for AI insights yet.",
        }
    ]


def test_build_ai_insights_summarizes_completed_fixtures_and_standings():
    fixtures = [
        make_fixture(
            group_name="Group A",
            home_team="Mexico",
            away_team="South Africa",
            home_team_code="MEX",
            away_team_code="RSA",
            home_score=2,
            away_score=0,
        ),
        make_fixture(
            group_name="Group D",
            home_team="United States",
            away_team="Paraguay",
            home_team_code="USA",
            away_team_code="PAR",
            home_score=4,
            away_score=1,
        ),
    ]

    result = build_ai_insights(fixtures)

    assert result["status"] == "ok"
    assert result["mode"] == "fallback"
    assert result["metadata"]["fixture_count"] == 2
    assert result["metadata"]["completed_count"] == 2
    assert result["metadata"]["teams_analyzed"] == 4
    assert result["metadata"]["groups_analyzed"] == 2

    titles = [insight["title"] for insight in result["insights"]]

    assert "Fixture data available" in titles
    assert "Completed results detected" in titles
    assert "Group leaders available" in titles
    assert "Strongest attacks identified" in titles

    summary = result["summary"].lower()

    assert "2 fixtures are available for ai insights" in summary
    assert "2 completed" in summary

    group_leaders_message = next(
        insight["message"]
        for insight in result["insights"]
        if insight["title"] == "Group leaders available"
    )

    assert "Mexico (Group A, 3 pts, +2 GD)" in group_leaders_message
    assert "United States (Group D, 3 pts, +3 GD)" in group_leaders_message


def test_build_ai_insights_can_filter_by_group_name():
    fixtures = [
        make_fixture(
            group_name="Group A",
            home_team="Mexico",
            away_team="South Africa",
            home_team_code="MEX",
            away_team_code="RSA",
            home_score=2,
            away_score=0,
        ),
        make_fixture(
            group_name="Group D",
            home_team="United States",
            away_team="Paraguay",
            home_team_code="USA",
            away_team_code="PAR",
            home_score=4,
            away_score=1,
        ),
    ]

    result = build_ai_insights(fixtures, group_name="Group A")

    assert result["filters"] == {
        "group_name": "Group A",
        "team": None,
        "limit": 5,
    }
    assert result["metadata"]["fixture_count"] == 1
    assert result["metadata"]["completed_count"] == 1
    assert result["metadata"]["teams_analyzed"] == 2
    assert result["metadata"]["groups_analyzed"] == 1
    assert "for Group A" in result["summary"]


def test_build_ai_insights_can_filter_by_team_name_or_code():
    fixtures = [
        make_fixture(
            group_name="Group A",
            home_team="Mexico",
            away_team="South Africa",
            home_team_code="MEX",
            away_team_code="RSA",
            home_score=2,
            away_score=0,
        ),
        make_fixture(
            group_name="Group D",
            home_team="United States",
            away_team="Paraguay",
            home_team_code="USA",
            away_team_code="PAR",
            home_score=4,
            away_score=1,
        ),
    ]

    result_by_name = build_ai_insights(fixtures, team="Mexico")
    result_by_code = build_ai_insights(fixtures, team="MEX")

    assert result_by_name["metadata"]["fixture_count"] == 1
    assert result_by_code["metadata"]["fixture_count"] == 1
    assert result_by_name["metadata"]["completed_count"] == 1
    assert result_by_code["metadata"]["completed_count"] == 1
    assert "for Mexico" in result_by_name["summary"]
    assert "for MEX" in result_by_code["summary"]


def test_build_ai_insights_includes_sync_status_when_provided():
    fixtures = [
        make_fixture(
            group_name="Group A",
            home_team="Mexico",
            away_team="South Africa",
            home_team_code="MEX",
            away_team_code="RSA",
            home_score=2,
            away_score=0,
        ),
    ]
    sync_status = {
        "status": "success",
        "source": "provider",
        "provider": "api_football",
    }

    result = build_ai_insights(
        fixtures=fixtures,
        sync_status=sync_status,
    )

    assert result["metadata"]["sync_status"] == "success"
    assert "latest provider sync completed successfully" in result["summary"].lower()

    sync_insight = result["insights"][-1]

    assert sync_insight == {
        "title": "Provider sync runtime status",
        "category": "sync",
        "message": "The latest provider fixture sync completed successfully using api_football.",
    }


def test_build_ai_insights_limit_controls_number_of_insights():
    fixtures = [
        make_fixture(
            group_name="Group A",
            home_team="Mexico",
            away_team="South Africa",
            home_team_code="MEX",
            away_team_code="RSA",
            home_score=2,
            away_score=0,
        ),
        make_fixture(
            group_name="Group D",
            home_team="United States",
            away_team="Paraguay",
            home_team_code="USA",
            away_team_code="PAR",
            home_score=4,
            away_score=1,
        ),
    ]

    result = build_ai_insights(fixtures, limit=2)

    assert result["filters"]["limit"] == 2
    assert len(result["insights"]) == 2