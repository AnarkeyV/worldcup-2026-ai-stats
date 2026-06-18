from app.services.telegram_notifier import TelegramNotificationError


def test_get_telegram_notification_status_without_credentials(client, monkeypatch):
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_bot_token",
        "replace_me",
    )
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_chat_id",
        "replace_me",
    )

    response = client.get("/notifications/telegram/status")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "channel": "telegram",
        "bot_token_configured": False,
        "chat_id_configured": False,
        "ready": False,
    }


def test_send_test_telegram_notification_without_bot_token(client, monkeypatch):
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_bot_token",
        "replace_me",
    )
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_chat_id",
        "123456",
    )

    response = client.post("/notifications/telegram/test")

    assert response.status_code == 400
    assert response.json()["detail"] == "TELEGRAM_BOT_TOKEN is not configured."


def test_send_test_telegram_notification_without_chat_id(client, monkeypatch):
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_bot_token",
        "fake-token",
    )
    monkeypatch.setattr(
        "app.services.telegram_notifier.settings.telegram_chat_id",
        "replace_me",
    )

    response = client.post("/notifications/telegram/test")

    assert response.status_code == 400
    assert response.json()["detail"] == "TELEGRAM_CHAT_ID is not configured."


def test_send_test_telegram_notification_success(client, monkeypatch):
    def fake_send_telegram_message(message: str):
        assert "🏁 Match Completed" in message
        assert "Mexico 2 - 0 South Africa" in message

        return {
            "ok": True,
            "result": {
                "message_id": 1,
            },
        }

    monkeypatch.setattr(
        "app.routes.notifications.send_telegram_message",
        fake_send_telegram_message,
    )

    response = client.post("/notifications/telegram/test")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Telegram test notification sent successfully"
    assert data["telegram_response"]["ok"] is True
    assert data["telegram_response"]["result"]["message_id"] == 1


def test_send_test_telegram_notification_api_failure(client, monkeypatch):
    def fake_send_telegram_message(message: str):
        raise TelegramNotificationError("Telegram API returned status 401.")

    monkeypatch.setattr(
        "app.routes.notifications.send_telegram_message",
        fake_send_telegram_message,
    )

    response = client.post("/notifications/telegram/test")

    assert response.status_code == 502
    assert response.json()["detail"] == "Telegram API returned status 401."
