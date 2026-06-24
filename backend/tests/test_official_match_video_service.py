from types import SimpleNamespace

from app.services.official_match_video_service import build_official_watch


def make_video(**overrides):
    data = {
        "source_key": "fifa_web",
        "content_type": "highlights",
        "title": "Mexico vs South Africa | Highlights",
        "external_url": (
            "https://www.fifa.com/en/tournaments/mens/worldcup/"
            "canadamexicousa2026/highlights/mexico-south-africa"
        ),
        "territory": "global",
        "is_match_specific": True,
        "published_at": "2026-06-12T21:00:00+00:00",
        "verified_at": "2026-06-12T22:00:00+00:00",
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_official_watch_returns_delayed_state_and_official_hubs_without_links():
    watch = build_official_watch([])

    assert watch["state"] == "not_available_yet"
    assert watch["links"] == []
    assert watch["source_policy"] == "manual_verified_outbound_links_only"
    assert [link["source_key"] for link in watch["fallback_links"]] == [
        "fifa_highlights_hub",
        "mediacorp_mewatch_hub",
    ]
    assert all(link["external"] is True for link in watch["fallback_links"])
    assert all(link["link_target"] == "_blank" for link in watch["fallback_links"])
    assert all(link["link_rel"] == "noopener noreferrer" for link in watch["fallback_links"])


def test_official_watch_serializes_verified_fifa_link_as_safe_external_card():
    watch = build_official_watch([make_video()])

    assert watch["state"] == "available"
    assert watch["reason"] is None
    assert watch["links"] == [
        {
            "source_key": "fifa_web",
            "source_name": "FIFA",
            "title": "Mexico vs South Africa | Highlights",
            "content_type": "highlights",
            "url": (
                "https://www.fifa.com/en/tournaments/mens/worldcup/"
                "canadamexicousa2026/highlights/mexico-south-africa"
            ),
            "territory": "Global",
            "territory_note": "Availability may still vary by territory.",
            "is_match_specific": True,
            "published_at": "2026-06-12T21:00:00+00:00",
            "verified_at": "2026-06-12T22:00:00+00:00",
            "external": True,
            "link_target": "_blank",
            "link_rel": "noopener noreferrer",
        }
    ]


def test_official_watch_marks_mewatch_only_link_as_region_dependent():
    watch = build_official_watch(
        [
            make_video(
                source_key="mediacorp_mewatch",
                title="Mexico vs South Africa | Match Highlights",
                external_url="https://www.mewatch.sg/watch/Mexico-v-South-Africa-123456",
                territory="singapore",
            )
        ]
    )

    assert watch["state"] == "region_dependent"
    assert watch["links"][0]["source_name"] == "meWATCH"
    assert watch["links"][0]["territory"] == "Singapore"
    assert "Singapore availability" in watch["links"][0]["territory_note"]


def test_official_watch_rejects_unsafe_unverified_and_generic_youtube_records():
    unsafe_url = make_video(external_url="javascript:alert('not-a-link')")
    missing_verification = make_video(verified_at=None)
    generic_source = make_video(source_key="random_youtube")
    non_match_specific = make_video(is_match_specific=False)
    unsupported_youtube_path = make_video(
        source_key="fifa_youtube",
        external_url="https://www.youtube.com/@fan-upload-channel",
    )

    watch = build_official_watch(
        [
            unsafe_url,
            missing_verification,
            generic_source,
            non_match_specific,
            unsupported_youtube_path,
        ]
    )

    assert watch["state"] == "not_available_yet"
    assert watch["links"] == []


def test_official_watch_accepts_only_supported_fifa_youtube_video_urls():
    watch = build_official_watch(
        [
            make_video(
                source_key="fifa_youtube",
                title="Mexico vs South Africa | FIFA Highlights",
                external_url="https://www.youtube.com/watch?v=ABcd_123-xy",
            )
        ]
    )

    assert watch["state"] == "available"
    assert watch["links"][0]["source_key"] == "fifa_youtube"
    assert watch["links"][0]["source_name"] == "FIFA on YouTube"
    assert watch["links"][0]["url"] == "https://www.youtube.com/watch?v=ABcd_123-xy"
