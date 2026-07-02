"""Static contracts for v1.23.0 Matchday Pulse progressive disclosure."""

from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = BACKEND_ROOT / "app" / "static"


def read_static_asset(name: str) -> str:
    return (STATIC_ROOT / name).read_text(encoding="utf-8")


def test_matchday_pulse_keeps_confirmed_state_and_local_change_context_visible() -> None:
    dashboard_html = read_static_asset("dashboard.html")

    assert "Matchday Pulse" in dashboard_html
    assert 'id="matchday-home-content"' in dashboard_html
    assert 'id="matchday-data-trust"' in dashboard_html
    assert 'id="data-health-badge"' in dashboard_html
    assert 'id="matchday-road-summary"' in dashboard_html
    assert 'id="matchday-pulse-changes-summary"' in dashboard_html
    assert 'data-progressive-disclosure-link="confirmed-knockout-path"' in dashboard_html
    assert 'data-progressive-disclosure-link="matchday-changes"' in dashboard_html


def test_long_dashboard_sections_use_native_collapsed_disclosures() -> None:
    dashboard_html = read_static_asset("dashboard.html")

    expected_ids = (
        "confirmed-knockout-path",
        "matchday-changes",
        "live-match-centre",
        "dashboard-overview",
        "sync-runtime",
        "ai-summary",
        "group-stage",
        "ai-insights",
        "group-race",
        "group-insights",
        "group-standings",
        "player-statistics",
        "match-data-quality",
        "fixtures",
    )

    for disclosure_id in expected_ids:
        marker = f'id="{disclosure_id}"'
        position = dashboard_html.index(marker)
        tag_start = dashboard_html.rfind("<details", 0, position)
        tag_end = dashboard_html.index(">", position)
        opening_tag = dashboard_html[tag_start:tag_end]

        assert tag_start != -1
        assert "data-progressive-disclosure" in opening_tag
        assert " open" not in opening_tag


def test_disclosure_headers_keep_factual_messages_available_while_collapsed() -> None:
    dashboard_html = read_static_asset("dashboard.html")

    for element_id in (
        "confirmed-knockout-path-summary",
        "matchday-changes-summary",
        "live-match-centre-summary",
        "provider-sync-message",
        "ai-summary-message",
        "group-stage-message",
        "ai-insights-message",
        "player-stats-message",
        "match-data-quality-message",
        "fixtures-summary",
    ):
        assert f'id="{element_id}"' in dashboard_html

    assert "No provider request is made by this panel." in dashboard_html
    assert "Progression is not inferred." in dashboard_html
    assert "Not a live feed." in dashboard_html


def test_progressive_disclosure_reuses_existing_stored_data_without_new_network_behavior() -> None:
    dashboard_js = read_static_asset("dashboard.js")

    assert "const V123_PROGRESSIVE_DISCLOSURE_IDS = Object.freeze([" in dashboard_js
    assert "function initializeV123ProgressiveDisclosure()" in dashboard_js
    assert "function revealV123DisclosureForNavigation(event, sectionId)" in dashboard_js
    assert "function v123GetRoadToFinalSummary(fixtures = state.allFixtures)" in dashboard_js
    assert "function v123GetChangesSummary(comparison = state.knockoutVisitComparison)" in dashboard_js
    assert "function v123SyncLiveMatchCentreSummary()" in dashboard_js
    assert "selectFixture = async function selectFixtureWithFocusedDisclosure" in dashboard_js
    assert "state.v123AutomaticFixtureSelection" in dashboard_js
    assert "/fixtures/sync/provider" not in dashboard_js
    assert 'method: "POST"' not in dashboard_js


def test_progressive_disclosure_styles_keep_touch_targets_focus_and_mobile_width_safe() -> None:
    dashboard_css = read_static_asset("dashboard.css")

    assert ".dashboard-disclosure" in dashboard_css
    assert ".dashboard-subdisclosure" in dashboard_css
    assert ".matchday-pulse-context" in dashboard_css
    assert "min-height: 44px;" in dashboard_css
    assert ".dashboard-disclosure > summary:focus-visible" in dashboard_css
    assert "@media (max-width: 700px)" in dashboard_css
    assert "grid-template-columns: minmax(0, 1fr);" in dashboard_css
