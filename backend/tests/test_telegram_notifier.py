import httpx
import pytest

from app.services.telegram_notifier import (
    TelegramNotificationError,
    build_completed_fixture_message,
    send_completed_fixture_notifications,
    send_telegram_message,
)


def test_build_completed_fixture_message(monkeypatch):
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.public_dashboard_url",
        "https://worldcup.example.com/dashboard",
    )

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
    assert "📊 Open dashboard:" in message
    assert "https://worldcup.example.com/dashboard" in message


def test_build_completed_fixture_message_without_dashboard_link(monkeypatch):
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.public_dashboard_url",
        "",
    )

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
    assert "Mexico 2 - 0 South Africa" in message
    assert "📊 Open dashboard:" not in message


def test_send_telegram_message_without_message(monkeypatch):
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_bot_token",
        "fake-token",
    )
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_chat_id",
        "123456",
    )

    with pytest.raises(ValueError, match="Telegram message cannot be empty."):
        send_telegram_message("")


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


def test_send_telegram_message_success(monkeypatch):
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_bot_token",
        "fake-token",
    )
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_chat_id",
        "123456",
    )

    def fake_post(url, json, timeout):
        assert url == "https://api.telegram.org/botfake-token/sendMessage"
        assert json["chat_id"] == "123456"
        assert json["text"] == "Test message"
        assert json["disable_web_page_preview"] is True
        assert timeout == 20.0

        return httpx.Response(
            status_code=200,
            json={
                "ok": True,
                "result": {
                    "message_id": 1,
                },
            },
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr("app.services.telegram_notifier.httpx.post", fake_post)

    result = send_telegram_message("Test message")

    assert result["ok"] is True
    assert result["result"]["message_id"] == 1


def test_send_telegram_message_http_status_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_bot_token",
        "fake-token",
    )
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_chat_id",
        "123456",
    )

    def fake_post(url, json, timeout):
        return httpx.Response(
            status_code=401,
            json={
                "ok": False,
                "description": "Unauthorized",
            },
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr("app.services.telegram_notifier.httpx.post", fake_post)

    with pytest.raises(
        TelegramNotificationError,
        match="Telegram API returned status 401.",
    ):
        send_telegram_message("Test message")


def test_send_telegram_message_request_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_bot_token",
        "fake-token",
    )
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_chat_id",
        "123456",
    )

    def fake_post(url, json, timeout):
        request = httpx.Request("POST", url)
        raise httpx.RequestError("network unavailable", request=request)

    monkeypatch.setattr("app.services.telegram_notifier.httpx.post", fake_post)

    with pytest.raises(
        TelegramNotificationError,
        match="Telegram API request failed",
    ):
        send_telegram_message("Test message")


def test_send_telegram_message_rejected_by_telegram(monkeypatch):
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_bot_token",
        "fake-token",
    )
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_chat_id",
        "123456",
    )

    def fake_post(url, json, timeout):
        return httpx.Response(
            status_code=200,
            json={
                "ok": False,
                "description": "Bad Request: chat not found",
            },
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr("app.services.telegram_notifier.httpx.post", fake_post)

    with pytest.raises(
        TelegramNotificationError,
        match="Telegram API rejected the message: Bad Request: chat not found",
    ):
        send_telegram_message("Test message")


def test_send_completed_fixture_notifications(monkeypatch):
    sent_messages = []

    def fake_send_telegram_message(message: str):
        sent_messages.append(message)
        return {"ok": True}

    monkeypatch.setattr(
        "app.services.telegram_notifier.send_telegram_message",
        fake_send_telegram_message,
    )

    fixtures = [
        {
            "competition": "FIFA World Cup 2026",
            "stage": "Group Stage",
            "home_team": "Mexico",
            "away_team": "South Africa",
            "home_score": 2,
            "away_score": 0,
            "venue": "Estadio Azteca",
        },
        {
            "competition": "FIFA World Cup 2026",
            "stage": "Group Stage",
            "home_team": "United States",
            "away_team": "Paraguay",
            "home_score": 4,
            "away_score": 1,
            "venue": "SoFi Stadium",
        },
    ]

    result = send_completed_fixture_notifications(fixtures)

    assert result["sent"] == 2
    assert len(result["messages"]) == 2
    assert len(sent_messages) == 2
    assert "Mexico 2 - 0 South Africa" in sent_messages[0]
    assert "United States 4 - 1 Paraguay" in sent_messages[1]
