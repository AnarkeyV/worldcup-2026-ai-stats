from pathlib import Path


STATIC_DIR = Path(__file__).resolve().parents[1] / "app" / "static"


def read_static_asset(name: str) -> str:
    return (STATIC_DIR / name).read_text(encoding="utf-8")


def test_official_watch_distinguishes_match_specific_video_from_coverage_hub():
    dashboard_js = read_static_asset("dashboard.js")

    assert "function formatOfficialWatchContentType(value, fallback = false)" in dashboard_js
    assert "Verified for this selected match" in dashboard_js
    assert "Official coverage hub — not match-specific" in dashboard_js
    assert "Not linked to this selected match" in dashboard_js


def test_official_watch_discloses_publication_and_verification_context():
    dashboard_js = read_static_asset("dashboard.js")

    assert "Publication time is not recorded in the verified local record." in dashboard_js
    assert "Published:" in dashboard_js
    assert "Source and match association checked:" in dashboard_js
    assert "function formatOfficialWatchTimestamp(value)" in dashboard_js


def test_official_watch_uses_clear_match_video_heading_and_styles():
    dashboard_js = read_static_asset("dashboard.js")
    dashboard_css = read_static_asset("dashboard.css")

    assert "Official Match Video" in dashboard_js
    assert ".official-watch-card.is-match-specific" in dashboard_css
    assert ".official-watch-record" in dashboard_css
