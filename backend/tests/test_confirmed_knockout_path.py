# Static contracts for the v1.22.0 confirmed knockout path checkpoint.
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_HTML = (BACKEND_ROOT / "app/static/dashboard.html").read_text(encoding="utf-8")
DASHBOARD_JS = (BACKEND_ROOT / "app/static/dashboard.js").read_text(encoding="utf-8")
DASHBOARD_CSS = (BACKEND_ROOT / "app/static/dashboard.css").read_text(encoding="utf-8")


def test_confirmed_knockout_path_is_semantic_and_has_no_future_placeholders():
    assert 'id="confirmed-knockout-path"' in DASHBOARD_HTML
    assert 'id="confirmed-knockout-stage-tabs"' in DASHBOARD_HTML
    assert 'id="confirmed-knockout-stage-content"' in DASHBOARD_HTML
    assert "Later stages appear only when stored. Progression is not inferred." in DASHBOARD_HTML
    assert "Later stages are intentionally not shown until stored provider-backed fixtures exist." in DASHBOARD_JS


def test_matchday_changes_is_browser_local_and_not_live():
    assert 'id="matchday-changes"' in DASHBOARD_HTML
    assert "Compares stored knockout data saved by this browser. Not a live feed." in DASHBOARD_HTML
    assert 'const CONFIRMED_KNOCKOUT_STORAGE_KEY = "wc2026.confirmed-knockout-path.v1";' in DASHBOARD_JS
    assert "window.localStorage" in DASHBOARD_JS
    assert "First visit on this browser" in DASHBOARD_JS
    assert "No stored knockout changes since your last visit" in DASHBOARD_JS
    assert "Local comparison unavailable" in DASHBOARD_JS


def test_confirmed_path_reuses_existing_stages_status_and_selection():
    assert "return safeFixtures.filter((fixture) => Boolean(getRecognizedKnockoutStage(fixture)));" in DASHBOARD_JS
    assert "getFixtureStatusPresentation(fixture)" in DASHBOARD_JS
    assert "function compareConfirmedKnockoutSnapshots" in DASHBOARD_JS
    assert 'type: "new_fixture"' in DASHBOARD_JS
    assert 'type: "newly_completed"' in DASHBOARD_JS
    assert 'type: "score_or_status_changed"' in DASHBOARD_JS
    assert "selectFixture(fixture.id, { scroll: true });" in DASHBOARD_JS


def test_checkpoint_keeps_mobile_targets_and_focus_styles():
    assert ".confirmed-knockout-stage-tabs" in DASHBOARD_CSS
    assert ".confirmed-knockout-fixture-grid" in DASHBOARD_CSS
    assert "min-height: 44px;" in DASHBOARD_CSS
    assert ".confirmed-knockout-stage-button:focus-visible" in DASHBOARD_CSS


def test_active_v121_matchday_renderer_invokes_checkpoint_features():
    active_renderer = (
        "renderMatchdayHome = function renderMatchdayHomeV121(fixtures = state.matchdayFixtures) {\n"
        "    renderConfirmedKnockoutPath(state.allFixtures);\n"
        "    renderMatchdayChanges(state.allFixtures);"
    )
    assert active_renderer in DASHBOARD_JS
    assert (
        "function renderMatchdayHome(fixtures = state.matchdayFixtures) {\n"
        "    renderConfirmedKnockoutPath(state.allFixtures);"
    ) not in DASHBOARD_JS


def test_confirmed_path_reuses_the_existing_status_presentation_verbatim():
    assert 'const status = statusPresentation?.label || "Stored status unavailable";' in DASHBOARD_JS
    assert 'Provider status live' not in DASHBOARD_JS


def test_confirmed_path_uses_the_existing_canonical_stage_resolver():
    assert "return safeFixtures.filter((fixture) => Boolean(getRecognizedKnockoutStage(fixture)));" in DASHBOARD_JS
    assert 'stage: getRecognizedKnockoutStage(fixture) || "",' in DASHBOARD_JS
    assert "getRecognizedKnockoutStage(fixture) === state.confirmedKnockoutStage" in DASHBOARD_JS
    assert "getFixtureScopeFromKnockoutStage(knockoutStage)" in DASHBOARD_JS


def test_completion_comparison_uses_existing_completed_status_catalogue():
    assert "COMPLETED_FIXTURE_STATUSES.has(normalizeFixtureStatus(fixture))" in DASHBOARD_JS
