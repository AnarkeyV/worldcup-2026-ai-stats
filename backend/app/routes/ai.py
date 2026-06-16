from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fixture import Fixture
from app.services.local_llama_client import LocalLlamaClient

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)


def get_llama_client() -> LocalLlamaClient:
    return LocalLlamaClient()


def build_fixture_context(fixtures: list[Fixture]) -> str:
    lines = []

    for fixture in fixtures:
        if fixture.home_score is not None and fixture.away_score is not None:
            score = f"{fixture.home_score}-{fixture.away_score}"
        else:
            score = "match has not started"

        if fixture.kickoff_time:
            kickoff_time = (
                fixture.kickoff_time.isoformat()
                if hasattr(fixture.kickoff_time, "isoformat")
                else str(fixture.kickoff_time)
            )
        else:
            kickoff_time = "TBC"

        lines.append(
            (
                f"- {fixture.home_team} ({fixture.home_team_code}) vs "
                f"{fixture.away_team} ({fixture.away_team_code}) | "
                f"Group: {fixture.group_name or 'N/A'} | "
                f"Status: {fixture.status} | "
                f"Kickoff: {kickoff_time} | "
                f"Score: {score} | "
                f"Venue: {fixture.venue or 'TBC'}"
            )
        )

    return "\n".join(lines)


def build_summary_prompt(fixture_context: str) -> str:
    return f"""
You are an assistant for a World Cup 2026 stats dashboard.

Summarize the fixture information below in clear, simple language.

Important rules:
- Keep the summary short.
- Only use the fixture data provided below.
- Do not invent facts.
- If Status is complete, describe it as a completed result.
- If Status is scheduled, describe it as an upcoming scheduled match.
- Never say "unscheduled" when the Status is scheduled.
- Never say a fixture has no kickoff time unless the Kickoff value is exactly TBC.
- If a fixture has a Kickoff date/time, say it is scheduled for that date/time.
- Use a helpful sports-analysis tone.

Fixture data:
{fixture_context}
""".strip()


@router.get("/health")
def ai_health(llama_client: LocalLlamaClient = Depends(get_llama_client)):
    return llama_client.health_check()


@router.get("/fixtures/summary")
def summarize_fixtures(
    db: Session = Depends(get_db),
    llama_client: LocalLlamaClient = Depends(get_llama_client),
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

        fixture_context = build_fixture_context(fixtures)
        prompt = build_summary_prompt(fixture_context)
        result = llama_client.generate_summary(prompt)

        return {
            "fixture_count": len(fixtures),
            "provider": result["provider"],
            "model": result["model"],
            "summary": result["summary"],
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while generating fixture summary: {error}",
        ) from error


@router.get("/fixtures/{fixture_id}/summary")
def summarize_fixture_by_id(
    fixture_id: int,
    db: Session = Depends(get_db),
    llama_client: LocalLlamaClient = Depends(get_llama_client),
):
    try:
        fixture = db.query(Fixture).filter(Fixture.id == fixture_id).first()

        if fixture is None:
            raise HTTPException(
                status_code=404,
                detail="Fixture not found.",
            )

        fixture_context = build_fixture_context([fixture])
        prompt = build_summary_prompt(fixture_context)
        result = llama_client.generate_summary(prompt)

        return {
            "fixture_id": fixture.id,
            "provider": result["provider"],
            "model": result["model"],
            "summary": result["summary"],
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database error while generating fixture summary: {error}",
        ) from error