from sqlalchemy import Column, Integer, String

from app.database import Base


class Fixture(Base):
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, index=True, nullable=False)

    competition = Column(String(100), default="FIFA World Cup 2026", nullable=False)
    stage = Column(String(100), default="Group Stage", nullable=False)
    group_name = Column(String(50), nullable=True)

    home_team = Column(String(100), nullable=False)
    away_team = Column(String(100), nullable=False)
    home_team_code = Column(String(10), nullable=False)
    away_team_code = Column(String(10), nullable=False)

    kickoff_time = Column(String(50), nullable=False)
    venue = Column(String(150), nullable=True)
    status = Column(String(50), default="scheduled", nullable=False)

    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)

    created_at = Column(String(50), nullable=True)
    updated_at = Column(String(50), nullable=True)