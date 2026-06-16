import httpx

from app.config import settings


def build_completed_fixture_message(fixture: dict) -> str:
    """
    Build a Telegram message for a completed fixture.

    Args:
        fixture (dict): Serialized fixture data.

    Returns:
        str: Human-readable Telegram message.
    """
    home_team = fixture["home_team"]
    away_team = fixture["away_team"]
    home_score = fixture["home_score"]
    away_score = fixture["away_score"]
    competition = fixture.get("competition", "FIFA World Cup 2026")
    stage = fixture.get("stage", "Match")
    venue = fixture.get("venue") or "Venue TBC"

    return (
        "🏁 Match Completed\n\n"
        f"{competition}\n"
        f"{stage}\n\n"
        f"{home_team} {home_score} - {away_score} {away_team}\n\n"
        f"Venue: {venue}"
    )


def send_telegram_message(message: str) -> dict:
    """
    Send a Telegram message using the configured bot token and chat ID.

    This function is safe by default because it raises a clear error when
    Telegram credentials are not configured.
    """
    if not settings.telegram_bot_token or settings.telegram_bot_token == "replace_me":
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured.")

    if not settings.telegram_chat_id or settings.telegram_chat_id == "replace_me":
        raise ValueError("TELEGRAM_CHAT_ID is not configured.")

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"

    response = httpx.post(
        url,
        json={
            "chat_id": settings.telegram_chat_id,
            "text": message,
        },
        timeout=20.0,
    )
    response.raise_for_status()

    return response.json()


def send_completed_fixture_notifications(fixtures: list[dict]) -> dict:
    """
    Send Telegram notifications for completed fixtures.

    Args:
        fixtures (list[dict]): Serialized completed fixture data.

    Returns:
        dict: Summary of sent notifications.
    """
    sent = 0
    messages = []

    for fixture in fixtures:
        message = build_completed_fixture_message(fixture)
        send_telegram_message(message)

        sent += 1
        messages.append(message)

    return {
        "sent": sent,
        "messages": messages,
    }