"""Static contracts for the v1.21.0 knockout-stage Matchday UX."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_JS = PROJECT_ROOT / "app" / "static" / "dashboard.js"


def read_dashboard_js() -> str:
    return DASHBOARD_JS.read_text(encoding="utf-8")


def test_knockout_stage_resolver_accepts_only_known_provider_stage_labels() -> None:
    dashboard_js = read_dashboard_js()

    assert "const RECOGNIZED_KNOCKOUT_STAGES = Object.freeze([" in dashboard_js
    for stage in (
        "Round of 32",
        "Round of 16",
        "Quarter-finals",
        "Semi-finals",
        "Third-place Playoff",
        "Final",
    ):
        assert f'"{stage}"' in dashboard_js

    assert "function getRecognizedKnockoutStage(fixture)" in dashboard_js
    assert "return Boolean(getRecognizedKnockoutStage(fixture));" in dashboard_js
    assert '!stage.includes("group")' not in dashboard_js


def test_fixture_browser_supports_stage_specific_knockout_scopes() -> None:
    dashboard_js = read_dashboard_js()

    assert 'const KNOCKOUT_STAGE_SCOPE_PREFIX = "knockout-stage:";' in dashboard_js
    assert "function getFixtureScopeFromKnockoutStage(stage)" in dashboard_js
    assert "function getKnockoutStageFromScope(scope)" in dashboard_js
    assert "const availableKnockoutStages = getRecognizedKnockoutStages(statusFixtures);" in dashboard_js
    assert "scope: getFixtureScopeFromKnockoutStage(stage)," in dashboard_js
    assert 'label: "All fixtures",' in dashboard_js


def test_matchday_uses_recognized_knockout_fixtures_before_group_fixtures() -> None:
    dashboard_js = read_dashboard_js()

    assert "getMatchdayHeroFixtures = function getMatchdayHeroFixturesV121" in dashboard_js
    assert "const knockoutFixtures = safeFixtures.filter(isKnockoutFixture);" in dashboard_js
    assert "const preferredFixtures = knockoutFixtures.length > 0 ? knockoutFixtures : safeFixtures;" in dashboard_js
    assert "knockoutFocused: knockoutFixtures.length > 0," in dashboard_js
    assert '"Next confirmed knockout match"' in dashboard_js
    assert '"Latest knockout result"' in dashboard_js
    assert "const knockoutContext = heroes.knockoutFocused" in dashboard_js
