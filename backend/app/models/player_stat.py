from sqlalchemy import Column, Integer, String

from app.database import Base


class PlayerStat(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, index=True, nullable=False)

    competition = Column(String(100), default="FIFA World Cup 2026", nullable=False)
    stage = Column(String(100), default="Group Stage", nullable=False)
    group_name = Column(String(50), nullable=True)

    team = Column(String(100), nullable=False)
    team_code = Column(String(10), nullable=False)

    player_name = Column(String(120), nullable=False)
    position = Column(String(50), nullable=True)
    shirt_number = Column(Integer, nullable=True)

    appearances = Column(Integer, default=0, nullable=False)
    goals = Column(Integer, default=0, nullable=False)
    assists = Column(Integer, default=0, nullable=False)
    yellow_cards = Column(Integer, default=0, nullable=False)
    red_cards = Column(Integer, default=0, nullable=False)
    minutes_played = Column(Integer, default=0, nullable=False)

    created_at = Column(String(50), nullable=True)
    updated_at = Column(String(50), nullable=True)
