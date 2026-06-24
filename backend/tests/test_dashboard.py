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


def test_dashboard_page_includes_provider_player_leaders_section():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Player Leaders" in response.text
    assert "Provider-backed match detail" in response.text
    assert 'id="player-stats-message"' in response.text
    assert 'id="player-stats-container"' in response.text
    assert "Loading provider-backed scorer and card leaderboards" in response.text

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


def test_static_dashboard_css_includes_provider_player_leader_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "player-stats-section" in response.text
    assert "player-stats-grid" in response.text
    assert "provider-coverage-card" in response.text
    assert "player-leaderboard-card" in response.text
    assert "player-leader-list" in response.text
    assert "assist-availability-note" in response.text

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


def test_dashboard_js_uses_provider_backed_player_leaders():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "fetchProviderLeaders" in response.text
    assert "refreshProviderLeaders" in response.text
    assert "renderProviderLeaders" in response.text
    assert "/players/leaders" in response.text
    assert "assist_data" in response.text
    assert "Generic sample player records are intentionally hidden" not in response.text

def test_dashboard_page_includes_latest_completed_match_summary():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="latest-completed-summary"' in response.text
    assert "Latest provider-backed completed match" in response.text
    assert "Loading the latest provider-backed completed match" in response.text


def test_dashboard_js_includes_latest_completed_match_summary_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "fetchLatestCompletedSummary" in response.text
    assert "refreshLatestCompletedSummary" in response.text
    assert "renderLatestCompletedSummary" in response.text
    assert "/ai/latest-completed/summary" in response.text
    assert "Major incidents" in response.text


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
    assert "dashboard.js?v=v1.18.0" in response.text
    assert "dashboard.css?v=v1.18.0" in response.text

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


def test_dashboard_page_includes_persistent_quick_navigation():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="dashboard-section-nav"' in response.text
    assert "Quick dashboard navigation" in response.text
    assert 'data-section-nav-link="dashboard-overview"' in response.text
    assert 'href="#fixtures"' in response.text
    assert 'id="group-standings"' in response.text
    assert 'id="fixtures"' in response.text


def test_static_dashboard_css_includes_persistent_quick_navigation_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "dashboard-section-nav" in response.text
    assert "dashboard-section-nav-link" in response.text
    assert "position: sticky" in response.text
    assert "scroll-margin-top" in response.text


def test_dashboard_js_includes_section_navigation_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "initializeSectionNavigation" in response.text
    assert "setActiveSectionNavLink" in response.text
    assert "IntersectionObserver" in response.text
    assert "data-section-nav-link" in response.text


def test_dashboard_page_includes_group_race_board():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Group Race" in response.text
    assert "Top two teams in each group" in response.text
    assert 'id="group-race-message"' in response.text
    assert 'id="group-race-container"' in response.text


def test_static_dashboard_css_includes_group_race_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "group-race-board" in response.text
    assert "group-race-grid" in response.text
    assert "group-race-card" in response.text
    assert "group-race-row" in response.text


def test_dashboard_js_includes_group_race_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "renderGroupRace" in response.text
    assert "group_race" in response.text
    assert "Top-two group positions" in response.text
    assert "fetchAiInsights(state.filters)" in response.text


def test_dashboard_page_includes_sync_freshness_and_safety_elements():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="sync-freshness-badge"' in response.text
    assert 'id="sync-data-freshness"' in response.text
    assert 'id="sync-data-age"' in response.text
    assert 'id="sync-scheduler-mode"' in response.text
    assert 'id="sync-alert-policy"' in response.text
    assert "Completed-match Telegram alerts are off by default." in response.text


def test_static_dashboard_css_includes_sync_freshness_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "sync-freshness-badge" in response.text
    assert "sync-freshness-badge.fresh" in response.text
    assert "sync-freshness-badge.aging" in response.text
    assert "sync-freshness-badge.stale" in response.text
    assert "sync-freshness-badge.last-sync-failed" in response.text


def test_dashboard_js_includes_sync_freshness_and_stored_detail_refresh_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "formatSyncFreshness" in response.text
    assert "formatDataAgeSeconds" in response.text
    assert "formatSchedulerMode" in response.text
    assert "last_sync_failed" in response.text
    assert "formatStoredDetailRefresh" in response.text
    assert "Stored detail refresh" in response.text
    assert "Stored provider payload; not a live detail request." in response.text

def test_dashboard_page_includes_match_data_quality_panel():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="match-data-quality"' in response.text
    assert "Match Data Coverage" in response.text
    assert "Read-only stored data" in response.text
    assert 'id="match-data-quality-message"' in response.text
    assert 'id="refresh-match-data-quality"' in response.text
    assert 'id="match-data-quality-summary"' in response.text
    assert 'id="match-data-quality-events"' in response.text
    assert 'id="missing-detail-fixtures"' in response.text
    assert 'href="#match-data-quality"' in response.text


def test_dashboard_js_includes_match_data_quality_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "fetchMatchDataQuality" in response.text
    assert "refreshMatchDataQuality" in response.text
    assert "renderMatchDataQuality" in response.text
    assert "/fixtures/data-quality" in response.text
    assert "missing_detail_fixtures" in response.text
    assert "data-missing-detail-fixture-id" in response.text
    assert "Stored match-detail coverage" in response.text
    assert "No provider request was made by this panel." in response.text


def test_static_dashboard_css_includes_match_data_quality_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "match-data-quality-panel" in response.text
    assert "match-data-quality-grid" in response.text
    assert "match-data-quality-card" in response.text
    assert "match-data-quality-event-card" in response.text
    assert "missing-detail-fixtures" in response.text
    assert "missing-detail-fixture-button" in response.text
def test_dashboard_page_includes_visual_matchday_home_and_mobile_navigation():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="matchday-home"' in response.text
    assert "Matchday" in response.text
    assert 'id="matchday-home-content"' in response.text
    assert 'id="data-health-badge"' in response.text
    assert 'id="mobile-bottom-nav"' in response.text
    assert 'data-section-nav-link="matchday-home"' in response.text


def test_dashboard_js_includes_visual_matchday_and_chart_rendering_logic():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "renderMatchdayHome" in response.text
    assert "getMatchdayHeroFixtures" in response.text
    assert "data-matchday-fixture-id" in response.text
    assert "dataHealthBadge" in response.text
    assert "player-leader-bar-fill" in response.text
    assert "group-race-points-fill" in response.text
    assert "match-data-quality-donut" in response.text
    assert "mobile-bottom-nav" in response.text


def test_static_dashboard_css_includes_visual_matchday_and_chart_styles():
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "matchday-home-panel" in response.text
    assert "matchday-hero-grid" in response.text
    assert "matchday-score-card" in response.text
    assert "player-leader-bar-fill" in response.text
    assert "group-race-points-track" in response.text
    assert "match-data-quality-donut" in response.text
    assert "mobile-bottom-nav" in response.text


def test_dashboard_page_keeps_read_only_data_coverage_in_visual_home():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Data health" in response.text
    assert "Stored match data" in response.text
    assert "No provider request was made by this panel." in response.text


def test_dashboard_js_includes_stored_kickoff_schedule_derivation():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "deriveFixtureDisplayState" in response.text
    assert "parseStoredUtcKickoff" in response.text
    assert 'stateSource: DISPLAY_STATE_SOURCE_STORED_KICKOFF' in response.text
    assert "Scheduled from stored kickoff" in response.text
    assert "Provider match status unavailable" in response.text
    assert 'status !== "unknown"' in response.text
    assert 'matchState: "scheduled",' in response.text
    assert 'matchState: "unavailable",' in response.text
