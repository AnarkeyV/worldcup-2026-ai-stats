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


def test_dashboard_page_includes_ai_health_status_elements():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="ai-health-badge"' in response.text
    assert 'id="ai-health-details"' in response.text
    assert "Checking AI..." in response.text
    assert "Local AI status will appear here" in response.text


def test_dashboard_page_includes_group_standings_section():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Group Standings" in response.text
    assert 'id="standings-message"' in response.text
    assert 'id="standings-container"' in response.text
    assert "Loading standings..." in response.text


def test_static_dashboard_css_loads():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "dashboard-layout" in response.text
    assert "ai-summary-panel" in response.text
    assert "ai-summary-output" in response.text
    assert "fixture-ai-summary" in response.text
    assert "fixture-ai-button" in response.text


def test_static_dashboard_css_includes_ai_health_badge_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "ai-health-badge" in response.text
    assert "ai-health-badge.checking" in response.text
    assert "ai-health-badge.available" in response.text
    assert "ai-health-badge.unavailable" in response.text


def test_static_dashboard_css_includes_standings_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "standings-section" in response.text
    assert "standings-container" in response.text
    assert "standings-table-wrapper" in response.text
    assert "standings-table" in response.text


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


def test_dashboard_js_includes_ai_health_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "checkAiHealth" in response.text
    assert "/ai/health" in response.text
    assert "setAiHealthChecking" in response.text
    assert "setAiHealthAvailable" in response.text
    assert "setAiHealthUnavailable" in response.text
    assert "AI Online" in response.text
    assert "AI Offline" in response.text


def test_dashboard_js_includes_standings_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "fetchStandings" in response.text
    assert "renderStandings" in response.text
    assert "buildStandingsQueryString" in response.text
    assert "/standings" in response.text
    assert "Group" in response.text
    assert "Pts" in response.text


def test_root_includes_dashboard_ai_summary_and_standings_links():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["dashboard"] == "/dashboard"
    assert response.json()["ai_summary"] == "/ai/fixtures/summary"
    assert response.json()["standings"] == "/standings"
