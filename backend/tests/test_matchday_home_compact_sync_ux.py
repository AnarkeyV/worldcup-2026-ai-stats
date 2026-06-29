# Static contracts for the v1.20.0 Matchday Home and compact Sync UX.

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = PROJECT_ROOT / "app" / "static"


def read_static_asset(filename: str) -> str:
    return (STATIC_ROOT / filename).read_text(encoding="utf-8")


def get_section(source: str, start_marker: str, end_marker: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)

    return source[start:end]


def test_matchday_home_compact_ux_markup_contract() -> None:
    dashboard_html = read_static_asset("dashboard.html")

    assert 'id="matchday-data-trust"' in dashboard_html
    assert 'aria-label="Matchday data trust"' in dashboard_html
    assert 'href="#sync-runtime"' in dashboard_html
    assert 'data-more-menu-toggle' in dashboard_html
    assert 'id="dashboard-more-menu"' in dashboard_html
    assert 'id="mobile-more-menu"' in dashboard_html
    assert ">More<" in dashboard_html


def test_matchday_home_reuses_factual_fixture_state_derivation() -> None:
    dashboard_js = read_static_asset("dashboard.js")

    hero_section = get_section(
        dashboard_js,
        "getMatchdayHeroFixtures = function getMatchdayHeroFixturesV120",
        "renderMatchdayScoreCard = function renderMatchdayScoreCardV120",
    )
    card_section = get_section(
        dashboard_js,
        "renderMatchdayScoreCard = function renderMatchdayScoreCardV120",
        "renderMatchdayHome = function renderMatchdayHomeV120",
    )

    assert 'getFixtureStatusCategory(fixture) === "live"' in hero_section
    assert 'getFixtureStatusCategory(fixture) === "completed"' in hero_section
    assert 'getFixtureStatusCategory(fixture) === "scheduled"' in hero_section
    assert 'String(fixture?.status || "").toLowerCase()' not in hero_section

    assert "const statusPresentation = getFixtureStatusPresentation(fixture);" in card_section
    assert "DISPLAY_STATE_SOURCE_STORED_KICKOFF" in card_section
    assert "Last recorded live" in card_section
    assert "Live in latest stored refresh" in card_section
    assert "Upcoming from stored kickoff" in card_section
    assert "Provider match status unavailable; shown from future stored kickoff." in card_section
    assert "snapshot is stale" in card_section


def test_compact_navigation_and_accessibility_styles_exist() -> None:
    dashboard_css = read_static_asset("dashboard.css")

    assert ".matchday-data-trust" in dashboard_css
    assert ".dashboard-more-menu" in dashboard_css
    assert ".mobile-more-menu" in dashboard_css
    assert ":focus-visible" in dashboard_css
    assert "min-height: 44px" in dashboard_css


def test_live_match_change_details_use_native_disclosure() -> None:
    live_match_centre_js = read_static_asset("live_match_centre.js")
    live_match_centre_css = read_static_asset("live_match_centre.css")

    assert "<details" in live_match_centre_js
    assert "<summary>" in live_match_centre_js
    assert "Show change details" in live_match_centre_js
    assert "live-match-centre-change-details" in live_match_centre_css
