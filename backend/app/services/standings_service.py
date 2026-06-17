from dataclasses import asdict, dataclass
from typing import Any


COMPLETED_STATUSES = {
    "complete",
    "completed",
    "finished",
    "final",
    "ft",
    "full-time",
    "full_time",
    "match finished",
}


@dataclass
class StandingRow:
    group_name: str
    team: str
    team_code: str | None
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    goal_difference: int = 0
    points: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_group_standings(
    fixtures: list[Any],
    group_name: str | None = None,
) -> list[dict[str, Any]]:
    """
    Build group standings from completed fixtures.

    This service intentionally works with any fixture-like object that has:
    - group_name
    - status
    - home_team
    - away_team
    - home_team_code
    - away_team_code
    - home_score
    - away_score

    That keeps it easy to test and easy to reuse with database models.
    """

    standings: dict[tuple[str, str], StandingRow] = {}

    for fixture in fixtures:
        fixture_group_name = getattr(fixture, "group_name", None)

        if group_name is not None and fixture_group_name != group_name:
            continue

        if not _is_completed_fixture(fixture):
            continue

        home_team = getattr(fixture, "home_team")
        away_team = getattr(fixture, "away_team")
        home_team_code = getattr(fixture, "home_team_code", None)
        away_team_code = getattr(fixture, "away_team_code", None)
        home_score = getattr(fixture, "home_score")
        away_score = getattr(fixture, "away_score")

        home_row = _get_or_create_row(
            standings=standings,
            group_name=fixture_group_name,
            team=home_team,
            team_code=home_team_code,
        )
        away_row = _get_or_create_row(
            standings=standings,
            group_name=fixture_group_name,
            team=away_team,
            team_code=away_team_code,
        )

        _apply_match_result(
            home_row=home_row,
            away_row=away_row,
            home_score=home_score,
            away_score=away_score,
        )

    sorted_rows = sorted(
        standings.values(),
        key=lambda row: (
            row.group_name,
            -row.points,
            -row.goal_difference,
            -row.goals_for,
            row.team,
        ),
    )

    return [row.to_dict() for row in sorted_rows]


def _is_completed_fixture(fixture: Any) -> bool:
    status = getattr(fixture, "status", None)
    home_score = getattr(fixture, "home_score", None)
    away_score = getattr(fixture, "away_score", None)

    if home_score is None or away_score is None:
        return False

    if status is None:
        return False

    return str(status).strip().lower() in COMPLETED_STATUSES


def _get_or_create_row(
    standings: dict[tuple[str, str], StandingRow],
    group_name: str,
    team: str,
    team_code: str | None,
) -> StandingRow:
    key = (group_name, team)

    if key not in standings:
        standings[key] = StandingRow(
            group_name=group_name,
            team=team,
            team_code=team_code,
        )

    return standings[key]


def _apply_match_result(
    home_row: StandingRow,
    away_row: StandingRow,
    home_score: int,
    away_score: int,
) -> None:
    home_row.played += 1
    away_row.played += 1

    home_row.goals_for += home_score
    home_row.goals_against += away_score
    home_row.goal_difference = home_row.goals_for - home_row.goals_against

    away_row.goals_for += away_score
    away_row.goals_against += home_score
    away_row.goal_difference = away_row.goals_for - away_row.goals_against

    if home_score > away_score:
        home_row.wins += 1
        home_row.points += 3
        away_row.losses += 1
    elif away_score > home_score:
        away_row.wins += 1
        away_row.points += 3
        home_row.losses += 1
    else:
        home_row.draws += 1
        away_row.draws += 1
        home_row.points += 1
        away_row.points += 1
