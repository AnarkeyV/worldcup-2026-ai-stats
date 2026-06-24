from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint

from app.database import Base


class OfficialMatchVideo(Base):
    """A manually verified, outbound-only official video destination.

    Records are intentionally not created through a public HTTP endpoint. They
    are designed for a later controlled local import workflow after a curator
    verifies the exact official source and match association.
    """

    __tablename__ = "official_match_videos"
    __table_args__ = (
        UniqueConstraint(
            "fixture_id",
            "source_key",
            "external_url",
            name="uq_official_match_video_fixture_source_url",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    fixture_id = Column(
        Integer,
        ForeignKey("fixtures.id"),
        nullable=False,
        index=True,
    )

    source_key = Column(String(50), nullable=False)
    content_type = Column(String(50), nullable=False)
    title = Column(String(250), nullable=False)
    external_url = Column(String(1000), nullable=False)

    territory = Column(String(50), default="global", nullable=False)
    is_match_specific = Column(Boolean, default=True, nullable=False)

    published_at = Column(String(50), nullable=True)
    verified_at = Column(String(50), nullable=False)
    created_at = Column(String(50), nullable=True)
    updated_at = Column(String(50), nullable=True)
