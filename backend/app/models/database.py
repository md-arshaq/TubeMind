"""
Database Models
SQLAlchemy ORM models for persistent storage.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Video(Base):
    """Represents an analyzed YouTube video."""
    __tablename__ = "videos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String, unique=True, nullable=False, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    channel = Column(String, nullable=True)
    thumbnail = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    chunks_count = Column(Integer, default=0)
    status = Column(String, default="processing")  # processing, ready, failed
    summary = Column(Text, nullable=True)
    topics = Column(JSON, nullable=True)  # List of topic strings
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    messages = relationship("ChatMessage", back_populates="video", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Represents a chat message (question + answer) for a video."""
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String, ForeignKey("videos.video_id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # List of source chunks
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    video = relationship("Video", back_populates="messages")
