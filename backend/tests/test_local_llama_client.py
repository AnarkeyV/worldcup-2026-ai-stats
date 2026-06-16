import pytest

from app.services.local_llama_client import LocalLlamaClient


def test_local_llama_client_builds_endpoint_url():
    client = LocalLlamaClient(
        base_url="http://127.0.0.1:11434/",
        model="llama3.2:1b",
        timeout_seconds=5,
    )

    assert client._build_url("/api/tags") == "http://127.0.0.1:11434/api/tags"
    assert client._build_url("api/tags") == "http://127.0.0.1:11434/api/tags"


def test_local_llama_client_rejects_empty_prompt():
    client = LocalLlamaClient()

    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        client.generate_summary("")


def test_local_llama_client_generates_summary(monkeypatch):
    client = LocalLlamaClient(
        base_url="http://127.0.0.1:11434",
        model="llama3.2:1b",
        timeout_seconds=5,
    )

    captured_payload = {}

    def fake_post_json(endpoint, payload):
        captured_payload["endpoint"] = endpoint
        captured_payload["payload"] = payload

        return {
            "response": "Mexico opened the tournament with a strong win.",
        }

    monkeypatch.setattr(client, "_post_json", fake_post_json)

    result = client.generate_summary("Summarize Mexico vs South Africa.")

    assert captured_payload["endpoint"] == "/api/generate"
    assert captured_payload["payload"]["model"] == "llama3.2:1b"
    assert captured_payload["payload"]["stream"] is False
    assert result["provider"] == "local_llama"
    assert result["model"] == "llama3.2:1b"
    assert result["summary"] == "Mexico opened the tournament with a strong win."


def test_local_llama_client_handles_empty_llama_response(monkeypatch):
    client = LocalLlamaClient()

    def fake_post_json(endpoint, payload):
        return {
            "response": "",
        }

    monkeypatch.setattr(client, "_post_json", fake_post_json)

    with pytest.raises(RuntimeError, match="empty summary"):
        client.generate_summary("Summarize fixtures.")