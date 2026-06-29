from dataclasses import dataclass


from app.services.standings_service import build_group_standings


@dataclass
class FixtureStub:
    group_name: str | None
    status: str
    home_team: str
    away_team: str
    home_team_code: str
    away_team_code: str
    home_score: int | None
    away_score: int | None


def test_build_group_standings_ignores_completed_ungrouped_fixture() -> None:
    fixtures = [
        FixtureStub(
            group_name="Group A",
            status="complete",
            home_team="Mexico",
            away_team="South Africa",
            home_team_code="MEX",
            away_team_code="RSA",
            home_score=2,
            away_score=0,
        ),
        FixtureStub(
            group_name=None,
            status="complete",
            home_team="South Africa",
            away_team="Canada",
            home_team_code="RSA",
            away_team_code="CAN",
            home_score=0,
            away_score=1,
        ),
    ]

    standings = build_group_standings(fixtures)

    assert [row["group_name"] for row in standings] == ["Group A", "Group A"]
    assert [row["team"] for row in standings] == ["Mexico", "South Africa"]
    assert all(row["group_name"] is not None for row in standings)
