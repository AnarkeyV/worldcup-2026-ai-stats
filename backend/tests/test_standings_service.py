from types import SimpleNamespace

from app.services.standings_service import build_group_standings


def make_fixture(
    *,
    group_name="Group A",
    home_team="Mexico",
    away_team="South Africa",
    home_team_code="MEX",
    away_team_code="RSA",
    home_score=0,
    away_score=0,
    status="completed",
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


def test_build_group_standings_empty_list():
    standings = build_group_standings([])

    assert standings == []


def test_build_group_standings_ignores_incomplete_fixtures():
    fixtures = [
        make_fixture(
            home_team="Mexico",
            away_team="South Africa",
            home_score=None,
            away_score=None,
            status="scheduled",
        ),
        make_fixture(
            home_team="South Korea",
            away_team="Czechia",
            home_score=2,
            away_score=1,
            status="completed",
        ),
    ]

    standings = build_group_standings(fixtures)

    assert len(standings) == 2
    assert standings[0]["team"] == "South Korea"
    assert standings[0]["points"] == 3
    assert standings[1]["team"] == "Czechia"
    assert standings[1]["points"] == 0


def test_build_group_standings_calculates_points_and_goal_stats():
    fixtures = [
        make_fixture(
            home_team="Mexico",
            away_team="South Africa",
            home_team_code="MEX",
            away_team_code="RSA",
            home_score=2,
            away_score=0,
        ),
        make_fixture(
            home_team="South Korea",
            away_team="Czechia",
            home_team_code="KOR",
            away_team_code="CZE",
            home_score=2,
            away_score=1,
        ),
        make_fixture(
            home_team="Mexico",
            away_team="South Korea",
            home_team_code="MEX",
            away_team_code="KOR",
            home_score=1,
            away_score=1,
        ),
        make_fixture(
            home_team="South Africa",
            away_team="Czechia",
            home_team_code="RSA",
            away_team_code="CZE",
            home_score=3,
            away_score=0,
        ),
    ]

    standings = build_group_standings(fixtures)

    assert standings == [
        {
            "group_name": "Group A",
            "team": "Mexico",
            "team_code": "MEX",
            "played": 2,
            "wins": 1,
            "draws": 1,
            "losses": 0,
            "goals_for": 3,
            "goals_against": 1,
            "goal_difference": 2,
            "points": 4,
        },
        {
            "group_name": "Group A",
            "team": "South Korea",
            "team_code": "KOR",
            "played": 2,
            "wins": 1,
            "draws": 1,
            "losses": 0,
            "goals_for": 3,
            "goals_against": 2,
            "goal_difference": 1,
            "points": 4,
        },
        {
            "group_name": "Group A",
            "team": "South Africa",
            "team_code": "RSA",
            "played": 2,
            "wins": 1,
            "draws": 0,
            "losses": 1,
            "goals_for": 3,
            "goals_against": 2,
            "goal_difference": 1,
            "points": 3,
        },
        {
            "group_name": "Group A",
            "team": "Czechia",
            "team_code": "CZE",
            "played": 2,
            "wins": 0,
            "draws": 0,
            "losses": 2,
            "goals_for": 1,
            "goals_against": 5,
            "goal_difference": -4,
            "points": 0,
        },
    ]


def test_build_group_standings_can_filter_by_group_name():
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

    standings = build_group_standings(fixtures, group_name="Group B")

    assert standings == [
        {
            "group_name": "Group B",
            "team": "Canada",
            "team_code": "CAN",
            "played": 1,
            "wins": 0,
            "draws": 1,
            "losses": 0,
            "goals_for": 1,
            "goals_against": 1,
            "goal_difference": 0,
            "points": 1,
        },
        {
            "group_name": "Group B",
            "team": "Qatar",
            "team_code": "QAT",
            "played": 1,
            "wins": 0,
            "draws": 1,
            "losses": 0,
            "goals_for": 1,
            "goals_against": 1,
            "goal_difference": 0,
            "points": 1,
        },
    ]
