import pytest

from app.services.telegram_notifier import (
    build_completed_fixture_message,
    send_telegram_message,
)


def test_build_completed_fixture_message():
    fixture = {
        "competition": "FIFA World Cup 2026",
        "stage": "Group Stage",
        "home_team": "Mexico",
        "away_team": "South Africa",
        "home_score": 2,
        "away_score": 0,
        "venue": "Estadio Azteca",
    }

    message = build_completed_fixture_message(fixture)

    assert "🏁 Match Completed" in message
    assert "FIFA World Cup 2026" in message
    assert "Group Stage" in message
    assert "Mexico 2 - 0 South Africa" in message
    assert "Venue: Estadio Azteca" in message


def test_send_telegram_message_without_bot_token(monkeypatch):
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_bot_token",
        "replace_me",
    )
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_chat_id",
        "123456",
    )

    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is not configured."):
        send_telegram_message("Test message")


def test_send_telegram_message_without_chat_id(monkeypatch):
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_bot_token",
        "fake-token",
    )
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_chat_id",
        "replace_me",
    )

    with pytest.raises(ValueError, match="TELEGRAM_CHAT_ID is not configured."):
        send_telegram_message("Test message")