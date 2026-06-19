import httpx

from app.config import settings


class TelegramNotificationError(RuntimeError):
    """Raised when Telegram is configured but the Telegram API request fails."""


def build_dashboard_link_text() -> str:
    """
    Build a safe dashboard link block for Telegram messages.

    The URL is intentionally public-facing configuration so Telegram alerts can
    open the dashboard from mobile when PUBLIC_DASHBOARD_URL points to a
    Cloudflare Tunnel or another reachable URL.
    """
    dashboard_url = (settings.public_dashboard_url or "").strip()

    if not dashboard_url or dashboard_url == "replace_me":
        return ""

    return f"\n\n📊 Open dashboard:\n{dashboard_url}"


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
    home_score = fixture.get("home_score", "?")
    away_score = fixture.get("away_score", "?")
    competition = fixture.get("competition", "FIFA World Cup 2026")
    stage = fixture.get("stage", "Match")
    venue = fixture.get("venue") or "Venue TBC"

    dashboard_link = build_dashboard_link_text()

    return (
        "🏁 Match Completed\n\n"
        f"{competition}\n"
        f"{stage}\n\n"
        f"{home_team} {home_score} - {away_score} {away_team}\n\n"
        f"Venue: {venue}"
        f"{dashboard_link}"
    )


def send_telegram_message(message: str) -> dict:
    """
    Send a Telegram message using the configured bot token and chat ID.

    This function is safe by default because it raises a clear ValueError when
    Telegram credentials are not configured.

    If credentials are configured but Telegram cannot be reached, or Telegram
    rejects the message, TelegramNotificationError is raised.
    """
    if not message or not message.strip():
        raise ValueError("Telegram message cannot be empty.")

    if not settings.telegram_bot_token or settings.telegram_bot_token == "replace_me":
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured.")

    if not settings.telegram_chat_id or settings.telegram_chat_id == "replace_me":
        raise ValueError("TELEGRAM_CHAT_ID is not configured.")

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"

    try:
        response = httpx.post(
            url,
            json={
                "chat_id": settings.telegram_chat_id,
                "text": message,
                "disable_web_page_preview": True,
            },
            timeout=20.0,
        )
        response.raise_for_status()

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        raise TelegramNotificationError(
            f"Telegram API returned status {status_code}."
        ) from error

    except httpx.RequestError as error:
        raise TelegramNotificationError(
            f"Telegram API request failed: {error}"
        ) from error

    try:
        data = response.json()
    except ValueError as error:
        raise TelegramNotificationError(
            "Telegram API returned an invalid JSON response."
        ) from error

    if not data.get("ok", False):
        description = data.get("description", "Unknown Telegram API error.")
        raise TelegramNotificationError(
            f"Telegram API rejected the message: {description}"
        )

    return data


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
