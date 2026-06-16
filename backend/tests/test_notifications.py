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