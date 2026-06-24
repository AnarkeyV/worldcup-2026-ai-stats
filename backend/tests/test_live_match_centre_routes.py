from datetime import datetime, timezone

from app.models.fixture import Fixture
from app.models.fixture_sync_change_set import FixtureSyncChangeSet
from app.models.fixture_sync_run import FixtureSyncRun
from app.models.match_detail import MatchDetail
from app.models.match_detail_event_coverage import MatchDetailEventCoverage


def _fixture(
    *,
    external_id: str,
    status: str = "live",
    home_score: int | None = 0,
    away_score: int | None = 0,
    kickoff_time: str = "2026-06-11T19:00:00+00:00",
    updated_at: str = "2026-06-24T10:00:00+00:00",
) -> Fixture:
    return Fixture(
        external_id=external_id,
        competition="FIFA World Cup 2026",
        stage="Group Stage",
        group_name="Group A",
        home_team="Mexico",
        away_team="South Africa",
        home_team_code="MEX",
        away_team_code="RSA",
        kickoff_time=kickoff_time,
        venue="Mexico City Stadium",
        status=status,
        home_score=home_score,
        away_score=away_score,
        created_at="2026-06-24T09:00:00+00:00",
        updated_at=updated_at,
    )


def _success_run(
    *,
    completed_at: str = "2026-06-24T10:00:00+00:00",
) -> FixtureSyncRun:
    return FixtureSyncRun(
        source="provider",
        provider="zafronix",
        trigger_type="manual",
        status="success",
        started_at="2026-06-24T09:59:30+00:00",
        completed_at=completed_at,
        duration_seconds=0.5,
        total_fixtures=1,
        created=0,
        updated=1,
        newly_completed_count=0,
        newly_completed=[],
        last_error=None,
    )


def _failed_run() -> FixtureSyncRun:
    return FixtureSyncRun(
        source="provider",
        provider="zafronix",
        trigger_type="manual",
        status="error",
        started_at="2026-06-24T10:01:00+00:00",
        completed_at="2026-06-24T10:01:10+00:00",
        duration_seconds=0.2,
        total_fixtures=0,
        created=0,
        updated=0,
        newly_completed_count=0,
        newly_completed=[],
        last_error="provider unavailable",
    )


def _recorded_change_set(sync_run_id: int) -> FixtureSyncChangeSet:
    return FixtureSyncChangeSet(
        sync_run_id=sync_run_id,
        capture_state="recorded",
        compared_fixture_count=1,
        changed_fixture_count=1,
        total_change_count=2,
        changes=[
            {
                "external_id": "live-centre-001",
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
                ],
            }
        ],
        created_at="2026-06-24T10:00:01+00:00",
    )


def test_live_match_centre_returns_only_explicitly_live_stored_fixtures(
    client,
    db_session,
):
    live_fixture = _fixture(external_id="live-centre-001", home_score=1)
    completed_fixture = _fixture(
        external_id="completed-centre-001",
        status="complete",
        home_score=2,
        away_score=0,
    )
    scheduled_fixture = _fixture(
        external_id="scheduled-centre-001",
        status="scheduled",
        home_score=None,
        away_score=None,
    )
    unavailable_fixture = _fixture(
        external_id="postponed-centre-001",
        status="postponed",
        home_score=None,
        away_score=None,
    )
    db_session.add_all(
        [live_fixture, completed_fixture, scheduled_fixture, unavailable_fixture]
    )
    db_session.flush()

    db_session.add(
        MatchDetail(
            fixture_id=live_fixture.id,
            provider="zafronix",
            provider_match_id="provider-live-centre-001",
            goals=[],
            cards=[],
            substitutions=[],
            formations={},
            lineups={},
            statistics={},
            referee={},
            weather={},
            created_at="2026-06-24T09:00:00+00:00",
            updated_at="2026-06-24T10:00:00+00:00",
        )
    )
    db_session.add(
        MatchDetailEventCoverage(
            fixture_id=live_fixture.id,
            provider="zafronix",
            event_coverage={
                "goals": "available",
                "cards": "available",
                "substitutions": "not_provided",
            },
            created_at="2026-06-24T09:00:00+00:00",
            updated_at="2026-06-24T10:00:00+00:00",
        )
    )
    db_session.commit()

    response = client.get("/live-match-centre")

    assert response.status_code == 200
    data = response.json()
    assert data["counts"] == {
        "live": 1,
        "completed": 1,
        "scheduled": 1,
        "unavailable": 1,
    }
    assert data["scheduled_sources"] == {
        "provider_status": 1,
        "stored_kickoff": 0,
    }
    assert len(data["matches"]) == 1
    match = data["matches"][0]
    assert match["external_id"] == "live-centre-001"
    assert match["match_state"] == "live"
    assert match["home_score"] == 1
    assert match["stored_fixture_updated_at"] == "2026-06-24T10:00:00+00:00"
    assert match["event_data"] == {
        "availability": "available",
        "provider": "zafronix",
        "stored_detail_updated_at": "2026-06-24T10:00:00+00:00",
        "event_coverage": {
            "goals": "available",
            "cards": "available",
            "substitutions": "not_provided",
        },
    }


def test_live_match_centre_makes_missing_and_legacy_event_coverage_explicit(
    client,
    db_session,
):
    no_detail_fixture = _fixture(external_id="live-no-detail")
    legacy_detail_fixture = _fixture(external_id="live-legacy-detail")
    db_session.add_all([no_detail_fixture, legacy_detail_fixture])
    db_session.flush()

    db_session.add(
        MatchDetail(
            fixture_id=legacy_detail_fixture.id,
            provider="legacy-provider",
            provider_match_id="legacy-live-detail",
            goals=[],
            cards=[],
            substitutions=[],
            formations={},
            lineups={},
            statistics={},
            referee={},
            weather={},
            created_at="2026-06-24T09:00:00+00:00",
            updated_at="2026-06-24T10:00:00+00:00",
        )
    )
    db_session.commit()

    response = client.get("/live-match-centre")

    assert response.status_code == 200
    matches_by_external_id = {
        match["external_id"]: match for match in response.json()["matches"]
    }
    assert matches_by_external_id["live-no-detail"]["event_data"] == {
        "availability": "detail_not_available",
        "provider": None,
        "stored_detail_updated_at": None,
        "event_coverage": {
            "goals": "detail_not_available",
            "cards": "detail_not_available",
            "substitutions": "detail_not_available",
        },
    }
    assert matches_by_external_id["live-legacy-detail"]["event_data"] == {
        "availability": "available",
        "provider": "legacy-provider",
        "stored_detail_updated_at": "2026-06-24T10:00:00+00:00",
        "event_coverage": {
            "goals": "coverage_unknown",
            "cards": "coverage_unknown",
            "substitutions": "coverage_unknown",
        },
    }


def test_live_match_centre_returns_recorded_latest_refresh_changes(client, db_session):
    sync_run = _success_run()
    db_session.add(sync_run)
    db_session.flush()
    db_session.add(_recorded_change_set(sync_run.id))
    db_session.commit()

    response = client.get("/live-match-centre")

    assert response.status_code == 200
    refresh = response.json()["latest_successful_refresh"]
    assert refresh["availability"] == "recorded"
    assert refresh["sync_run_id"] == sync_run.id
    assert refresh["completed_at"] == "2026-06-24T10:00:00+00:00"
    assert refresh["compared_fixture_count"] == 1
    assert refresh["changed_fixture_count"] == 1
    assert refresh["change_count"] == 2
    assert [change["type"] for change in refresh["changes"][0]["changes"]] == [
        "score_changed",
        "goal_added",
    ]


def test_live_match_centre_marks_historical_success_without_change_set(client, db_session):
    sync_run = _success_run()
    db_session.add(sync_run)
    db_session.commit()

    response = client.get("/live-match-centre")

    assert response.status_code == 200
    refresh = response.json()["latest_successful_refresh"]
    assert refresh == {
        "availability": "not_recorded_before_v1_18",
        "sync_run_id": sync_run.id,
        "completed_at": "2026-06-24T10:00:00+00:00",
        "compared_fixture_count": None,
        "changed_fixture_count": None,
        "change_count": None,
        "changes": [],
    }


def test_live_match_centre_marks_no_successful_refresh_as_not_started(client):
    response = client.get("/live-match-centre")

    assert response.status_code == 200
    data = response.json()
    assert data["data_freshness"] == {
        "state": "not_started",
        "last_success_at": None,
        "data_age_seconds": None,
        "fresh_after_seconds": 3600,
        "stale_after_seconds": 10800,
        "message": "No successful provider snapshot has been stored yet.",
    }
    assert data["latest_successful_refresh"] == {
        "availability": "not_started",
        "sync_run_id": None,
        "completed_at": None,
        "compared_fixture_count": 0,
        "changed_fixture_count": 0,
        "change_count": 0,
        "changes": [],
    }
    assert data["matches"] == []
    assert data["counts"] == {
        "live": 0,
        "completed": 0,
        "scheduled": 0,
        "unavailable": 0,
    }


def test_live_match_centre_keeps_latest_failure_visible_without_hiding_success(
    client,
    db_session,
):
    successful_run = _success_run()
    db_session.add(successful_run)
    db_session.flush()
    db_session.add(_recorded_change_set(successful_run.id))
    db_session.add(_failed_run())
    db_session.commit()

    response = client.get("/live-match-centre")

    assert response.status_code == 200
    data = response.json()
    assert data["data_freshness"]["state"] == "last_sync_failed"
    assert data["data_freshness"]["last_success_at"] == "2026-06-24T10:00:00+00:00"
    assert data["data_freshness"]["message"] == (
        "The latest provider refresh failed; displayed data is from the last "
        "successful stored snapshot."
    )
    assert data["latest_successful_refresh"]["availability"] == "recorded"
    assert data["latest_successful_refresh"]["sync_run_id"] == successful_run.id


def test_live_match_centre_is_read_only(client, db_session, monkeypatch):
    fixture = _fixture(external_id="live-read-only")
    db_session.add(fixture)
    db_session.commit()

    provider_call = {"count": 0}

    def provider_call_not_allowed(*args, **kwargs):
        provider_call["count"] += 1
        raise AssertionError("Live Match Centre must not call a provider")

    monkeypatch.setattr(
        "app.providers.factory.get_configured_football_provider",
        provider_call_not_allowed,
    )

    before_counts = {
        "fixtures": db_session.query(Fixture).count(),
        "details": db_session.query(MatchDetail).count(),
        "coverage": db_session.query(MatchDetailEventCoverage).count(),
        "runs": db_session.query(FixtureSyncRun).count(),
        "change_sets": db_session.query(FixtureSyncChangeSet).count(),
    }

    response = client.get("/live-match-centre")

    after_counts = {
        "fixtures": db_session.query(Fixture).count(),
        "details": db_session.query(MatchDetail).count(),
        "coverage": db_session.query(MatchDetailEventCoverage).count(),
        "runs": db_session.query(FixtureSyncRun).count(),
        "change_sets": db_session.query(FixtureSyncChangeSet).count(),
    }
    assert response.status_code == 200
    assert provider_call["count"] == 0
    assert after_counts == before_counts


def test_live_match_centre_counts_unknown_future_kickoff_as_scheduled(
    client,
    db_session,
    monkeypatch,
):
    reference_time = datetime(2026, 6, 24, 12, tzinfo=timezone.utc)
    monkeypatch.setattr(
        "app.services.live_match_centre_service._utc_now",
        lambda: reference_time,
    )

    explicit_live = _fixture(
        external_id="explicit-live-001",
        status="live",
        home_score=1,
        away_score=0,
    )
    explicit_scheduled = _fixture(
        external_id="provider-scheduled-001",
        status="scheduled",
        kickoff_time="2026-06-24T10:00:00Z",
        home_score=None,
        away_score=None,
    )
    unknown_future = _fixture(
        external_id="unknown-future-001",
        status="unknown",
        kickoff_time="2026-06-24T19:00:00.000Z",
        home_score=None,
        away_score=None,
    )
    unknown_at_kickoff = _fixture(
        external_id="unknown-at-kickoff-001",
        status="unknown",
        kickoff_time="2026-06-24T12:00:00Z",
        home_score=None,
        away_score=None,
    )
    unknown_with_score = _fixture(
        external_id="unknown-score-001",
        status="unknown",
        kickoff_time="2026-06-24T19:00:00Z",
        home_score=0,
        away_score=None,
    )
    postponed = _fixture(
        external_id="postponed-001",
        status="postponed",
        kickoff_time="2026-06-24T19:00:00Z",
        home_score=None,
        away_score=None,
    )
    db_session.add_all(
        [
            explicit_live,
            explicit_scheduled,
            unknown_future,
            unknown_at_kickoff,
            unknown_with_score,
            postponed,
        ]
    )
    db_session.commit()

    response = client.get("/live-match-centre")

    assert response.status_code == 200
    data = response.json()
    assert data["counts"] == {
        "live": 1,
        "completed": 0,
        "scheduled": 2,
        "unavailable": 3,
    }
    assert data["scheduled_sources"] == {
        "provider_status": 1,
        "stored_kickoff": 1,
    }
    assert [match["external_id"] for match in data["matches"]] == [
        "explicit-live-001"
    ]
