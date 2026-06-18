"""
YouTube Transcript Fetcher
Extracts transcripts from YouTube videos with timestamp metadata.
"""

import re
import logging
import urllib.request
import json
import asyncio
import html
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


def timestamp_to_seconds(ts_str: str) -> float:
    """Convert timestamp format [H:MM:SS] or [MM:SS] to seconds."""
    parts = list(map(int, ts_str.split(':')))
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 1:
        return parts[0]
    return 0.0


async def fetch_transcript_fallback(video_id: str) -> TranscriptResult:
    """
    Fallback fetcher using youtube-transcript.ai when YouTube blocks the server IP.
    """
    logger.info(f"Using fallback scraper for video: {video_id}")
    url = f"https://youtube-transcript.ai/transcript/{video_id}.txt"
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        loop = asyncio.get_event_loop()
        def get_content():
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8')
        content = await loop.run_in_executor(None, get_content)
        
        # Clean HTML entities and non-breaking spaces
        content = html.unescape(content)
        content = content.replace('\xa0', ' ')
        
        # Try to extract total duration from header: "Duration: 2:22"
        duration_match = re.search(r'Duration:\s*(\d+(?::\d+)+)', content)
        total_duration = 0.0
        if duration_match:
            try:
                total_duration = timestamp_to_seconds(duration_match.group(1))
            except Exception:
                pass

        # Extract title
        title_match = re.search(r'# Transcript:\s*(.+)', content)
        title = title_match.group(1).strip() if title_match else f"YouTube Video ({video_id})"

        # Find the transcript section
        transcript_part = ""
        if "## Transcript" in content:
            transcript_part = content.split("## Transcript")[1]
        else:
            transcript_part = content

        if "---" in transcript_part:
            transcript_part = transcript_part.split("---")[0]

        # Extract segments
        pattern = r'\[(\d+(?::\d+)+)\]\s*(.*?)(?=\s*\[\d+(?::\d+)+\]|\s*$)'
        matches = re.findall(pattern, transcript_part, re.DOTALL)

        segments = []
        for i, (ts, text) in enumerate(matches):
            start = timestamp_to_seconds(ts)
            clean_text = " ".join(text.split())
            segments.append({
                "text": clean_text,
                "start": start,
                "duration": 0.0,
                "timestamp": ts
            })

        # Calculate durations
        for i in range(len(segments)):
            if i < len(segments) - 1:
                segments[i]["duration"] = segments[i+1]["start"] - segments[i]["start"]
            else:
                if total_duration > segments[i]["start"]:
                    segments[i]["duration"] = total_duration - segments[i]["start"]
                else:
                    segments[i]["duration"] = 30.0

        full_text = " ".join(seg["text"] for seg in segments)
        thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

        # Try to fetch additional metadata using YouTube oEmbed API
        channel = None
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={video_id}&format=json"
            def get_oembed():
                req_oe = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_oe, timeout=5) as resp:
                    return json.loads(resp.read().decode())
            data = await loop.run_in_executor(None, get_oembed)
            title = data.get("title", title)
            channel = data.get("author_name", channel)
        except Exception as oe_err:
            logger.warning(f"Failed to fetch oEmbed metadata in fallback: {oe_err}")

        return TranscriptResult(
            video_id=video_id,
            title=title,
            channel=channel,
            thumbnail=thumbnail,
            full_text=full_text,
            segments=segments,
            language="en"
        )
    except Exception as e:
        logger.error(f"Fallback transcript fetch failed for {video_id}: {e}")
        raise


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
            # Try fallback
            try:
                return await fetch_transcript_fallback(video_id)
            except Exception as fallback_error:
                logger.error(f"Fallback fetch failed as well: {fallback_error}")
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
