from app.config import settings


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "backend"
    assert response.json()["version"] == settings.app_version
