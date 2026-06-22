from sqlalchemy import JSON, Column, ForeignKey, Integer, String

from app.database import Base


class MatchDetail(Base):
    __tablename__ = "match_details"

    id = Column(Integer, primary_key=True, index=True)
    fixture_id = Column(
        Integer,
        ForeignKey("fixtures.id"),
        unique=True,
        index=True,
        nullable=False,
    )

    provider = Column(String(50), default="unknown", nullable=False)
    provider_match_id = Column(String(100), nullable=True)

    goals = Column(JSON, default=list, nullable=False)
    cards = Column(JSON, default=list, nullable=False)
    substitutions = Column(JSON, default=list, nullable=False)

    formations = Column(JSON, default=dict, nullable=False)
    lineups = Column(JSON, default=dict, nullable=False)
    statistics = Column(JSON, default=dict, nullable=False)

    referee = Column(JSON, default=dict, nullable=False)
    weather = Column(JSON, default=dict, nullable=False)

    created_at = Column(String(50), nullable=True)
    updated_at = Column(String(50), nullable=True)
