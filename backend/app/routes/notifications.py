from fastapi import APIRouter, HTTPException

from app.services.metrics_service import record_notification_result
from app.services.telegram_notifier import (
    TelegramNotificationError,
    build_completed_fixture_message,
    send_telegram_message,
)

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.get("/telegram/status")
def get_telegram_notification_status():
    """
    Return safe Telegram notification configuration status.

    This endpoint does not expose the bot token or chat ID values.
    """
    from app.config import settings

    bot_token_configured = bool(settings.telegram_bot_token) and (
        settings.telegram_bot_token != "replace_me"
    )
    chat_id_configured = bool(settings.telegram_chat_id) and (
        settings.telegram_chat_id != "replace_me"
    )

    return {
        "channel": "telegram",
        "bot_token_configured": bot_token_configured,
        "chat_id_configured": chat_id_configured,
        "ready": bot_token_configured and chat_id_configured,
    }


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

    except TelegramNotificationError as error:
        record_notification_result(
            channel="telegram",
            status="failed",
        )

        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
