"""
YouTube Transcript Fetcher
Extracts transcripts from YouTube videos with timestamp metadata.
"""

import re
import logging
import urllib.request
import json
from typing import Optional
from dataclasses import dataclass

from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)


@dataclass
class TranscriptResult:
    """Result of a transcript fetch operation."""
    video_id: str
    title: str
    channel: Optional[str]
    thumbnail: str
    full_text: str
    segments: list  # List of {text, start, duration} dicts
    language: str


def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from various URL formats.
    
    Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/v/VIDEO_ID
        - Just the video ID itself
    """
    patterns = [
        r'(?:v=|\/v\/|youtu\.be\/|embed\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url}")


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS or MM:SS format."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


async def fetch_transcript(url: str) -> TranscriptResult:
    """
    Fetch the transcript for a YouTube video.
    
    Args:
        url: YouTube video URL or video ID
        
    Returns:
        TranscriptResult with the full transcript text and segments
        
    Raises:
        ValueError: If the URL is invalid
        Exception: If transcript is not available
    """
    video_id = extract_video_id(url)
    logger.info(f"Fetching transcript for video: {video_id}")

    yt_api = YouTubeTranscriptApi()

    try:
        # Fetch transcript segments (defaulting to English)
        transcript_list = yt_api.fetch(
            video_id,
            languages=["en", "en-US", "en-GB"]
        )
    except Exception as e:
        logger.warning(f"English transcript not found, trying any language: {e}")
        try:
            # Get the first available transcript in any language
            transcripts = yt_api.list(video_id)
            transcript_list = next(iter(transcripts)).fetch()
        except Exception as e2:
            logger.error(f"No transcript available for {video_id}: {e2}")
            raise Exception(
                f"No transcript/captions available for this video. "
                f"The video might not have captions enabled."
            ) from e2

    # Build the segments list with timestamps
    segments = []
    for segment in transcript_list:
        # Handle both old (dict) and new (dataclass) versions of youtube-transcript-api
        text = segment["text"] if isinstance(segment, dict) else segment.text
        start = segment["start"] if isinstance(segment, dict) else segment.start
        duration = segment.get("duration", 0) if isinstance(segment, dict) else getattr(segment, "duration", 0)
        
        segments.append({
            "text": text,
            "start": start,
            "duration": duration,
            "timestamp": format_timestamp(start)
        })

    # Build full text
    full_text = " ".join(segment["text"] for segment in segments)

    # Build thumbnail URL
    thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    # Fetch metadata using YouTube oEmbed API
    title = f"YouTube Video ({video_id})"
    channel = None
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={video_id}&format=json"
        with urllib.request.urlopen(oembed_url) as response:
            data = json.loads(response.read().decode())
            title = data.get("title", title)
            channel = data.get("author_name", channel)
    except Exception as e:
        logger.warning(f"Failed to fetch oEmbed metadata for {video_id}: {e}")

    logger.info(
        f"Transcript fetched: {len(segments)} segments, "
        f"{len(full_text)} characters"
    )

    return TranscriptResult(
        video_id=video_id,
        title=title,
        channel=channel,
        thumbnail=thumbnail,
        full_text=full_text,
        segments=segments,
        language="en"
    )
