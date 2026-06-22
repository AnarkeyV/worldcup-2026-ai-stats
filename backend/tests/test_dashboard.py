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


def test_dashboard_page_includes_provider_sync_runtime_panel():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Provider Sync Runtime" in response.text
    assert "Runtime Observability" in response.text
    assert 'id="provider-sync-message"' in response.text
    assert 'id="sync-status-badge"' in response.text
    assert 'id="fixture-sync-status-container"' in response.text
    assert 'id="refresh-sync-status"' in response.text


def test_dashboard_page_includes_provider_sync_runtime_metric_elements():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="sync-provider"' in response.text
    assert 'id="sync-last-run"' in response.text
    assert 'id="sync-duration"' in response.text
    assert 'id="sync-total-fixtures"' in response.text
    assert 'id="sync-created"' in response.text
    assert 'id="sync-updated"' in response.text
    assert 'id="sync-newly-completed"' in response.text
    assert 'id="sync-last-success"' in response.text
    assert 'id="sync-error-message"' in response.text


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


def test_dashboard_page_includes_group_insights_section():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Group Insights" in response.text
    assert 'id="insights-message"' in response.text
    assert 'id="insights-container"' in response.text
    assert "Loading insights..." in response.text


def test_dashboard_page_includes_player_stats_section():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Player Statistics" in response.text
    assert 'id="player-stats-message"' in response.text
    assert 'id="player-stats-container"' in response.text
    assert "Preparing provider-backed player leaderboards" in response.text

def test_static_dashboard_css_loads():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "dashboard-layout" in response.text
    assert "ai-summary-panel" in response.text
    assert "ai-summary-output" in response.text
    assert "fixture-ai-summary" in response.text
    assert "fixture-ai-button" in response.text


def test_static_dashboard_css_includes_provider_sync_runtime_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "sync-runtime-panel" in response.text
    assert "sync-runtime-grid" in response.text
    assert "sync-runtime-card" in response.text
    assert "sync-status-badge" in response.text
    assert "sync-error-message" in response.text


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
    assert "group-standings-grid" in response.text
    assert "group-standings-card" in response.text
    assert "standings-compact-row" in response.text

def test_static_dashboard_css_includes_insight_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "insights-section" in response.text
    assert "insights-grid" in response.text
    assert "insight-card" in response.text
    assert "insight-label" in response.text


def test_static_dashboard_css_includes_player_stats_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "player-stats-section" in response.text
    assert "player-stats-grid" in response.text
    assert "player-stats-notice" in response.text

def test_static_dashboard_js_loads():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "initializeDashboard" in response.text
    assert "generateAiSummary" in response.text
    assert "generateSingleFixtureSummary" in response.text
    assert "/ai/fixtures/summary" in response.text
    assert "/ai/fixtures/${fixtureId}/summary" in response.text


def test_dashboard_js_includes_provider_sync_runtime_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "fetchFixtureSyncStatus" in response.text
    assert "refreshFixtureSyncStatus" in response.text
    assert "renderFixtureSyncStatus" in response.text
    assert "/fixtures/sync/status" in response.text
    assert "formatDurationSeconds" in response.text
    assert "getSyncStatusClass" in response.text


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
    assert "buildGroupOnlyQueryString" in response.text
    assert "/standings" in response.text
    assert "Group" in response.text
    assert "Pts" in response.text


def test_dashboard_js_includes_insights_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "fetchInsights" in response.text
    assert "renderInsights" in response.text
    assert "/insights/groups" in response.text
    assert "Group Leaders" in response.text
    assert "Strongest Attack" in response.text
    assert "Best Defence" in response.text
    assert "Unbeaten Teams" in response.text
    assert "Winless Teams" in response.text


def test_dashboard_js_hides_generic_sample_player_stats():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "renderPlayerStats" in response.text
    assert "Generic sample player records are intentionally hidden" in response.text
    assert "provider-backed match details" in response.text
    assert "Assist data is not present" in response.text

def test_root_includes_dashboard_ai_summary_standings_insights_and_player_stats_links():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["dashboard"] == "/dashboard"
    assert response.json()["ai_summary"] == "/ai/fixtures/summary"
    assert response.json()["standings"] == "/standings"
    assert response.json()["group_insights"] == "/insights/groups"
    assert response.json()["player_stats"] == "/players/stats"

def test_dashboard_page_includes_match_detail_panel():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Match Detail Dashboard" in response.text
    assert 'id="match-detail-panel"' in response.text
    assert 'id="match-detail-title"' in response.text
    assert 'id="match-detail-status"' in response.text
    assert 'id="selected-match-detail"' in response.text


def test_static_dashboard_css_includes_rich_match_detail_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "match-detail-panel" in response.text
    assert "match-detail-tabs" in response.text
    assert "match-timeline" in response.text
    assert "stat-comparison-row" in response.text
    assert "lineup-grid" in response.text

def test_dashboard_page_includes_fixture_group_tabs():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="fixture-group-tabs"' in response.text
    assert "Browse fixtures by group" in response.text
    assert "Provider-backed Rich Match Dashboard" in response.text
    assert "dashboard.js?v=1.11.0-ui2" in response.text
    assert "dashboard.css?v=1.11.0-ui2" in response.text

def test_dashboard_page_includes_fixture_status_browser_controls():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="fixture-status-tabs"' in response.text
    assert 'id="fixture-browser-message"' in response.text
    assert "Browse fixtures by status" in response.text
    assert "Completed" in response.text
    assert "Upcoming" in response.text
    assert "fixture-browser-layout" in response.text



def test_static_dashboard_css_includes_fixture_group_tab_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "fixture-group-tabs" in response.text
    assert "fixture-group-tab" in response.text
    assert "fixture-group-tab.is-active" in response.text


def test_dashboard_js_includes_rich_match_detail_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "data-fixture-card-id" in response.text
    assert "data-fixture-scope" in response.text
    assert "fixtureScope" in response.text
    assert "renderFixtureGroupTabs" in response.text
    assert "setFixtureScope" in response.text
    assert "Knockout" in response.text
    assert "fetchFixtureDetail" in response.text
    assert "/fixtures/${fixtureId}/detail" in response.text
    assert "renderMatchTimelineTab" in response.text
    assert "renderMatchStatsTab" in response.text
    assert "renderMatchLineupsTab" in response.text
    assert "match-detail-tab" in response.text


def test_static_dashboard_css_includes_status_first_fixture_browser_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "fixture-status-tabs" in response.text
    assert "fixture-status-tab" in response.text
    assert "fixture-browser-layout" in response.text
    assert "fixture-group-section" in response.text
    assert "fixture-card.is-selected" in response.text


def test_dashboard_js_includes_status_first_fixture_browser_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "fixtureStatusScope" in response.text
    assert "getFixtureStatusCategory" in response.text
    assert "renderFixtureStatusTabs" in response.text
    assert "setFixtureStatusScope" in response.text
    assert "ensureFixtureBrowserSelection" in response.text
    assert "renderFixtureBrowser" in response.text
    assert "fixture-group-section" in response.text
