"""
pipeline.py
------------
Orchestrates the full offline pipeline for one topic:

    for each video in that topic's VIDEO_DB entries:
        fetch transcript -> chunk -> extract candidate answers
        for each candidate:
            generate a question (T5 or cloze fallback)
            classify its difficulty
            build 3 distractors from the video's own candidate-answer pool
            validate + dedupe
    until we have `target_per_level` questions at each of easy/medium/hard

Output shape matches data.py's QUIZ_BANK exactly (plus one extra
"source_video" field main.py doesn't need to read), so it's a drop-in
replacement.
"""

import random

from .transcript_fetcher import fetch_transcript
from .chunker import chunk_transcript
from .answer_extractor import extract_candidate_answers
from .question_generator import get_question_generator
from .difficulty import classify_difficulty
from .distractors import build_distractors

LEVELS = ("easy", "medium", "hard")


def _iter_topic_videos(topic: str, video_db: dict):
    """Yields every {"title", "url", ...} video dict under this topic,
    across all difficulty tiers and modules — more source material makes
    for a bigger, more varied question pool."""
    for difficulty, modules in video_db.get(topic, {}).items():
        for module_key, videos in modules.items():
            for v in videos:
                yield v


def _make_question(answer: str, sentence: str, generator, source_video: dict) -> dict | None:
    question = generator.generate(answer, sentence)
    if not question or len(question.split()) < 3:
        return None
    level = classify_difficulty(question, sentence)
    explanation = f"From the video \"{source_video['title']}\": {sentence}"
    return {
        "level": level,
        "q": question,
        "_answer_text": answer,     # used to build opts/ans below, stripped before saving
        "_sentence": sentence,
        "explanation": explanation,
        "source_video": source_video["title"],
    }


def generate_topic_quiz_bank(
    topic: str,
    video_db: dict,
    target_per_level: int = 5,
    generator=None,
    seed: int | None = None,
) -> list[dict]:
    rng = random.Random(seed)
    generator = generator or get_question_generator()

    videos = list(_iter_topic_videos(topic, video_db))
    if not videos:
        return []

    counts = {lvl: 0 for lvl in LEVELS}
    results: list[dict] = []
    seen_questions: set[str] = set()

    # Build one shared distractor pool per video (its own candidate
    # answers), so distractors stay plausible/on-topic per source.
    for video in videos:
        if all(counts[lvl] >= target_per_level for lvl in LEVELS):
            break
        try:
            transcript = fetch_transcript(video["url"])
        except Exception:
            continue  # skip videos we can't fetch (no captions, no network, etc.)

        chunks = chunk_transcript(transcript)
        video_candidates = []
        for chunk in chunks:
            video_candidates.extend(extract_candidate_answers(chunk))
        if not video_candidates:
            continue

        answer_pool = [c["answer"] for c in video_candidates]
        rng.shuffle(video_candidates)

        for cand in video_candidates:
            if all(counts[lvl] >= target_per_level for lvl in LEVELS):
                break
            raw = _make_question(cand["answer"], cand["sentence"], generator, video)
            if raw is None:
                continue
            if raw["q"].lower() in seen_questions:
                continue
            if counts[raw["level"]] >= target_per_level:
                continue  # already have enough at this level, skip to keep the bank balanced

            distractors = build_distractors(raw["_answer_text"], answer_pool, n=3)
            opts = distractors + [raw["_answer_text"]]
            rng.shuffle(opts)
            ans_idx = opts.index(raw["_answer_text"])

            results.append({
                "level": raw["level"],
                "q": raw["q"],
                "opts": opts,
                "ans": ans_idx,
                "explanation": raw["explanation"],
                "source_video": raw["source_video"],
            })
            seen_questions.add(raw["q"].lower())
            counts[raw["level"]] += 1

    return results
