"""
difficulty.py
--------------
Labels a generated question as easy / medium / hard using two grounded
signals (not a model's opinion of itself):

  1. Question type — factual-recall question words (what/who/when/where)
     skew easy; reasoning words (why/how/compare) skew hard.
  2. Readability of the source sentence — Flesch-Kincaid grade level of
     the transcript sentence the question was built from. Denser,
     higher-grade-level source material makes for a harder question even
     when the question word itself is neutral (e.g. "which").

This keeps difficulty tied to measurable properties of the actual video
content, so it adapts per-video rather than being a fixed per-topic label
— and it uses the same easy/medium/hard labels main.py already expects,
so nothing downstream has to change.
"""

_EASY_STARTERS = ("what is", "what are", "who", "when", "where", "which of these", "name")
_HARD_STARTERS = ("why", "how does", "how do", "explain", "compare", "what happens if")


def _question_type_score(question: str) -> int:
    """0 = easy, 1 = medium, 2 = hard, based on the question's opening words."""
    q = question.strip().lower()
    if any(q.startswith(s) for s in _HARD_STARTERS):
        return 2
    if any(q.startswith(s) for s in _EASY_STARTERS):
        return 0
    return 1


def _readability_score(sentence: str) -> int:
    """0 = easy, 1 = medium, 2 = hard, based on Flesch-Kincaid grade level
    of the source sentence. Falls back to a simple word-length heuristic
    if `textstat` isn't installed."""
    try:
        import textstat
        grade = textstat.flesch_kincaid_grade(sentence)
    except Exception:
        words = sentence.split()
        avg_len = sum(len(w) for w in words) / max(1, len(words))
        grade = (avg_len - 4) * 2  # rough proxy, tuned to land in a similar range

    if grade < 7:
        return 0
    if grade < 11:
        return 1
    return 2


def classify_difficulty(question: str, context_sentence: str) -> str:
    combined = (_question_type_score(question) + _readability_score(context_sentence)) / 2
    if combined < 0.75:
        return "easy"
    if combined < 1.5:
        return "medium"
    return "hard"
