"""
distractors.py
----------------
Builds the wrong MCQ options for a generated question. Rather than
pulling in another model, this reuses other candidate answers already
extracted from the same video (see answer_extractor.py) — they're
guaranteed to be plausible (real terms from the same video) while being
verifiably wrong (not the correct answer for this specific question).
"""

import random


def build_distractors(correct_answer: str, all_candidate_answers: list[str], n: int = 3) -> list[str]:
    """
    all_candidate_answers: every candidate answer extracted across the
    whole video (not just this chunk) — the bigger the pool, the better
    the distractors.
    """
    correct_lower = correct_answer.lower()
    pool = [
        a for a in dict.fromkeys(all_candidate_answers)  # de-dupe, preserve order
        if a.lower() != correct_lower
        and correct_lower not in a.lower()
        and a.lower() not in correct_lower
    ]
    random.shuffle(pool)

    distractors = pool[:n]
    # Not enough real candidates (short/early video) — pad with generic
    # plausible-sounding but clearly-not-correct filler so the question
    # still renders as a valid 4-option MCQ.
    filler = ["None of the above", "All of the above", "Not covered in this video"]
    i = 0
    while len(distractors) < n and i < len(filler):
        if filler[i] not in distractors:
            distractors.append(filler[i])
        i += 1

    return distractors[:n]
