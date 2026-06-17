from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fixture import Fixture
from app.services.local_llama_client import LocalLlamaClient
from app.services.standings_service import COMPLETED_STATUSES, build_group_standings

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)

DISPLAY_TIMEZONE = ZoneInfo("Asia/Singapore")
DISPLAY_TIMEZONE_LABEL = "SGT"

LIVE_STATUSES = {
    "live",
}

SCHEDULED_STATUSES = {
    "scheduled",
    "upcoming",
    "not_started",
    "not started",
}


def get_llama_client() -> LocalLlamaClient:
    return LocalLlamaClient()


def normalize_fixture_status(fixture: Fixture) -> str:
    return str(getattr(fixture, "status", "") or "").strip().lower()


def is_completed_fixture(fixture: Fixture) -> bool:
    return normalize_fixture_status(fixture) in COMPLETED_STATUSES


def is_live_fixture(fixture: Fixture) -> bool:
    return normalize_fixture_status(fixture) in LIVE_STATUSES


def is_scheduled_fixture(fixture: Fixture) -> bool:
    return normalize_fixture_status(fixture) in SCHEDULED_STATUSES


def format_fixture_result_state(fixture: Fixture) -> str:
    if is_completed_fixture(fixture):
        if fixture.home_score is not None and fixture.away_score is not None:
            return (
                f"MATCH_STATE=COMPLETED_FINAL | "
                f"FINAL_SCORE={fixture.home_team} {fixture.home_score}-{fixture.away_score} {fixture.away_team} | "
                f"RESULT_SENTENCE={fixture.home_team} defeated {fixture.away_team} "
                f"{fixture.home_score}-{fixture.away_score}."
            )

        return (
            "MATCH_STATE=COMPLETED_FINAL | "
            "FINAL_SCORE=score unavailable | "
            "RESULT_SENTENCE=This match is complete, but the score is unavailable."
        )

    if is_live_fixture(fixture):
        if fixture.home_score is not None and fixture.away_score is not None:
            return (
                f"MATCH_STATE=LIVE_NOW | "
                f"LIVE_SCORE={fixture.home_team} {fixture.home_score}-{fixture.away_score} {fixture.away_team} | "
                f"RESULT_SENTENCE={fixture.home_team} and {fixture.away_team} are currently playing."
            )

        return (
            "MATCH_STATE=LIVE_NOW | "
            "LIVE_SCORE=score unavailable | "
            "RESULT_SENTENCE=This match is currently live."
        )

    if is_scheduled_fixture(fixture):
        return (
            "MATCH_STATE=UPCOMING_NOT_PLAYED | "
            "FINAL_SCORE=not available because the match has not been played | "
            "RESULT_SENTENCE=This match is scheduled and has not been played yet."
        )

    return (
        f"MATCH_STATE=UNKNOWN | "
        f"RAW_STATUS={fixture.status or 'unknown'} | "
        "RESULT_SENTENCE=The match status is unknown."
    )


def build_fixture_context(fixtures: list[Fixture]) -> str:
    lines = []

    for fixture in fixtures:
        kickoff_time = format_kickoff_display(fixture)
        result_state = format_fixture_result_state(fixture)

        lines.append(
            (
                f"- Fixture ID: {fixture.id} | "
                f"Competition: {fixture.competition or 'FIFA World Cup 2026'} | "
                f"Teams: {fixture.home_team} ({fixture.home_team_code}) vs "
                f"{fixture.away_team} ({fixture.away_team_code}) | "
                f"Group: {fixture.group_name or 'N/A'} | "
                f"Raw status: {fixture.status} | "
                f"Kickoff: {kickoff_time} | "
                f"Venue: {fixture.venue or 'TBC'} | "
                f"{result_state}"
            )
        )

    return "\n".join(lines)


def build_summary_prompt(fixture_context: str) -> str:
    return f"""
You are an assistant for a World Cup 2026 stats dashboard.

Your job is to summarize the fixture information below accurately.

Use only the fixture data provided. Do not invent facts.

Most important rule:
MATCH_STATE is the source of truth.

Status meaning:
- MATCH_STATE=COMPLETED_FINAL means the match is already finished.
- MATCH_STATE=LIVE_NOW means the match is currently being played.
- MATCH_STATE=UPCOMING_NOT_PLAYED means the match has not been played yet.

Strict rules:
- For COMPLETED_FINAL matches, say the match is complete, finished, or final.
- For COMPLETED_FINAL matches, use the provided FINAL_SCORE or RESULT_SENTENCE.
- For COMPLETED_FINAL matches, never say scheduled, upcoming, set to kick off, will play, or has not started.
- For UPCOMING_NOT_PLAYED matches, say the match is upcoming or scheduled.
- For UPCOMING_NOT_PLAYED matches, never invent a final score or winner.
- For LIVE_NOW matches, say the match is live.
- Never say a fixture has no kickoff time unless the Kickoff value is exactly TBC.
- Do not describe a completed result as a future match.
- Keep the summary short and clear.
- Avoid hype and avoid saying "next round" unless the data explicitly says that.

Output style:
- Write 2 to 5 short bullet points.
- Each bullet must be based on the provided fixture data.
- Do not include internal labels such as MATCH_STATE, FINAL_SCORE, or RESULT_SENTENCE in the final answer.

Fixture data:
{fixture_context}
""".strip()


def parse_kickoff_datetime(kickoff_time) -> datetime | None:
    if kickoff_time is None:
        return None

    if isinstance(kickoff_time, datetime):
        return kickoff_time

    if isinstance(kickoff_time, str):
        value = kickoff_time.strip()

        if not value:
            return None

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    return None


def format_datetime_for_display(value: datetime) -> str:
    if value.tzinfo is not None:
        value = value.astimezone(DISPLAY_TIMEZONE)

    formatted = value.strftime("%d %b %Y, %I:%M %p")
    formatted = formatted.replace(", 0", ", ")

    if value.tzinfo is not None:
        return f"{formatted} {DISPLAY_TIMEZONE_LABEL}"

    return formatted


def format_kickoff_display(fixture: Fixture) -> str:
    kickoff_datetime = parse_kickoff_datetime(fixture.kickoff_time)

    if kickoff_datetime is None:
        return "TBC"

    return format_datetime_for_display(kickoff_datetime)


def format_kickoff_phrase(fixture: Fixture, completed: bool = False) -> str:
    kickoff_time = format_kickoff_display(fixture)

    if kickoff_time == "TBC":
        return "with kickoff time still to be confirmed"

    if completed:
        return f"after kicking off on {kickoff_time}"

    return f"with kickoff scheduled for {kickoff_time}"


def build_result_text(fixture: Fixture) -> str:
    if fixture.home_score is None or fixture.away_score is None:
        return "The match is complete, but the final score is not available in the dashboard data"

    if fixture.home_score > fixture.away_score:
        return (
            f"{fixture.home_team} defeated {fixture.away_team} "
            f"{fixture.home_score}-{fixture.away_score}"
        )

    if fixture.away_score > fixture.home_score:
        return (
            f"{fixture.away_team} defeated {fixture.home_team} "
            f"{fixture.away_score}-{fixture.home_score}"
        )

    return (
        f"{fixture.home_team} and {fixture.away_team} drew "
        f"{fixture.home_score}-{fixture.away_score}"
    )


def build_deterministic_fixture_summary(fixture: Fixture) -> str:
    group_text = f" in {fixture.group_name}" if fixture.group_name else ""
    venue_text = f" at {fixture.venue}" if fixture.venue else ""

    if is_completed_fixture(fixture):
        result_text = build_result_text(fixture)
        kickoff_text = format_kickoff_phrase(fixture, completed=True)

        return (
            f"{result_text}{group_text}. "
            f"The match is complete {kickoff_text}{venue_text}. "
            "Final whistle time is not available in the current fixture data."
        )

    if is_scheduled_fixture(fixture):
        kickoff_text = format_kickoff_phrase(fixture)

        return (
            f"{fixture.home_team} vs {fixture.away_team}{group_text} is an upcoming fixture "
            f"{kickoff_text}{venue_text}. No score is available yet because the match has not been played."
        )

    if is_live_fixture(fixture):
        if fixture.home_score is not None and fixture.away_score is not None:
            return (
                f"{fixture.home_team} vs {fixture.away_team}{group_text} is currently live, "
                f"with the score at {fixture.home_score}-{fixture.away_score}."
            )

        return (
            f"{fixture.home_team} vs {fixture.away_team}{group_text} is currently live, "
            f"but no score is available in the dashboard data."
        )

    return (
        f"{fixture.home_team} vs {fixture.away_team}{group_text} has status "
        f"'{fixture.status or 'unknown'}' in the dashboard data."
    )


def format_goal_difference(goal_difference: int) -> str:
    if goal_difference > 0:
        return f"+{goal_difference}"

    return str(goal_difference)


def format_leader_entry(standing: dict) -> str:
    return (
        f"{standing['team']} "
        f"({standing['group_name']}, {standing['points']} pts, "
        f"{format_goal_difference(standing['goal_difference'])} GD)"
    )


def join_readable_list(items: list[str]) -> str:
    if not items:
        return ""

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return f"{', '.join(items[:-1])}, and {items[-1]}"


def build_group_leaders_summary(fixtures: list[Fixture], max_leaders: int = 4) -> str | None:
    standings = build_group_standings(fixtures)

    if not standings:
        return None

    leaders_by_group: dict[str, dict] = {}

    for standing in standings:
        group_name = standing.get("group_name")

        if not group_name:
            continue

        if group_name not in leaders_by_group:
            leaders_by_group[group_name] = standing

    if not leaders_by_group:
        return None

    leader_entries = [
        format_leader_entry(leaders_by_group[group_name])
        for group_name in sorted(leaders_by_group)
    ][:max_leaders]

    return (
        "Current group leaders based on completed fixtures include "
        f"{join_readable_list(leader_entries)}."
    )


def build_deterministic_tournament_summary(fixtures: list[Fixture]) -> str:
    completed_fixtures = [
        fixture for fixture in fixtures
        if is_completed_fixture(fixture)
    ]
    live_fixtures = [
        fixture for fixture in fixtures
        if is_live_fixture(fixture)
    ]
    scheduled_fixtures = [
        fixture for fixture in fixtures
        if is_scheduled_fixture(fixture)
    ]

    lines = []

    if completed_fixtures:
        completed_count = len(completed_fixtures)
        lines.append(
            f"{completed_count} fixture{' has' if completed_count == 1 else 's have'} been completed."
        )

        for fixture in completed_fixtures[:2]:
            lines.append(build_deterministic_fixture_summary(fixture))

        group_leaders_summary = build_group_leaders_summary(fixtures)

        if group_leaders_summary:
            lines.append(group_leaders_summary)

    if live_fixtures:
        live_count = len(live_fixtures)
        lines.append(
            f"{live_count} fixture{' is' if live_count == 1 else 's are'} currently live."
        )

    if scheduled_fixtures:
        scheduled_count = len(scheduled_fixtures)
        lines.append(
            f"{scheduled_count} fixture{' is' if scheduled_count == 1 else 's are'} still upcoming."
        )

        for fixture in scheduled_fixtures[:2]:
            lines.append(build_deterministic_fixture_summary(fixture))

    if not lines:
        return "No fixture summary is available yet."

    return "\n".join(f"- {line}" for line in lines)


@router.get("/health")
def ai_health(llama_client: LocalLlamaClient = Depends(get_llama_client)):
    return llama_client.health_check()


@router.get("/fixtures/summary")
def summarize_fixtures(
    db: Session = Depends(get_db),
):
    try:
        fixtures = (
            db.query(Fixture)
            .order_by(Fixture.kickoff_time.asc())
            .all()
        )

        if not fixtures:
            raise HTTPException(
                status_code=404,
                detail="No fixtures available to summarize.",
            )

        summary = build_deterministic_tournament_summary(fixtures)

        return {
            "fixture_count": len(fixtures),
            "provider": "deterministic_tournament_summary",
            "model": "rules_based_v2",
            "summary": summary,
        }

    except HTTPException:
        raise

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while generating fixture summary: {error}",
        ) from error


@router.get("/fixtures/{fixture_id}/summary")
def summarize_fixture_by_id(
    fixture_id: int,
    db: Session = Depends(get_db),
):
    try:
        fixture = db.query(Fixture).filter(Fixture.id == fixture_id).first()

        if fixture is None:
            raise HTTPException(
                status_code=404,
                detail="Fixture not found.",
            )

        summary = build_deterministic_fixture_summary(fixture)

        return {
            "fixture_id": fixture.id,
            "provider": "deterministic_fixture_summary",
            "model": "rules_based_v2",
            "summary": summary,
        }

    except HTTPException:
        raise

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while generating fixture summary: {error}",
        ) from error
