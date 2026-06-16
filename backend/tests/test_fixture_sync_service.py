from app.models.fixture import Fixture
from app.services.fixture_sync_service import sync_fixtures


def test_sync_fixtures_creates_new_fixture(db_session):
    fixtures = [
        {
            "external_id": "provider-fixture-1",
            "competition": "FIFA World Cup 2026",
            "stage": "Group Stage",
            "group_name": "Group A",
            "home_team": "Mexico",
            "away_team": "South Africa",
            "home_team_code": "MEX",
            "away_team_code": "RSA",
            "kickoff_time": "2026-06-11T19:00:00+00:00",
            "venue": "Estadio Azteca",
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        }
    ]

    result = sync_fixtures(db_session, fixtures)

    assert result["created"] == 1
    assert result["updated"] == 0
    assert result["total_fixtures"] == 1

    saved_fixture = (
        db_session.query(Fixture)
        .filter(Fixture.external_id == "provider-fixture-1")
        .first()
    )

    assert saved_fixture is not None
    assert saved_fixture.home_team == "Mexico"
    assert saved_fixture.away_team == "South Africa"
    assert saved_fixture.created_at is not None
    assert saved_fixture.updated_at is not None


def test_sync_fixtures_updates_existing_fixture(db_session):
    existing_fixture = Fixture(
        external_id="provider-fixture-2",
        competition="FIFA World Cup 2026",
        stage="Group Stage",
        group_name="Group D",
        home_team="United States",
        away_team="Paraguay",
        home_team_code="USA",
        away_team_code="PAR",
        kickoff_time="2026-06-12T21:00:00+00:00",
        venue="SoFi Stadium",
        status="scheduled",
        home_score=None,
        away_score=None,
        created_at="2026-06-16T00:00:00+00:00",
        updated_at="2026-06-16T00:00:00+00:00",
    )
    db_session.add(existing_fixture)
    db_session.commit()

    fixtures = [
        {
            "external_id": "provider-fixture-2",
            "competition": "FIFA World Cup 2026",
            "stage": "Group Stage",
            "group_name": "Group D",
            "home_team": "United States",
            "away_team": "Paraguay",
            "home_team_code": "USA",
            "away_team_code": "PAR",
            "kickoff_time": "2026-06-12T21:00:00+00:00",
            "venue": "SoFi Stadium",
            "status": "complete",
            "home_score": 4,
            "away_score": 1,
        }
    ]

    result = sync_fixtures(db_session, fixtures)

    assert result["created"] == 0
    assert result["updated"] == 1
    assert result["total_fixtures"] == 1

    saved_fixture = (
        db_session.query(Fixture)
        .filter(Fixture.external_id == "provider-fixture-2")
        .first()
    )

    assert saved_fixture.status == "complete"
    assert saved_fixture.home_score == 4
    assert saved_fixture.away_score == 1
    assert saved_fixture.created_at == "2026-06-16T00:00:00+00:00"
    assert saved_fixture.updated_at != "2026-06-16T00:00:00+00:00"

def test_sync_fixtures_detects_newly_completed_existing_fixture(db_session):
    existing_fixture = Fixture(
        external_id="provider-fixture-3",
        competition="FIFA World Cup 2026",
        stage="Group Stage",
        group_name="Group I",
        home_team="France",
        away_team="Senegal",
        home_team_code="FRA",
        away_team_code="SEN",
        kickoff_time="2026-06-16T19:00:00+00:00",
        venue="MetLife Stadium",
        status="scheduled",
        home_score=None,
        away_score=None,
        created_at="2026-06-16T00:00:00+00:00",
        updated_at="2026-06-16T00:00:00+00:00",
    )
    db_session.add(existing_fixture)
    db_session.commit()

    fixtures = [
        {
            "external_id": "provider-fixture-3",
            "competition": "FIFA World Cup 2026",
            "stage": "Group Stage",
            "group_name": "Group I",
            "home_team": "France",
            "away_team": "Senegal",
            "home_team_code": "FRA",
            "away_team_code": "SEN",
            "kickoff_time": "2026-06-16T19:00:00+00:00",
            "venue": "MetLife Stadium",
            "status": "complete",
            "home_score": 2,
            "away_score": 1,
        }
    ]

    result = sync_fixtures(db_session, fixtures)

    assert result["created"] == 0
    assert result["updated"] == 1
    assert result["newly_completed_count"] == 1
    assert result["newly_completed"] == ["provider-fixture-3"]


def test_sync_fixtures_does_not_duplicate_already_completed_fixture(db_session):
    existing_fixture = Fixture(
        external_id="provider-fixture-4",
        competition="FIFA World Cup 2026",
        stage="Group Stage",
        group_name="Group J",
        home_team="Argentina",
        away_team="Algeria",
        home_team_code="ARG",
        away_team_code="DZA",
        kickoff_time="2026-06-16T21:00:00+00:00",
        venue="Hard Rock Stadium",
        status="complete",
        home_score=3,
        away_score=0,
        created_at="2026-06-16T00:00:00+00:00",
        updated_at="2026-06-16T00:00:00+00:00",
    )
    db_session.add(existing_fixture)
    db_session.commit()

    fixtures = [
        {
            "external_id": "provider-fixture-4",
            "competition": "FIFA World Cup 2026",
            "stage": "Group Stage",
            "group_name": "Group J",
            "home_team": "Argentina",
            "away_team": "Algeria",
            "home_team_code": "ARG",
            "away_team_code": "DZA",
            "kickoff_time": "2026-06-16T21:00:00+00:00",
            "venue": "Hard Rock Stadium",
            "status": "complete",
            "home_score": 3,
            "away_score": 0,
        }
    ]

    result = sync_fixtures(db_session, fixtures)

    assert result["created"] == 0
    assert result["updated"] == 1
    assert result["newly_completed_count"] == 0
    assert result["newly_completed"] == []