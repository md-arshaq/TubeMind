"""
Chat API Routes
Endpoints for chatting with analyzed YouTube videos using RAG.
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    SourceChunk,
)
from app.models.database import Video, ChatMessage
from app.db.session import get_db
from app.core.rag import ask_question

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/videos", tags=["chat"])


@router.post("/{video_id}/chat", response_model=ChatResponse)
async def chat_with_video(
    video_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Ask a question about a specific video.
    Uses the RAG pipeline to retrieve relevant transcript chunks
    and generate a contextual answer using Gemini.
    """
    # Verify video exists and is ready
    result = await db.execute(
        select(Video).where(Video.video_id == video_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")
    if video.status != "ready":
        raise HTTPException(
            status_code=400,
            detail=f"Video is not ready for chat. Status: {video.status}"
        )

    try:
        # Run RAG pipeline
        rag_response = await ask_question(video_id, request.question)

        # Build source chunks
        sources = [
            SourceChunk(
                text=s["text"],
                timestamp=s.get("timestamp"),
            )
            for s in rag_response.sources
        ]

        # Persist chat message
        message_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        chat_message = ChatMessage(
            id=message_id,
            video_id=video_id,
            question=request.question,
            answer=rag_response.answer,
            sources=[s.model_dump() for s in sources],
            created_at=now,
        )
        db.add(chat_message)
        await db.flush()

        return ChatResponse(
            id=message_id,
            question=request.question,
            answer=rag_response.answer,
            sources=sources,
            created_at=now,
        )

    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}"
        )


@router.get("/{video_id}/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    video_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the chat history for a specific video."""
    # Verify video exists
    result = await db.execute(
        select(Video).where(Video.video_id == video_id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")

    # Get chat messages
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.video_id == video_id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = result.scalars().all()

    return ChatHistoryResponse(
        video_id=video_id,
        messages=[
            ChatResponse(
                id=msg.id,
                question=msg.question,
                answer=msg.answer,
                sources=[
                    SourceChunk(**s) for s in (msg.sources or [])
                ],
                created_at=msg.created_at,
            )
            for msg in messages
        ],
        total=len(messages),
    )
