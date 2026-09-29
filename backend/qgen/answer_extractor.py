"""
answer_extractor.py
--------------------
Finds candidate "answers" (facts worth quizzing on) inside a transcript
chunk: noun phrases and technical terms. These become both (a) the answer
the question-generator is told to ask about, and (b) raw material for
distractor generation later.
"""

import re

_STOPWORDS = {
    "the", "a", "an", "this", "that", "these", "those", "is", "are", "was",
    "were", "it", "its", "we", "you", "they", "i", "he", "she", "so", "of",
    "to", "and", "or", "in", "on", "for", "with", "as", "be", "at", "by",
    "from", "your", "our", "their", "his", "her", "not", "just", "like",
    "okay", "right", "now", "here", "there", "um", "uh",
}


def _ensure_nltk_pos():
    import nltk
    for pkg, path in [
        ("averaged_perceptron_tagger_eng", "taggers/averaged_perceptron_tagger_eng"),
        ("averaged_perceptron_tagger", "taggers/averaged_perceptron_tagger"),
    ]:
        try:
            nltk.data.find(path)
            return
        except LookupError:
            continue
    nltk.download("averaged_perceptron_tagger_eng", quiet=True)


def _noun_phrases_pos(sentence: str) -> list[str]:
    """POS-tag based noun-phrase extraction (proper NLP path)."""
    import nltk
    _ensure_nltk_pos()
    words = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(words)

    phrases, current = [], []
    for word, tag in tagged:
        if tag.startswith("NN") or tag in ("JJ",):
            current.append(word)
        else:
            if len(current) >= 1:
                phrases.append(" ".join(current))
            current = []
    if current:
        phrases.append(" ".join(current))

    return [p for p in phrases if p.lower() not in _STOPWORDS and len(p) > 2]


def _noun_phrases_regex(sentence: str) -> list[str]:
    """Dependency-free fallback: capitalized terms and CamelCase/technical
    tokens (e.g. 'NumPy', 'Neural Network') plus longer lowercase words as
    a last resort, used only if NLTK's POS tagger can't be downloaded."""
    candidates = re.findall(r"\b[A-Z][a-zA-Z0-9]*(?:\s[A-Z][a-zA-Z0-9]*)*\b", sentence)
    if not candidates:
        words = [w.strip(".,!?;:()\"'") for w in sentence.split()]
        candidates = [w for w in words if len(w) > 5 and w.lower() not in _STOPWORDS]
    return candidates


def extract_candidate_answers(chunk: str, max_candidates: int = 8) -> list[dict]:
    """
    Returns a list of {"answer": str, "sentence": str} — each a candidate
    fact from the chunk, paired with the sentence it came from (the
    question generator needs that surrounding context).
    """
    sentences = re.split(r"(?<=[.!?])\s+", chunk)
    candidates = []
    seen = set()

    for sent in sentences:
        if len(sent.split()) < 4:
            continue
        try:
            phrases = _noun_phrases_pos(sent)
        except Exception:
            phrases = _noun_phrases_regex(sent)

        for phrase in phrases:
            key = phrase.lower()
            if key in seen or len(phrase) < 3:
                continue
            seen.add(key)
            candidates.append({"answer": phrase, "sentence": sent.strip()})

    return candidates[:max_candidates]
