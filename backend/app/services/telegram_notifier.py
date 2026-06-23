from html import escape

import httpx

from app.config import settings


class TelegramNotificationError(RuntimeError):
    """Raised when Telegram is configured but the Telegram API request fails."""


def build_dashboard_link_text(public_dashboard_url: str | None = None) -> str:
    """
    Build a clickable dashboard link block for Telegram messages.

    The optional URL keeps scheduled digests explicit and testable. When it is
    omitted, the configured public dashboard URL is used for existing messages.
    """
    dashboard_url = (
        public_dashboard_url
        if public_dashboard_url is not None
        else settings.public_dashboard_url
    )
    dashboard_url = str(dashboard_url or "").strip()

    if not dashboard_url or dashboard_url == "replace_me":
        return ""

    safe_dashboard_url = escape(dashboard_url, quote=True)

    return f'\n\n📊 <a href="{safe_dashboard_url}">Open dashboard</a>'


def build_completed_fixture_message(fixture: dict) -> str:
    """
    Build a Telegram message for a completed fixture.

    Args:
        fixture (dict): Serialized fixture data.

    Returns:
        str: Human-readable Telegram message.
    """
    home_team = escape(str(fixture["home_team"]))
    away_team = escape(str(fixture["away_team"]))
    home_score = escape(str(fixture.get("home_score", "?")))
    away_score = escape(str(fixture.get("away_score", "?")))
    competition = escape(str(fixture.get("competition", "FIFA World Cup 2026")))
    stage = escape(str(fixture.get("stage", "Match")))
    venue = escape(str(fixture.get("venue") or "Venue TBC"))

    dashboard_link = build_dashboard_link_text()

    return (
        "🏁 Match Completed\n\n"
        f"{competition}\n"
        f"{stage}\n\n"
        f"{home_team} {home_score} - {away_score} {away_team}\n\n"
        f"Venue: {venue}"
        f"{dashboard_link}"
    )


def build_scheduled_completed_fixture_digest(
    fixtures: list[dict],
    public_dashboard_url: str | None = None,
) -> str:
    """Build one Telegram roundup for all fixtures completed in a sync run."""
    result_lines = []

    for fixture in fixtures:
        home_team = escape(str(fixture.get("home_team", "Home team")))
        away_team = escape(str(fixture.get("away_team", "Away team")))
        home_score = escape(str(fixture.get("home_score", "?")))
        away_score = escape(str(fixture.get("away_score", "?")))

        result_lines.append(
            f"• {home_team} {home_score}–{away_score} {away_team}"
        )

    dashboard_link = build_dashboard_link_text(public_dashboard_url)

    return (
        "🏁 World Cup Matchday Update\n\n"
        "Newly completed matches:\n"
        f"{chr(10).join(result_lines)}"
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
                "parse_mode": "HTML",
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


def send_scheduled_completed_fixture_digest(
    fixtures: list[dict],
    enabled: bool,
    public_dashboard_url: str,
) -> dict:
    """
    Send one scheduled Telegram digest for newly completed fixtures.

    Scheduled delivery is opt-in. An empty completion set is intentionally
    silent so a scheduled provider sync does not create Telegram noise.
    """
    if not enabled:
        return {
            "status": "skipped",
            "reason": "Scheduled Telegram digest is disabled by configuration.",
            "sent": 0,
        }

    if not fixtures:
        return {
            "status": "skipped",
            "reason": "No newly completed fixtures",
            "sent": 0,
        }

    message = build_scheduled_completed_fixture_digest(
        fixtures=fixtures,
        public_dashboard_url=public_dashboard_url,
    )
    send_telegram_message(message)

    return {
        "status": "sent",
        "sent": 1,
        "fixture_count": len(fixtures),
    }
