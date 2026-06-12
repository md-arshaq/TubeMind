"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────

class VideoStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


# ──────────────────────────────────────────────
# Video Schemas
# ──────────────────────────────────────────────

class VideoCreateRequest(BaseModel):
    """Request to analyze a YouTube video."""
    url: str = Field(..., description="YouTube video URL", examples=["https://www.youtube.com/watch?v=Gfr50f6ZBvo"])


class VideoResponse(BaseModel):
    """Response after video analysis."""
    id: str
    video_id: str
    title: str
    channel: Optional[str] = None
    thumbnail: Optional[str] = None
    duration: Optional[str] = None
    chunks_count: int = 0
    status: VideoStatus
    summary: Optional[str] = None
    topics: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """Response for listing all videos."""
    videos: List[VideoResponse]
    total: int


# ──────────────────────────────────────────────
# Chat Schemas
# ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Request to ask a question about a video."""
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question to ask about the video",
        examples=["What are the main topics discussed in this video?"]
    )


class SourceChunk(BaseModel):
    """A source chunk from the transcript."""
    text: str
    timestamp: Optional[str] = None
    relevance_score: Optional[float] = None


class ChatResponse(BaseModel):
    """Response to a chat question."""
    id: str
    question: str
    answer: str
    sources: List[SourceChunk] = []
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    """Response for chat history of a video."""
    video_id: str
    messages: List[ChatResponse]
    total: int


# ──────────────────────────────────────────────
# Summary Schemas
# ──────────────────────────────────────────────

class SummaryResponse(BaseModel):
    """Response for video summary."""
    video_id: str
    summary: str
    topics: List[str]
    key_points: List[str]


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    environment: str
