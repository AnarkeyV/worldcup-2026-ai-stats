"""Provider-backed fixture changes captured for one successful sync run."""

from sqlalchemy import JSON, Column, ForeignKey, Integer, String

from app.database import Base


class FixtureSyncChangeSet(Base):
    """Persist the factual delta calculated during one v1.18+ sync run."""

    __tablename__ = "fixture_sync_change_sets"

    id = Column(Integer, primary_key=True, index=True)
    sync_run_id = Column(
        Integer,
        ForeignKey("fixture_sync_runs.id"),
        unique=True,
        index=True,
        nullable=False,
    )
    capture_state = Column(String(50), default="recorded", nullable=False)
    compared_fixture_count = Column(Integer, default=0, nullable=False)
    changed_fixture_count = Column(Integer, default=0, nullable=False)
    total_change_count = Column(Integer, default=0, nullable=False)
    changes = Column(JSON, default=list, nullable=False)
    created_at = Column(String(50), nullable=True)
