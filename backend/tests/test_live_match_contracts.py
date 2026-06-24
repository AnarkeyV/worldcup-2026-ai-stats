from datetime import datetime, timezone
from app.services.live_match_contracts import (
    COMPARISON_AVAILABLE,
    COMPARISON_BASELINE_UNAVAILABLE,
    EVENT_COMPARISON_AVAILABLE,
    EVENT_COMPARISON_BASELINE_UNAVAILABLE,
    EVENT_COMPARISON_COVERAGE_UNKNOWN,
    EVENT_COMPARISON_CURRENT_DETAIL_MISSING,
    EVENT_COMPARISON_NOT_PROVIDED,
    EVENT_COMPARISON_PREVIOUS_DETAIL_MISSING,
    MATCH_STATE_COMPLETED,
    MATCH_STATE_LIVE,
    MATCH_STATE_SCHEDULED,
    MATCH_STATE_UNAVAILABLE,
    build_fixture_change_summary,
    classify_stored_match_status,
    derive_fixture_display_state,
)


def _fixture(
    *,
    external_id: str = "fixture-001",
    status: str | None = "live",
    home_score: int | None = 0,
    away_score: int | None = 0,
) -> dict:
    return {
        "external_id": external_id,
        "status": status,
        "home_score": home_score,
        "away_score": away_score,
    }


def _detail(
    *,
    goals: list | None = None,
    cards: list | None = None,
    substitutions: list | None = None,
    event_coverage: dict | None = None,
) -> dict:
    return {
        "goals": goals if goals is not None else [],
        "cards": cards if cards is not None else [],
        "substitutions": substitutions if substitutions is not None else [],
        "event_coverage": event_coverage
        if event_coverage is not None
        else {
            "goals": "available",
            "cards": "available",
            "substitutions": "available",
        },
    }


def test_classify_stored_match_status_only_promotes_normalized_supported_states():
    assert classify_stored_match_status("live") == MATCH_STATE_LIVE
    assert classify_stored_match_status(" COMPLETE ") == MATCH_STATE_COMPLETED
    assert classify_stored_match_status("full_time") == MATCH_STATE_COMPLETED
    assert classify_stored_match_status("scheduled") == MATCH_STATE_SCHEDULED
    assert classify_stored_match_status("not_started") == MATCH_STATE_SCHEDULED


def test_classify_stored_match_status_keeps_missing_and_non_live_states_unavailable():
    assert classify_stored_match_status(None) == MATCH_STATE_UNAVAILABLE
    assert classify_stored_match_status("") == MATCH_STATE_UNAVAILABLE
    assert classify_stored_match_status("postponed") == MATCH_STATE_UNAVAILABLE
    assert classify_stored_match_status("cancelled") == MATCH_STATE_UNAVAILABLE
    assert classify_stored_match_status("abandoned") == MATCH_STATE_UNAVAILABLE
    assert classify_stored_match_status("provider-new-state") == MATCH_STATE_UNAVAILABLE


def test_first_observation_is_explicitly_not_a_change_claim():
    summary = build_fixture_change_summary(
        None,
        _fixture(status="complete", home_score=3, away_score=2),
        current_detail=_detail(
            goals=[{"minute": 82, "team": "home", "scorer": "Player A"}]
        ),
    )

    assert summary == {
        "external_id": "fixture-001",
        "comparison_status": COMPARISON_BASELINE_UNAVAILABLE,
        "event_comparison": {
            "goals": EVENT_COMPARISON_BASELINE_UNAVAILABLE,
            "cards": EVENT_COMPARISON_BASELINE_UNAVAILABLE,
            "substitutions": EVENT_COMPARISON_BASELINE_UNAVAILABLE,
        },
        "changes": [],
    }


def test_score_change_requires_two_complete_stored_score_pairs():
    summary = build_fixture_change_summary(
        _fixture(home_score=None, away_score=None),
        _fixture(home_score=0, away_score=0),
    )

    assert summary["comparison_status"] == COMPARISON_AVAILABLE
    assert summary["changes"] == []


def test_score_status_and_completion_changes_are_recorded_from_stored_values():
    summary = build_fixture_change_summary(
        _fixture(status="live", home_score=1, away_score=0),
        _fixture(status="complete", home_score=2, away_score=0),
    )

    assert summary["changes"] == [
        {
            "type": "score_changed",
            "before": {"home": 1, "away": 0},
            "after": {"home": 2, "away": 0},
        },
        {"type": "status_changed", "before": "live", "after": "complete"},
        {"type": "match_completed", "status": "complete"},
    ]


def test_canonical_goal_additions_are_provider_backed_and_deduplicated():
    previous_detail = _detail()
    current_detail = _detail(
        goals=[
            {"minute": "78", "team": "home", "scorer": "Player A"},
            {"minute": 78, "team": "HOME", "scorer": " player a "},
            {"minute": 80, "team": "away"},
        ]
    )

    summary = build_fixture_change_summary(
        _fixture(),
        _fixture(),
        previous_detail=previous_detail,
        current_detail=current_detail,
    )

    assert summary["event_comparison"]["goals"] == EVENT_COMPARISON_AVAILABLE
    assert summary["changes"] == [
        {
            "type": "goal_added",
            "event": {"minute": 78, "team": "home", "scorer": "Player A"},
        }
    ]


def test_card_and_substitution_additions_are_reported_separately():
    summary = build_fixture_change_summary(
        _fixture(),
        _fixture(),
        previous_detail=_detail(),
        current_detail=_detail(
            cards=[
                {
                    "minute": 59,
                    "team": "away",
                    "player": "Player B",
                    "color": "Yellow",
                }
            ],
            substitutions=[
                {
                    "minute": 61,
                    "team": "home",
                    "on": "Player C",
                    "off": "Player D",
                }
            ],
        ),
    )

    assert summary["changes"] == [
        {
            "type": "card_added",
            "event": {
                "minute": 59,
                "team": "away",
                "player": "Player B",
                "color": "yellow",
            },
        },
        {
            "type": "substitution_added",
            "event": {
                "minute": 61,
                "team": "home",
                "on": "Player C",
                "off": "Player D",
            },
        },
    ]


def test_event_removal_or_edit_is_neutral_provider_revision_not_new_event_claim():
    summary = build_fixture_change_summary(
        _fixture(),
        _fixture(),
        previous_detail=_detail(
            goals=[{"minute": 25, "team": "home", "scorer": "Player A"}]
        ),
        current_detail=_detail(
            goals=[{"minute": 25, "team": "home", "scorer": "Player E"}]
        ),
    )

    assert summary["changes"] == [
        {
            "type": "provider_event_record_revised",
            "event_type": "goals",
            "previous_count": 1,
            "current_count": 1,
        }
    ]


def test_missing_or_legacy_detail_data_remains_explicitly_unavailable():
    current_fixture = _fixture()

    previous_missing = build_fixture_change_summary(
        _fixture(),
        current_fixture,
        previous_detail=None,
        current_detail=_detail(),
    )
    current_missing = build_fixture_change_summary(
        _fixture(),
        current_fixture,
        previous_detail=_detail(),
        current_detail=None,
    )
    legacy = build_fixture_change_summary(
        _fixture(),
        current_fixture,
        previous_detail={"goals": []},
        current_detail={"goals": []},
    )

    assert previous_missing["event_comparison"]["goals"] == (
        EVENT_COMPARISON_PREVIOUS_DETAIL_MISSING
    )
    assert current_missing["event_comparison"]["cards"] == (
        EVENT_COMPARISON_CURRENT_DETAIL_MISSING
    )
    assert legacy["event_comparison"]["substitutions"] == (
        EVENT_COMPARISON_COVERAGE_UNKNOWN
    )
    assert all(not item["type"].endswith("_added") for item in legacy["changes"])


def test_provider_not_provided_event_category_is_not_interpreted_as_no_events():
    previous_detail = _detail(
        event_coverage={
            "goals": "available",
            "cards": "not_provided",
            "substitutions": "available",
        }
    )
    current_detail = _detail(
        cards=[
            {
                "minute": 41,
                "team": "home",
                "player": "Player A",
                "color": "yellow",
            }
        ],
        event_coverage={
            "goals": "available",
            "cards": "not_provided",
            "substitutions": "available",
        },
    )

    summary = build_fixture_change_summary(
        _fixture(),
        _fixture(),
        previous_detail=previous_detail,
        current_detail=current_detail,
    )

    assert summary["event_comparison"]["cards"] == EVENT_COMPARISON_NOT_PROVIDED
    assert summary["changes"] == []


def test_derive_fixture_display_state_preserves_explicit_stored_statuses():
    reference_time = datetime(2026, 6, 24, 12, tzinfo=timezone.utc)

    assert derive_fixture_display_state(
        "scheduled",
        "2026-06-24T10:00:00Z",
        None,
        None,
        now=reference_time,
    ) == {
        "match_state": MATCH_STATE_SCHEDULED,
        "state_source": "stored_status",
    }
    assert derive_fixture_display_state(
        "live",
        "2026-06-25T10:00:00Z",
        None,
        None,
        now=reference_time,
    ) == {
        "match_state": MATCH_STATE_LIVE,
        "state_source": "stored_status",
    }
    assert derive_fixture_display_state(
        "complete",
        "2026-06-23T10:00:00Z",
        2,
        1,
        now=reference_time,
    ) == {
        "match_state": MATCH_STATE_COMPLETED,
        "state_source": "stored_status",
    }


def test_derive_fixture_display_state_schedules_unknown_future_fixture_from_stored_kickoff():
    result = derive_fixture_display_state(
        "unknown",
        "2026-06-24T19:00:00.000Z",
        None,
        None,
        now=datetime(2026, 6, 24, 12, tzinfo=timezone.utc),
    )

    assert result == {
        "match_state": MATCH_STATE_SCHEDULED,
        "state_source": "stored_kickoff",
    }


def test_derive_fixture_display_state_never_uses_time_to_infer_live_status():
    result = derive_fixture_display_state(
        "unknown",
        "2026-06-24T12:00:00Z",
        None,
        None,
        now=datetime(2026, 6, 24, 12, tzinfo=timezone.utc),
    )

    assert result == {
        "match_state": MATCH_STATE_UNAVAILABLE,
        "state_source": "unavailable",
    }


def test_derive_fixture_display_state_keeps_unknown_without_a_usable_future_kickoff_unavailable():
    reference_time = datetime(2026, 6, 24, 12, tzinfo=timezone.utc)

    for kickoff_time in (None, "", "not-a-date", "2026-06-24T19:00:00"):
        assert derive_fixture_display_state(
            "unknown",
            kickoff_time,
            None,
            None,
            now=reference_time,
        ) == {
            "match_state": MATCH_STATE_UNAVAILABLE,
            "state_source": "unavailable",
        }


def test_derive_fixture_display_state_keeps_unknown_with_scores_or_non_unknown_status_unavailable():
    reference_time = datetime(2026, 6, 24, 12, tzinfo=timezone.utc)

    assert derive_fixture_display_state(
        "unknown",
        "2026-06-24T19:00:00Z",
        0,
        None,
        now=reference_time,
    ) == {
        "match_state": MATCH_STATE_UNAVAILABLE,
        "state_source": "unavailable",
    }
    assert derive_fixture_display_state(
        "postponed",
        "2026-06-24T19:00:00Z",
        None,
        None,
        now=reference_time,
    ) == {
        "match_state": MATCH_STATE_UNAVAILABLE,
        "state_source": "unavailable",
    }
