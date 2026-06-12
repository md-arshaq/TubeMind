"""
Video API Routes
Endpoints for analyzing YouTube videos and managing the video library.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.schemas import (
    VideoCreateRequest,
    VideoResponse,
    VideoListResponse,
    SummaryResponse,
    VideoStatus,
)
from app.models.database import Video
from app.db.session import get_db
from app.core.transcript import fetch_transcript
from app.core.vectorstore import create_vector_store, delete_vector_store
from app.core.rag import generate_summary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.post("", response_model=VideoResponse, status_code=201)
async def analyze_video(
    request: VideoCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a YouTube video URL for analysis.
    Fetches the transcript, chunks it, generates embeddings, and stores in vector DB.
    """
    try:
        # Fetch transcript
        transcript = await fetch_transcript(request.url)

        # Check if video already exists
        result = await db.execute(
            select(Video).where(Video.video_id == transcript.video_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            # Return existing video if already analyzed
            return _video_to_response(existing)

        # Create vector store with embeddings
        chunks_count = await create_vector_store(
            video_id=transcript.video_id,
            transcript_text=transcript.full_text,
            segments=transcript.segments,
        )

        # Save to database
        video = Video(
            video_id=transcript.video_id,
            url=request.url,
            title=transcript.title,
            channel=transcript.channel,
            thumbnail=transcript.thumbnail,
            chunks_count=chunks_count,
            status="ready",
        )
        db.add(video)
        await db.flush()
        await db.refresh(video)

        logger.info(f"Video analyzed successfully: {transcript.video_id}")
        return _video_to_response(video)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing video: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze video: {str(e)}"
        )


@router.get("", response_model=VideoListResponse)
async def list_videos(db: AsyncSession = Depends(get_db)):
    """List all analyzed videos."""
    result = await db.execute(
        select(Video).order_by(Video.created_at.desc())
    )
    videos = result.scalars().all()
    return VideoListResponse(
        videos=[_video_to_response(v) for v in videos],
        total=len(videos),
    )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, db: AsyncSession = Depends(get_db)):
    """Get details of a specific analyzed video."""
    video = await _get_video_or_404(video_id, db)
    return _video_to_response(video)


@router.delete("/{video_id}", status_code=204)
async def delete_video(video_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a video and its associated data."""
    video = await _get_video_or_404(video_id, db)

    # Delete vector store
    await delete_vector_store(video_id)

    # Delete from database
    await db.delete(video)
    logger.info(f"Video deleted: {video_id}")


@router.post("/{video_id}/summary", response_model=SummaryResponse)
async def summarize_video(
    video_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Generate or regenerate a summary for a video."""
    video = await _get_video_or_404(video_id, db)

    try:
        result = await generate_summary(video_id)

        # Update video with summary
        video.summary = result["summary"]
        video.topics = result["topics"]
        await db.flush()

        return SummaryResponse(
            video_id=video_id,
            summary=result["summary"],
            topics=result["topics"],
            key_points=result["key_points"],
        )
    except Exception as e:
        logger.error(f"Error generating summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

async def _get_video_or_404(video_id: str, db: AsyncSession) -> Video:
    """Get a video by its YouTube video ID or raise 404."""
    result = await db.execute(
        select(Video).where(Video.video_id == video_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")
    return video


def _video_to_response(video: Video) -> VideoResponse:
    """Convert a Video ORM model to a response schema."""
    return VideoResponse(
        id=video.id,
        video_id=video.video_id,
        title=video.title,
        channel=video.channel,
        thumbnail=video.thumbnail,
        duration=video.duration,
        chunks_count=video.chunks_count,
        status=VideoStatus(video.status),
        summary=video.summary,
        topics=video.topics,
        created_at=video.created_at,
        updated_at=video.updated_at,
    )
