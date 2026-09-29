"""
generate_quiz_bank.py
-----------------------
Offline batch generator. Run this once (and re-run whenever you add new
videos to VIDEO_DB) — NOT during a live user session:

    python generate_quiz_bank.py                  # all topics
    python generate_quiz_bank.py Python "Deep Learning"   # specific topics

Needs real internet access (to fetch YouTube captions and, the first
time, to download the T5 question-generation model). Results are cached
to qgen/_cache/generated_quiz_bank.json; main.py reads from there at
quiz time, falling back to the static QUIZ_BANK in data.py for any topic
that hasn't been generated yet.
"""

import sys

from data import TOPICS, VIDEO_DB
from qgen.pipeline import generate_topic_quiz_bank
from qgen.question_generator import get_question_generator
from qgen.cache import save_topic_questions


def main():
    requested = sys.argv[1:] or TOPICS
    unknown = [t for t in requested if t not in TOPICS]
    if unknown:
        print(f"Unknown topic(s): {unknown}. Valid topics: {TOPICS}")
        sys.exit(1)

    print("Loading question-generation model (this may download ~850MB the first time)...")
    generator = get_question_generator()
    print(f"Using: {type(generator).__name__}")

    for topic in requested:
        print(f"\n=== Generating questions for: {topic} ===")
        questions = generate_topic_quiz_bank(topic, VIDEO_DB, target_per_level=5, generator=generator)
        by_level = {"easy": 0, "medium": 0, "hard": 0}
        for q in questions:
            by_level[q["level"]] += 1
        print(f"  Generated {len(questions)} questions -> {by_level}")
        if questions:
            save_topic_questions(topic, questions)
            print(f"  Saved to qgen/_cache/generated_quiz_bank.json")
        else:
            print(f"  No questions generated for {topic} — check network/transcript availability. "
                  f"main.py will keep using the static QUIZ_BANK for this topic.")


if __name__ == "__main__":
    main()
