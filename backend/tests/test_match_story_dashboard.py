
def test_dashboard_js_includes_read_only_match_story_and_official_watch_logic(client):
    response = client.get("/static/dashboard.js")

    assert response.status_code == 200
    assert "fetchFixtureStory" in response.text
    assert "/fixtures/${fixtureId}/story" in response.text
    assert "renderMatchStoryTab" in response.text
    assert "renderScoreProgression" in response.text
    assert "renderStoryEventTimeline" in response.text
    assert "renderStoryStatistics" in response.text
    assert "renderOfficialWatch" in response.text
    assert "Official Match Video" in response.text
    assert "No video is embedded, downloaded, or rehosted here." in response.text
    assert "target=\"_blank\"" in response.text
    assert "rel=\"noopener noreferrer\"" in response.text
    assert "Promise.allSettled" in response.text
    assert "Only values supplied for both teams are visualised." in response.text
    assert "Both teams recorded 0 for this provider metric." in response.text
    assert "<iframe" not in response.text


def test_dashboard_css_includes_mobile_first_match_story_and_official_watch_styles(client):
    response = client.get("/static/dashboard.css")

    assert response.status_code == 200
    assert "match-story-grid" in response.text
    assert "score-progression" in response.text
    assert "story-event-list" in response.text
    assert "story-stat-comparison-row" in response.text
    assert "official-watch" in response.text
    assert "official-watch-card" in response.text
    assert "official-watch-link" in response.text
    assert "story-provenance" in response.text
    assert "@media (max-width: 760px)" in response.text
