from types import SimpleNamespace

from app.services.insights_service import build_group_insights


def make_fixture(
    *,
    group_name="Group A",
    home_team="Mexico",
    away_team="South Africa",
    home_team_code="MEX",
    away_team_code="RSA",
    home_score=0,
    away_score=0,
    status="complete",
):
    return SimpleNamespace(
        group_name=group_name,
        home_team=home_team,
        away_team=away_team,
        home_team_code=home_team_code,
        away_team_code=away_team_code,
        home_score=home_score,
        away_score=away_score,
        status=status,
    )


def test_build_group_insights_empty_list():
    insights = build_group_insights([])

    assert insights == {
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
    }


def test_build_group_insights_identifies_group_leaders():
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

    insights = build_group_insights(fixtures)

    assert insights["summary"] == {
        "teams_analyzed": 4,
        "groups_analyzed": 2,
        "has_data": True,
    }

    assert [team["team"] for team in insights["group_leaders"]] == [
        "Mexico",
        "United States",
    ]


def test_build_group_insights_identifies_strongest_attacks():
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
        make_fixture(
            group_name="Group I",
            home_team="France",
            away_team="Senegal",
            home_team_code="FRA",
            away_team_code="SEN",
            home_score=3,
            away_score=1,
        ),
    ]

    insights = build_group_insights(fixtures)

    assert [team["team"] for team in insights["strongest_attacks"][:3]] == [
        "United States",
        "France",
        "Mexico",
    ]


def test_build_group_insights_identifies_best_defences():
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
        make_fixture(
            group_name="Group J",
            home_team="Argentina",
            away_team="Algeria",
            home_team_code="ARG",
            away_team_code="DZA",
            home_score=3,
            away_score=0,
        ),
    ]

    insights = build_group_insights(fixtures)

    assert [team["team"] for team in insights["best_defences"][:2]] == [
        "Argentina",
        "Mexico",
    ]


def test_build_group_insights_identifies_unbeaten_and_winless_teams():
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
            group_name="Group B",
            home_team="Canada",
            away_team="Qatar",
            home_team_code="CAN",
            away_team_code="QAT",
            home_score=1,
            away_score=1,
        ),
    ]

    insights = build_group_insights(fixtures)

    assert [team["team"] for team in insights["unbeaten_teams"]] == [
        "Mexico",
        "Canada",
        "Qatar",
    ]

    assert [team["team"] for team in insights["winless_teams"]] == [
        "South Africa",
        "Canada",
        "Qatar",
    ]


def test_build_group_insights_can_filter_by_group_name():
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

    insights = build_group_insights(fixtures, group_name="Group D")

    assert insights["summary"] == {
        "teams_analyzed": 2,
        "groups_analyzed": 1,
        "has_data": True,
    }

    assert [team["team"] for team in insights["group_leaders"]] == [
        "United States",
    ]

    assert {team["group_name"] for team in insights["strongest_attacks"]} == {
        "Group D",
    }


def test_build_group_insights_limit_can_reduce_result_lists():
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

    insights = build_group_insights(fixtures, limit=1)

    assert len(insights["strongest_attacks"]) == 1
    assert len(insights["best_defences"]) == 1
    assert len(insights["unbeaten_teams"]) == 1
    assert len(insights["winless_teams"]) == 1
