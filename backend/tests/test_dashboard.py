from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_dashboard_page_loads():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "World Cup 2026 AI Stats" in response.text
    assert "Interactive Dashboard" in response.text
    assert "AI Fixture Summary" in response.text
    assert "Generate AI Summary" in response.text
    assert "fixtures-container" in response.text


def test_dashboard_page_includes_ai_summary_panel_elements():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Local Llama Agent" in response.text
    assert 'id="ai-summary-message"' in response.text
    assert 'id="ai-summary-output"' in response.text
    assert 'id="generate-ai-summary"' in response.text


def test_static_dashboard_css_loads():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "dashboard-layout" in response.text
    assert "ai-summary-panel" in response.text
    assert "ai-summary-output" in response.text
    assert "fixture-ai-summary" in response.text
    assert "fixture-ai-button" in response.text


def test_static_dashboard_js_loads():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "initializeDashboard" in response.text
    assert "generateAiSummary" in response.text
    assert "generateSingleFixtureSummary" in response.text
    assert "/ai/fixtures/summary" in response.text
    assert "/ai/fixtures/${fixtureId}/summary" in response.text


def test_dashboard_js_includes_fixture_summary_button_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "Generate Match Summary" in response.text
    assert "data-fixture-summary-id" in response.text
    assert "fixtureSummaries" in response.text


def test_root_includes_dashboard_and_ai_summary_links():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["dashboard"] == "/dashboard"
    assert response.json()["ai_summary"] == "/ai/fixtures/summary"
