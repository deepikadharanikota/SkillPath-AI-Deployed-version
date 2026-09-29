"""
cache.py
--------
Persists generated questions to disk, in the exact same shape as the
static QUIZ_BANK in data.py:

    {"Python": [{"level": "easy", "q": ..., "opts": [...], "ans": 1,
                 "explanation": ..., "source_video": "..."}, ...], ...}

Generation is a slow, offline, batch step (transcript fetch + model
inference) — it should never run live during a user's quiz. This module
is the boundary: generate_quiz_bank.py writes here once, main.py only
ever reads from here (with a fallback to the static QUIZ_BANK if a topic
hasn't been generated yet).
"""

import json
import os

CACHE_DIR = os.path.join(os.path.dirname(__file__), "_cache")
BANK_PATH = os.path.join(CACHE_DIR, "generated_quiz_bank.json")


def _load_all() -> dict:
    if not os.path.exists(BANK_PATH):
        return {}
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_all(bank: dict) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(BANK_PATH, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2)


def save_topic_questions(topic: str, questions: list[dict]) -> None:
    bank = _load_all()
    bank[topic] = questions
    _save_all(bank)


def load_topic_questions(topic: str) -> list[dict] | None:
    """Returns the generated question list for `topic`, or None if
    nothing has been generated for it yet (caller should fall back to
    the static QUIZ_BANK)."""
    bank = _load_all()
    return bank.get(topic)


def has_generated_content() -> bool:
    return os.path.exists(BANK_PATH) and bool(_load_all())
