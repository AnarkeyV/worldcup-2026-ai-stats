from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_dashboard_page_loads():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "World Cup 2026 AI Stats" in response.text
    assert "Interactive Dashboard" in response.text


def test_static_dashboard_css_loads():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "dashboard-layout" in response.text


def test_static_dashboard_js_loads():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "initializeDashboard" in response.text


def test_root_includes_dashboard_link():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["dashboard"] == "/dashboard"