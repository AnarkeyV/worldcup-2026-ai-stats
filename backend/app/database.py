from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


def build_engine():
    if settings.database_url.startswith("sqlite"):
        return create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
    )


engine = build_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def create_db_and_tables() -> None:
    from app.models.fixture import Fixture
    from app.models.fixture_sync_run import FixtureSyncRun
    from app.models.match_detail import MatchDetail
    from app.models.player_stat import PlayerStat

    _ = Fixture, FixtureSyncRun, MatchDetail, PlayerStat

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
