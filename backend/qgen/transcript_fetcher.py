"""
transcript_fetcher.py
----------------------
Pulls the caption/transcript text for a YouTube video referenced in
VIDEO_DB, and caches it to disk so we only ever fetch each video once.

Requires network access to youtube.com — this only works when run on a
machine with normal internet access (the generation is meant to run
offline/in batch via generate_quiz_bank.py, not live during a user's
quiz session).
"""

import json
import os
import re

TRANSCRIPT_CACHE_DIR = os.path.join(os.path.dirname(__file__), "_cache", "transcripts")


def _video_id_from_url(url: str) -> str:
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    if not match:
        raise ValueError(f"Could not extract a YouTube video id from URL: {url}")
    return match.group(1)


def _cache_path(video_id: str) -> str:
    os.makedirs(TRANSCRIPT_CACHE_DIR, exist_ok=True)
    return os.path.join(TRANSCRIPT_CACHE_DIR, f"{video_id}.json")


def fetch_transcript(url: str, force_refresh: bool = False) -> str:
    """
    Returns the full transcript of the video at `url` as one plain-text
    string (timestamps stripped, captions joined with spaces).

    Cached on disk under qgen/_cache/transcripts/<video_id>.json so
    repeat calls (e.g. re-running the batch generator) don't re-fetch.
    """
    video_id = _video_id_from_url(url)
    cache_file = _cache_path(video_id)

    if not force_refresh and os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)["text"]

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as e:
        raise RuntimeError(
            "youtube-transcript-api is not installed. Run: "
            "pip install youtube-transcript-api"
        ) from e

    fetched = YouTubeTranscriptApi().fetch(video_id)
    text = " ".join(snippet.text.strip() for snippet in fetched if snippet.text.strip())
    text = re.sub(r"\s+", " ", text).strip()

    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump({"video_id": video_id, "url": url, "text": text}, f)

    return text
