from app.models.fixture_sync_change_set import FixtureSyncChangeSet
from app.models.match_detail_event_coverage import MatchDetailEventCoverage
from app.providers.zafronix import ZafronixProvider
from app.services.fixture_sync_service import sync_fixtures
from app.services.sync_observability_service import record_fixture_sync_status


def _fixture_payload(
    *,
    status: str = "live",
    home_score: int | None = 0,
    away_score: int | None = 0,
    match_detail: dict | None = None,
) -> dict:
    item = {
        "external_id": "live-change-001",
        "competition": "FIFA World Cup 2026",
        "stage": "Group Stage",
        "group_name": "Group A",
        "home_team": "Mexico",
        "away_team": "South Africa",
        "home_team_code": "MEX",
        "away_team_code": "RSA",
        "kickoff_time": "2026-06-11T19:00:00+00:00",
        "venue": "Mexico City Stadium",
        "status": status,
        "home_score": home_score,
        "away_score": away_score,
    }
    if match_detail is not None:
        item["match_detail"] = match_detail
    return item


def _detail(
    *,
    goals: list | None = None,
    cards: list | None = None,
    substitutions: list | None = None,
    coverage: dict | None = None,
) -> dict:
    return {
        "provider": "zafronix",
        "provider_match_id": "live-change-provider-001",
        "goals": goals if goals is not None else [],
        "cards": cards if cards is not None else [],
        "substitutions": substitutions if substitutions is not None else [],
        "event_coverage": coverage
        if coverage is not None
        else {
            "goals": "available",
            "cards": "available",
            "substitutions": "available",
        },
        "formations": {},
        "lineups": {},
        "statistics": {},
        "referee": {},
        "weather": {},
    }


def test_zafronix_marks_empty_lists_available_and_missing_categories_not_provided():
    provider = ZafronixProvider()

    detail = provider._normalize_match_detail(
        {
            "id": "coverage-001",
            "goals": [],
            "cards": None,
        }
    )

    assert detail["event_coverage"] == {
        "goals": "available",
        "cards": "not_provided",
        "substitutions": "not_provided",
    }


def test_sync_persists_event_coverage_and_factual_changes_for_existing_fixture(
    db_session,
):
    initial = sync_fixtures(
        db_session,
        [_fixture_payload(match_detail=_detail())],
    )

    assert initial["created"] == 1
    assert initial["compared_fixture_count"] == 0
    assert initial["change_summaries"] == []

    coverage = db_session.query(MatchDetailEventCoverage).one()
    assert coverage.provider == "zafronix"
    assert coverage.event_coverage == {
        "goals": "available",
        "cards": "available",
        "substitutions": "available",
    }

    updated = sync_fixtures(
        db_session,
        [
            _fixture_payload(
                home_score=1,
                away_score=0,
                match_detail=_detail(
                    goals=[
                        {
                            "minute": 22,
                            "team": "home",
                            "scorer": "Player A",
                        }
                    ],
                    cards=[
                        {
                            "minute": 31,
                            "team": "away",
                            "player": "Player B",
                            "color": "yellow",
                        }
                    ],
                    substitutions=[
                        {
                            "minute": 56,
                            "team": "home",
                            "on": "Player C",
                            "off": "Player D",
                        }
                    ],
                ),
            )
        ],
    )

    assert updated["created"] == 0
    assert updated["updated"] == 1
    assert updated["compared_fixture_count"] == 1
    assert updated["change_summaries"] == [
        {
            "external_id": "live-change-001",
            "comparison_status": "available",
            "event_comparison": {
                "goals": "available",
                "cards": "available",
                "substitutions": "available",
            },
            "changes": [
                {
                    "type": "score_changed",
                    "before": {"home": 0, "away": 0},
                    "after": {"home": 1, "away": 0},
                },
                {
                    "type": "goal_added",
                    "event": {
                        "minute": 22,
                        "team": "home",
                        "scorer": "Player A",
                    },
                },
                {
                    "type": "card_added",
                    "event": {
                        "minute": 31,
                        "team": "away",
                        "player": "Player B",
                        "color": "yellow",
                    },
                },
                {
                    "type": "substitution_added",
                    "event": {
                        "minute": 56,
                        "team": "home",
                        "on": "Player C",
                        "off": "Player D",
                    },
                },
            ],
        }
    ]


def test_sync_does_not_claim_event_changes_when_provider_does_not_supply_category(
    db_session,
):
    sync_fixtures(
        db_session,
        [_fixture_payload(match_detail=_detail())],
    )

    result = sync_fixtures(
        db_session,
        [
            _fixture_payload(
                match_detail=_detail(
                    cards=[
                        {
                            "minute": 38,
                            "team": "away",
                            "player": "Player B",
                            "color": "yellow",
                        }
                    ],
                    coverage={
                        "goals": "available",
                        "cards": "not_provided",
                        "substitutions": "available",
                    },
                )
            )
        ],
    )

    assert result["compared_fixture_count"] == 1
    assert result["change_summaries"] == []


def test_successful_sync_audit_gets_one_companion_change_set(db_session):
    sync_fixtures(db_session, [_fixture_payload(match_detail=_detail())])
    result = sync_fixtures(
        db_session,
        [
            _fixture_payload(
                home_score=1,
                away_score=0,
                match_detail=_detail(
                    goals=[
                        {
                            "minute": 17,
                            "team": "home",
                            "scorer": "Player A",
                        }
                    ]
                ),
            )
        ],
    )

    recorded_run = record_fixture_sync_status(
        db=db_session,
        source="provider",
        provider="zafronix",
        status="success",
        result=result,
        duration_seconds=0.1,
        trigger_type="manual",
        started_at="2026-06-11T19:00:00+00:00",
    )

    change_set = db_session.query(FixtureSyncChangeSet).one()
    assert change_set.sync_run_id == recorded_run["id"]
    assert change_set.capture_state == "recorded"
    assert change_set.compared_fixture_count == 1
    assert change_set.changed_fixture_count == 1
    assert change_set.total_change_count == 2
    assert change_set.changes[0]["external_id"] == "live-change-001"
    assert [change["type"] for change in change_set.changes[0]["changes"]] == [
        "score_changed",
        "goal_added",
    ]


def test_failed_sync_audit_does_not_create_a_change_set(db_session):
    record_fixture_sync_status(
        db=db_session,
        source="provider",
        provider="zafronix",
        status="error",
        result={"total_fixtures": 0},
        duration_seconds=0.1,
        error="provider unavailable",
        trigger_type="scheduled",
        started_at="2026-06-11T19:00:00+00:00",
    )

    assert db_session.query(FixtureSyncChangeSet).count() == 0
