from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dashboard_page_includes_live_match_centre_panel_and_read_only_controls():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="live-match-centre"' in response.text
    assert "Live Match Centre" in response.text
    assert 'id="live-match-centre-message"' in response.text
    assert 'id="live-match-centre-freshness"' in response.text
    assert 'id="live-match-centre-matches"' in response.text
    assert 'id="refresh-live-match-centre"' in response.text
    assert "Refresh stored live state" in response.text
    assert "No provider request is made by this panel." in response.text
    assert "/static/live_match_centre.css?v=v1.22.1" in response.text
    assert "/static/live_match_centre.js?v=v1.22.1" in response.text


def test_live_match_centre_static_script_uses_only_read_only_endpoint_logic():
    response = client.get("/static/live_match_centre.js")

    assert response.status_code == 200
    assert "fetchLiveMatchCentre" in response.text
    assert "refreshLiveMatchCentre" in response.text
    assert "/live-match-centre" in response.text
    assert "What changed?" in response.text
    assert "not_recorded_before_v1_18" in response.text
    assert "No provider request is made by this panel." in response.text
    assert "Last confirmed live from stored snapshot" in response.text
    assert "Current live status is not inferred from kickoff time." in response.text
    assert "renderLiveMatch(match, freshness.state)" in response.text
    assert "/fixtures/sync/provider" not in response.text
    assert "method: \"POST\"" not in response.text


def test_live_match_centre_static_styles_load():
    response = client.get("/static/live_match_centre.css")

    assert response.status_code == 200
    assert "live-match-centre-panel" in response.text
    assert "live-match-card" in response.text
    assert "live-match-centre-changes" in response.text
    assert "live-match-centre-freshness" in response.text


def test_dashboard_browser_status_classifier_derives_future_unknown_statuses_from_stored_kickoff():
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "deriveFixtureDisplayState" in response.text
    assert "parseStoredUtcKickoff" in response.text
    assert 'stateSource: DISPLAY_STATE_SOURCE_STORED_KICKOFF' in response.text
    assert "Scheduled from stored kickoff" in response.text
    assert "Provider match status unavailable" in response.text
    assert 'matchState: "scheduled",' in response.text
    assert 'matchState: "unavailable",' in response.text
    assert 'status.includes("live")' not in response.text
    assert 'status.includes("in play")' not in response.text
    assert "live-match-centre:open-fixture" in response.text
