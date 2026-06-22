from typing import Any

from app.services.standings_service import COMPLETED_STATUSES, build_group_standings


DEFAULT_AI_INSIGHTS_LIMIT = 5
TOP_GROUP_RACE_TEAMS = 2

LIVE_STATUSES = {
    "live",
}

SCHEDULED_STATUSES = {
    "scheduled",
    "upcoming",
    "not_started",
    "not started",
}


def build_ai_insights(
    fixtures: list[Any],
    group_name: str | None = None,
    team: str | None = None,
    sync_status: dict[str, Any] | None = None,
    limit: int = DEFAULT_AI_INSIGHTS_LIMIT,
) -> dict[str, Any]:
    """
    Build structured AI-friendly insights from fixture, standings, and sync data.

    This service intentionally uses deterministic rules. It is safe for demos,
    tests, and offline runtime because it does not require Local Llama to be
    available.
    """

    safe_limit = max(1, limit)
    filtered_fixtures = _filter_fixtures(
        fixtures=fixtures,
        group_name=group_name,
        team=team,
    )
    status_counts = _count_fixture_statuses(filtered_fixtures)
    standings = build_group_standings(
        fixtures=filtered_fixtures,
        group_name=group_name,
    )
    group_race = _build_group_race(standings)

    insights = []

    if not filtered_fixtures:
        insights.append(
            _build_insight(
                title="No fixture data available",
                category="fixtures",
                message=_build_empty_fixture_message(
                    group_name=group_name,
                    team=team,
                ),
            )
        )
    else:
        insights.append(
            _build_fixture_availability_insight(
                fixture_count=len(filtered_fixtures),
                status_counts=status_counts,
                group_name=group_name,
                team=team,
            )
        )

        completed_insight = _build_completed_fixture_insight(
            fixtures=filtered_fixtures,
            completed_count=status_counts["completed"],
        )

        if completed_insight:
            insights.append(completed_insight)

        group_leaders_insight = _build_group_leaders_insight(standings)

        if group_leaders_insight:
            insights.append(group_leaders_insight)

        group_race_insight = _build_group_race_insight(group_race)

        if group_race_insight:
            insights.append(group_race_insight)

    sync_insight = _build_sync_status_insight(sync_status)

    if sync_insight:
        insights.append(sync_insight)

    limited_insights = insights[:safe_limit]

    return {
        "status": "ok",
        "mode": "fallback",
        "provider": "rules_based_ai_insights",
        "model": "rules_based_v1",
        "summary": _build_summary(
            fixture_count=len(filtered_fixtures),
            status_counts=status_counts,
            group_name=group_name,
            team=team,
            sync_status=sync_status,
        ),
        "filters": {
            "group_name": group_name,
            "team": team,
            "limit": safe_limit,
        },
        "metadata": {
            "fixture_count": len(filtered_fixtures),
            "completed_count": status_counts["completed"],
            "live_count": status_counts["live"],
            "scheduled_count": status_counts["scheduled"],
            "other_status_count": status_counts["other"],
            "teams_analyzed": len(standings),
            "groups_analyzed": _count_groups(standings),
            "group_race_group_count": len(group_race["groups"]),
            "sync_status": _get_sync_status_value(sync_status),
        },
        "group_race": group_race,
        "insights": limited_insights,
    }


def _filter_fixtures(
    fixtures: list[Any],
    group_name: str | None = None,
    team: str | None = None,
) -> list[Any]:
    filtered_fixtures = list(fixtures)

    if group_name:
        filtered_fixtures = [
            fixture for fixture in filtered_fixtures
            if getattr(fixture, "group_name", None) == group_name
        ]

    if team:
        team_search = team.strip().lower()

        filtered_fixtures = [
            fixture for fixture in filtered_fixtures
            if team_search in _get_fixture_team_values(fixture)
        ]

    return filtered_fixtures


def _get_fixture_team_values(fixture: Any) -> set[str]:
    values = {
        getattr(fixture, "home_team", "") or "",
        getattr(fixture, "away_team", "") or "",
        getattr(fixture, "home_team_code", "") or "",
        getattr(fixture, "away_team_code", "") or "",
    }

    return {
        value.strip().lower()
        for value in values
        if value and value.strip()
    }


def _count_fixture_statuses(fixtures: list[Any]) -> dict[str, int]:
    counts = {
        "completed": 0,
        "live": 0,
        "scheduled": 0,
        "other": 0,
    }

    for fixture in fixtures:
        status = _normalize_status(fixture)

        if status in COMPLETED_STATUSES:
            counts["completed"] += 1
        elif status in LIVE_STATUSES:
            counts["live"] += 1
        elif status in SCHEDULED_STATUSES:
            counts["scheduled"] += 1
        else:
            counts["other"] += 1

    return counts


def _normalize_status(fixture: Any) -> str:
    return str(getattr(fixture, "status", "") or "").strip().lower()


def _build_summary(
    fixture_count: int,
    status_counts: dict[str, int],
    group_name: str | None = None,
    team: str | None = None,
    sync_status: dict[str, Any] | None = None,
) -> str:
    if fixture_count == 0:
        return _build_empty_fixture_message(
            group_name=group_name,
            team=team,
        )

    scope = _build_scope_text(group_name=group_name, team=team)
    completed_count = status_counts["completed"]
    scheduled_count = status_counts["scheduled"]
    live_count = status_counts["live"]

    status_parts = []

    if completed_count:
        status_parts.append(f"{completed_count} completed")
    if live_count:
        status_parts.append(f"{live_count} live")
    if scheduled_count:
        status_parts.append(f"{scheduled_count} scheduled")

    status_text = ", ".join(status_parts) if status_parts else "available"

    summary = (
        f"{fixture_count} {_pluralize('fixture', fixture_count)} "
        f"{_pluralize('is', fixture_count, plural='are')} available for AI insights"
        f"{scope}, with {status_text} fixture data."
    )

    sync_status_value = _get_sync_status_value(sync_status)

    if sync_status_value == "success":
        summary += " The latest provider sync completed successfully."
    elif sync_status_value and sync_status_value != "not_started":
        summary += f" The latest provider sync status is {sync_status_value}."

    return summary


def _build_empty_fixture_message(
    group_name: str | None = None,
    team: str | None = None,
) -> str:
    scope = _build_scope_text(group_name=group_name, team=team)

    if scope:
        return f"No fixture data is available for AI insights{scope}."

    return "No fixture data is available for AI insights yet."


def _build_scope_text(
    group_name: str | None = None,
    team: str | None = None,
) -> str:
    scope_parts = []

    if group_name:
        scope_parts.append(group_name)

    if team:
        scope_parts.append(team)

    if not scope_parts:
        return ""

    return f" for {' / '.join(scope_parts)}"


def _build_fixture_availability_insight(
    fixture_count: int,
    status_counts: dict[str, int],
    group_name: str | None = None,
    team: str | None = None,
) -> dict[str, str]:
    scope = _build_scope_text(group_name=group_name, team=team)

    return _build_insight(
        title="Fixture data available",
        category="fixtures",
        message=(
            f"{fixture_count} {_pluralize('fixture', fixture_count)} "
            f"{_pluralize('is', fixture_count, plural='are')} available{scope}. "
            f"Completed: {status_counts['completed']}. "
            f"Live: {status_counts['live']}. "
            f"Scheduled: {status_counts['scheduled']}."
        ),
    )


def _build_completed_fixture_insight(
    fixtures: list[Any],
    completed_count: int,
) -> dict[str, str] | None:
    if completed_count == 0:
        return None

    completed_fixtures = [
        fixture for fixture in fixtures
        if _normalize_status(fixture) in COMPLETED_STATUSES
    ]

    sample_results = [
        _format_result_line(fixture)
        for fixture in completed_fixtures[:2]
    ]

    message = (
        f"{completed_count} completed "
        f"{_pluralize('fixture', completed_count)} can be used for standings and form analysis."
    )

    if sample_results:
        message += f" Example: {join_readable_list(sample_results)}."

    return _build_insight(
        title="Completed results detected",
        category="results",
        message=message,
    )


def _format_result_line(fixture: Any) -> str:
    home_team = getattr(fixture, "home_team", "Home Team")
    away_team = getattr(fixture, "away_team", "Away Team")
    home_score = getattr(fixture, "home_score", None)
    away_score = getattr(fixture, "away_score", None)

    if home_score is None or away_score is None:
        return f"{home_team} vs {away_team} is complete"

    return f"{home_team} {home_score}-{away_score} {away_team}"


def _build_group_leaders_insight(
    standings: list[dict[str, Any]],
) -> dict[str, str] | None:
    leaders = _get_group_leaders(standings)

    if not leaders:
        return None

    leader_entries = [
        _format_leader_entry(leader)
        for leader in leaders[:4]
    ]

    return _build_insight(
        title="Group leaders available",
        category="standings",
        message=(
            "Current group leaders based on completed fixtures include "
            f"{join_readable_list(leader_entries)}."
        ),
    )


def _get_group_leaders(
    standings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
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


def _format_leader_entry(standing: dict[str, Any]) -> str:
    return (
        f"{standing['team']} "
        f"({standing['group_name']}, {standing['points']} pts, "
        f"{_format_goal_difference(standing['goal_difference'])} GD)"
    )


def _format_goal_difference(goal_difference: int) -> str:
    if goal_difference > 0:
        return f"+{goal_difference}"

    return str(goal_difference)


def _build_group_race(
    standings: list[dict[str, Any]],
) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}

    for standing in standings:
        group_name = str(standing.get("group_name") or "").strip()

        if not group_name:
            continue

        groups.setdefault(group_name, []).append(standing)

    race_groups = []

    for group_name in sorted(groups):
        ordered_teams = sorted(
            groups[group_name],
            key=lambda standing: (
                -_as_int(standing.get("points")),
                -_as_int(standing.get("goal_difference")),
                -_as_int(standing.get("goals_for")),
                str(standing.get("team") or ""),
            ),
        )

        top_teams = [
            _serialize_group_race_team(standing, rank=index + 1)
            for index, standing in enumerate(ordered_teams[:TOP_GROUP_RACE_TEAMS])
        ]

        if top_teams:
            race_groups.append(
                {
                    "group_name": group_name,
                    "teams": top_teams,
                }
            )

    return {
        "teams_per_group": TOP_GROUP_RACE_TEAMS,
        "groups": race_groups,
    }


def _serialize_group_race_team(
    standing: dict[str, Any],
    rank: int,
) -> dict[str, Any]:
    return {
        "rank": rank,
        "team": standing.get("team") or "Team unavailable",
        "team_code": standing.get("team_code") or "",
        "played": _as_int(standing.get("played")),
        "points": _as_int(standing.get("points")),
        "goal_difference": _as_int(standing.get("goal_difference")),
        "goals_for": _as_int(standing.get("goals_for")),
        "goals_against": _as_int(standing.get("goals_against")),
    }


def _as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _build_group_race_insight(
    group_race: dict[str, Any],
) -> dict[str, str] | None:
    groups = group_race.get("groups") or []

    if not groups:
        return None

    group_count = len(groups)
    teams_per_group = group_race.get("teams_per_group") or TOP_GROUP_RACE_TEAMS

    return _build_insight(
        title="Top two group positions",
        category="standings",
        message=(
            f"The Group Race board shows the current top {teams_per_group} teams "
            f"in each of {group_count} completed-fixture group"
            f"{'' if group_count == 1 else 's'}, ordered by points, goal difference, "
            "and goals scored."
        ),
    )


def _build_sync_status_insight(
    sync_status: dict[str, Any] | None,
) -> dict[str, str] | None:
    if not sync_status:
        return None

    status = _get_sync_status_value(sync_status)
    provider = sync_status.get("provider") or "unknown provider"
    source = sync_status.get("source") or "unknown source"

    if status == "success":
        message = (
            f"The latest {source} fixture sync completed successfully "
            f"using {provider}."
        )
    elif status == "not_started":
        message = "No fixture sync run has been recorded yet."
    else:
        message = (
            f"The latest {source} fixture sync status is {status} "
            f"using {provider}."
        )

    return _build_insight(
        title="Provider sync runtime status",
        category="sync",
        message=message,
    )


def _count_groups(standings: list[dict[str, Any]]) -> int:
    return len({
        team["group_name"]
        for team in standings
        if team.get("group_name")
    })


def _get_sync_status_value(sync_status: dict[str, Any] | None) -> str | None:
    if not sync_status:
        return None

    return str(sync_status.get("status") or "unknown").strip().lower()


def _build_insight(
    title: str,
    category: str,
    message: str,
) -> dict[str, str]:
    return {
        "title": title,
        "category": category,
        "message": message,
    }


def join_readable_list(items: list[str]) -> str:
    if not items:
        return ""

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _pluralize(
    singular: str,
    count: int,
    plural: str | None = None,
) -> str:
    if count == 1:
        return singular

    if plural:
        return plural

    return f"{singular}s"
