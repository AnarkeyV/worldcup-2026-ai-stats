from pathlib import Path


STATIC_DIR = Path(__file__).resolve().parents[1] / "app" / "static"


def read_static_asset(name: str) -> str:
    return (STATIC_DIR / name).read_text(encoding="utf-8")


def test_group_stage_uses_native_disclosure_and_contains_group_content() -> None:
    dashboard_html = read_static_asset("dashboard.html")

    start = dashboard_html.index('<details\n            id="group-stage"')
    end = dashboard_html.index("</details>", start)
    disclosure = dashboard_html[start:end]

    assert 'data-dashboard-section' in disclosure
    assert "<summary>" in disclosure
    assert 'id="group-stage-message"' in disclosure
    assert 'id="group-standings"' in disclosure
    assert 'id="ai-insights"' in disclosure
    assert 'id="group-insights"' in disclosure


def test_group_navigation_targets_the_group_stage_disclosure() -> None:
    dashboard_html = read_static_asset("dashboard.html")

    expected = (
        'href="#group-stage" '
        'data-section-nav-link="group-stage">Groups</a>'
    )

    assert dashboard_html.count(expected) == 2


def test_more_menus_expose_controls_for_accessible_behavior() -> None:
    dashboard_html = read_static_asset("dashboard.html")

    assert 'aria-controls="dashboard-more-menu-links"' in dashboard_html
    assert 'id="dashboard-more-menu-links"' in dashboard_html
    assert 'aria-controls="mobile-more-menu-links"' in dashboard_html
    assert 'id="mobile-more-menu-links"' in dashboard_html


def test_group_stage_and_more_menu_runtime_contracts_are_present() -> None:
    dashboard_js = read_static_asset("dashboard.js")

    assert "function syncGroupStageDisclosure(fixtures)" in dashboard_js
    assert "getRecognizedKnockoutStages(fixtures)" in dashboard_js
    assert "function revealGroupStageForNavigation(event, sectionId)" in dashboard_js
    assert 'event.key !== "Escape"' in dashboard_js
    assert 'document.addEventListener("pointerdown"' in dashboard_js
    assert 'mobileViewport.addEventListener("change", closeForViewportChange)' in dashboard_js
    assert "function initializeMoreMenuBehavior()" in dashboard_js


def test_group_stage_and_desktop_more_menu_styles_are_present() -> None:
    dashboard_css = read_static_asset("dashboard.css")

    assert ".group-stage-disclosure" in dashboard_css
    assert ".group-stage-disclosure-content" in dashboard_css
    assert "#dashboard-section-nav .dashboard-section-nav-inner" in dashboard_css
    assert "overflow: visible;" in dashboard_css
    assert ".dashboard-more-menu[open]" in dashboard_css
