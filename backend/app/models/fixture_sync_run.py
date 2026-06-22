from sqlalchemy import JSON, Column, Float, Integer, String, Text

from app.database import Base


class FixtureSyncRun(Base):
    """Persisted audit record for one fixture sync attempt."""

    __tablename__ = "fixture_sync_runs"

    id = Column(Integer, primary_key=True, index=True)

    source = Column(String(50), nullable=False)
    provider = Column(String(50), nullable=False)
    trigger_type = Column(String(30), default="manual", nullable=False)
    status = Column(String(20), nullable=False)

    started_at = Column(String(50), nullable=False)
    completed_at = Column(String(50), nullable=False)
    duration_seconds = Column(Float, nullable=True)

    total_fixtures = Column(Integer, default=0, nullable=False)
    created = Column(Integer, default=0, nullable=False)
    updated = Column(Integer, default=0, nullable=False)
    newly_completed_count = Column(Integer, default=0, nullable=False)
    newly_completed = Column(JSON, default=list, nullable=False)

    last_error = Column(Text, nullable=True)
