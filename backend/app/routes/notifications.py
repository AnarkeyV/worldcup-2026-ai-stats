from fastapi import APIRouter, HTTPException

from app.services.metrics_service import record_notification_result
from app.services.telegram_notifier import (
    build_completed_fixture_message,
    send_telegram_message,
)

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.post("/telegram/test")
def send_test_telegram_notification():
    fixture = {
        "competition": "FIFA World Cup 2026",
        "stage": "Test Notification",
        "home_team": "Mexico",
        "away_team": "South Africa",
        "home_score": 2,
        "away_score": 0,
        "venue": "Estadio Azteca",
    }

    message = build_completed_fixture_message(fixture)

    try:
        result = send_telegram_message(message)

        record_notification_result(
            channel="telegram",
            status="sent",
        )

        return {
            "message": "Telegram test notification sent successfully",
            "telegram_response": result,
        }

    except ValueError as error:
        record_notification_result(
            channel="telegram",
            status="skipped",
        )

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
