from types import SimpleNamespace

from app.services.match_story_service import build_match_story


def make_fixture(**overrides):
    data = {
        "id": 7,
        "home_team": "Mexico",
        "away_team": "South Africa",
        "home_score": 2,
        "away_score": 1,
        "status": "complete",
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_detail(**overrides):
    data = {
        "provider": "zafronix",
        "provider_match_id": "2026-001",
        "updated_at": "2026-06-24T01:45:00+00:00",
        "goals": [
            {"minute": 9, "team": "home", "scorer": "Quiñones"},
            {"minute": "45+2", "team": "away", "scorer": "Mokwana"},
            {"minute": 67, "team": "home", "scorer": "Jiménez"},
        ],
        "cards": [
            {
                "minute": 49,
                "team": "away",
                "player": "Sphephelo Sithole",
                "color": "red",
            }
        ],
        "substitutions": [
            {
                "minute": 66,
                "team": "home",
                "on": "Gilberto Mora",
                "off": "Álvaro Fidalgo",
            }
        ],
        "statistics": {
            "home": {
                "possessionPct": 61,
                "shotsTotal": 16,
                "shotsOnGoal": 6,
                "expectedGoals": 1.41,
                "corners": 4,
            },
            "away": {
                "possessionPct": 39,
                "shotsTotal": 3,
                "shotsOnGoal": 1,
                "expectedGoals": 0.07,
                "corners": 0,
            },
        },
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_build_match_story_creates_score_progression_timeline_and_statistics():
    story = build_match_story(make_fixture(), make_detail())

    assert story["state"] == "available"
    assert story["source"] == {
        "mode": "stored_provider_match_detail",
        "detail_available": True,
        "provider": "zafronix",
        "provider_match_id": "2026-001",
        "stored_detail_updated_at": "2026-06-24T01:45:00+00:00",
    }
    assert story["score_progression"] == {
        "state": "available",
        "reason": None,
        "events": [
            {
                "minute": 9,
                "team": "home",
                "scorer": "Quiñones",
                "home_score": 1,
                "away_score": 0,
            },
            {
                "minute": "45+2",
                "team": "away",
                "scorer": "Mokwana",
                "home_score": 1,
                "away_score": 1,
            },
            {
                "minute": 67,
                "team": "home",
                "scorer": "Jiménez",
                "home_score": 2,
                "away_score": 1,
            },
        ],
    }
    assert [event["kind"] for event in story["timeline"]["events"]] == [
        "goal",
        "goal",
        "card",
        "substitution",
        "goal",
    ]
    assert story["statistics"] == {
        "state": "available",
        "reason": None,
        "metrics": [
            {
                "key": "possessionPct",
                "label": "Possession",
                "unit": "percent",
                "home": 61,
                "away": 39,
            },
            {
                "key": "shotsTotal",
                "label": "Shots",
                "unit": "count",
                "home": 16,
                "away": 3,
            },
            {
                "key": "shotsOnGoal",
                "label": "Shots on target",
                "unit": "count",
                "home": 6,
                "away": 1,
            },
            {
                "key": "expectedGoals",
                "label": "Expected goals",
                "unit": "decimal",
                "home": 1.41,
                "away": 0.07,
            },
            {
                "key": "corners",
                "label": "Corners",
                "unit": "count",
                "home": 4,
                "away": 0,
            },
        ],
        "incomplete_metric_keys": [],
    }


def test_build_match_story_keeps_timeline_but_rejects_unreconciled_score_progression():
    detail = make_detail(
        goals=[{"minute": 9, "team": "home", "scorer": "Quiñones"}],
    )

    story = build_match_story(make_fixture(home_score=2, away_score=0), detail)

    assert story["state"] == "partial"
    assert story["score_progression"] == {
        "state": "unavailable",
        "reason": "Stored goal events do not reconcile with the fixture score.",
        "events": [],
    }
    assert story["timeline"]["state"] == "available"
    assert story["timeline"]["events"] == [
        {
            "kind": "goal",
            "minute": 9,
            "team": "home",
            "scorer": "Quiñones",
        },
        {
            "kind": "card",
            "minute": 49,
            "team": "away",
            "player": "Sphephelo Sithole",
            "color": "red",
        },
        {
            "kind": "substitution",
            "minute": 66,
            "team": "home",
            "player_on": "Gilberto Mora",
            "player_off": "Álvaro Fidalgo",
        },
    ]


def test_build_match_story_keeps_unknown_minute_events_in_timeline_only():
    detail = make_detail(
        goals=[{"minute": None, "team": "home", "scorer": "Quiñones"}],
        cards=[],
        substitutions=[],
        statistics={"home": {}, "away": {}},
    )

    story = build_match_story(make_fixture(home_score=1, away_score=0), detail)

    assert story["state"] == "partial"
    assert story["score_progression"] == {
        "state": "unavailable",
        "reason": "At least one stored goal is missing a usable minute.",
        "events": [],
    }
    assert story["timeline"] == {
        "state": "available",
        "reason": None,
        "events": [
            {
                "kind": "goal",
                "minute": None,
                "team": "home",
                "scorer": "Quiñones",
            }
        ],
    }
    assert story["statistics"]["state"] == "unavailable"


def test_build_match_story_only_returns_valid_paired_statistics():
    detail = make_detail(
        goals=[],
        cards=[],
        substitutions=[],
        statistics={
            "home": {
                "possessionPct": "61",
                "shotsTotal": 16,
                "corners": 0,
                "fouls": "not-supplied",
            },
            "away": {
                "possessionPct": "39",
                "corners": 0,
                "fouls": 7,
            },
        },
    )

    story = build_match_story(make_fixture(home_score=0, away_score=0), detail)

    assert story["state"] == "partial"
    assert story["statistics"] == {
        "state": "partial",
        "reason": "Only statistics supplied for both teams are shown.",
        "metrics": [
            {
                "key": "possessionPct",
                "label": "Possession",
                "unit": "percent",
                "home": 61,
                "away": 39,
            },
            {
                "key": "corners",
                "label": "Corners",
                "unit": "count",
                "home": 0,
                "away": 0,
            },
        ],
        "incomplete_metric_keys": ["shotsTotal", "fouls"],
    }


def test_build_match_story_returns_unavailable_sections_without_stored_detail():
    story = build_match_story(make_fixture(), None)

    assert story == {
        "state": "unavailable",
        "source": {
            "mode": "stored_provider_match_detail",
            "detail_available": False,
            "provider": None,
            "provider_match_id": None,
            "stored_detail_updated_at": None,
        },
        "score_progression": {
            "state": "unavailable",
            "reason": "No stored provider match detail is available for this fixture.",
            "events": [],
        },
        "timeline": {
            "state": "unavailable",
            "reason": "No stored provider event timeline is available for this fixture.",
            "events": [],
        },
        "statistics": {
            "state": "unavailable",
            "reason": "No stored provider match statistics are available for this fixture.",
            "metrics": [],
            "incomplete_metric_keys": [],
        },
    }
