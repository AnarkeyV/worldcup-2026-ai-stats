"""Provider-declared event-category coverage for one stored match detail."""

from sqlalchemy import JSON, Column, ForeignKey, Integer, String

from app.database import Base


class MatchDetailEventCoverage(Base):
    """Persist provider event-category availability without changing match_details."""

    __tablename__ = "match_detail_event_coverage"

    id = Column(Integer, primary_key=True, index=True)
    fixture_id = Column(
        Integer,
        ForeignKey("fixtures.id"),
        unique=True,
        index=True,
        nullable=False,
    )
    provider = Column(String(50), default="unknown", nullable=False)
    event_coverage = Column(JSON, default=dict, nullable=False)
    created_at = Column(String(50), nullable=True)
    updated_at = Column(String(50), nullable=True)
