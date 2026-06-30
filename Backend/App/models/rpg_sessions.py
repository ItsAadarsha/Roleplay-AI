
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from app.database import Base

def _uuid() -> str:
    return str(uuid.uuid4())

def _now() -> datetime:
    return datetime.now(timezone.utc)

class RpgSession(Base):
    __tablename__ = "rpg_sessions"

    id = Column(String, primary_key=True, default=_uuid)
    title = Column(String, nullable=False)
    synopsis = Column(Text, nullable=True)
    genre = Column(String, nullable=True)
    world_key = Column(String, nullable=True, index=True)
    magic_rules_md = Column(Text, nullable=True)
    active_chapter_number = Column(Integer, nullable=False, default=1)
    word_count_total = Column(Integer, nullable=False, default=0)
    context_token_limit = Column(Integer, nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )

    chapters = relationship(
        "ChronicleChapter",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChronicleChapter.number",
    )

    # These are defined in their own model files (character.py, lore.py)
    # but declared here too via back_populates once those files exist:
    # characters = relationship("Character", back_populates="session", cascade="all, delete-orphan")
    # lore_entries = relationship("LoreEntry", back_populates="session", cascade="all, delete-orphan")
    # story_beats = relationship("StoryBeat", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<RpgSession id={self.id!r} title={self.title!r}>"


class ChronicleChapter(Base):

    __tablename__ = "chronicle_chapters"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(
        String, ForeignKey("rpg_sessions.id", ondelete="CASCADE"), nullable=False
    )

    number = Column(Integer, nullable=False)
    summary = Column(Text, nullable=True)

    # Raw turn-by-turn messages for this chapter, stored as JSON text.
    # Kept as a single JSON blob rather than a separate Message table for
    # now -- simplest option while the schema is still settling. Revisit
    # if you need to query into individual messages later.
    messages_json = Column(Text, nullable=False, default="[]")

    # Token count of messages_json at last write -- lets the turn handler
    # decide whether to close this chapter and start a new one without
    # re-tokenizing the whole blob every turn.
    token_count = Column(Integer, nullable=False, default=0)

    is_closed = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    session = relationship("RpgSession", back_populates="chapters")

    def __repr__(self) -> str:
        return (
            f"<ChronicleChapter id={self.id!r} session_id={self.session_id!r} "
            f"number={self.number} closed={self.is_closed}>"
        )