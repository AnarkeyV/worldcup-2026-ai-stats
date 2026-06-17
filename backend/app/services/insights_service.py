from typing import Any

from app.services.standings_service import build_group_standings


DEFAULT_LIMIT = 5


def build_group_insights(
    fixtures: list[Any],
    group_name: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> dict[str, Any]:
    """
    Build group/team insights from completed fixture standings.

    Insights are based only on completed fixtures with scores, because the
    standings service already filters out scheduled/live matches without final
    results.
    """

    standings = build_group_standings(
        fixtures=fixtures,
        group_name=group_name,
    )

    return {
        "summary": {
            "teams_analyzed": len(standings),
            "groups_analyzed": _count_groups(standings),
            "has_data": bool(standings),
        },
        "group_leaders": _get_group_leaders(standings),
        "strongest_attacks": _limit_rows(
            _sort_by_strongest_attack(standings),
            limit,
        ),
        "best_defences": _limit_rows(
            _sort_by_best_defence(standings),
            limit,
        ),
        "unbeaten_teams": _limit_rows(
            _sort_by_table_strength(
                [team for team in standings if team["losses"] == 0]
            ),
            limit,
        ),
        "winless_teams": _limit_rows(
            _sort_by_winless_order(
                [team for team in standings if team["wins"] == 0]
            ),
            limit,
        ),
    }


def _count_groups(standings: list[dict[str, Any]]) -> int:
    return len({
        team["group_name"]
        for team in standings
        if team.get("group_name")
    })


def _get_group_leaders(standings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    leaders_by_group: dict[str, dict[str, Any]] = {}

    for team in standings:
        group_name = team.get("group_name")

        if not group_name:
            continue

        if group_name not in leaders_by_group:
            leaders_by_group[group_name] = team

    return [
        leaders_by_group[group_name]
        for group_name in sorted(leaders_by_group)
    ]


def _sort_by_table_strength(teams: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        teams,
        key=lambda team: (
            team["group_name"],
            -team["points"],
            -team["goal_difference"],
            -team["goals_for"],
            team["team"],
        ),
    )


def _sort_by_strongest_attack(teams: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        teams,
        key=lambda team: (
            -team["goals_for"],
            -team["points"],
            -team["goal_difference"],
            team["goals_against"],
            team["team"],
        ),
    )


def _sort_by_best_defence(teams: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        teams,
        key=lambda team: (
            team["goals_against"],
            -team["points"],
            -team["goal_difference"],
            -team["goals_for"],
            team["team"],
        ),
    )


def _sort_by_winless_order(teams: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        teams,
        key=lambda team: (
            -team["losses"],
            team["points"],
            team["goal_difference"],
            team["goals_for"],
            team["team"],
        ),
    )


def _limit_rows(
    rows: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    if limit <= 0:
        return []

    return rows[:limit]
