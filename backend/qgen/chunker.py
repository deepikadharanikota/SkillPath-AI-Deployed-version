"""
chunker.py
----------
Splits a raw transcript into semantically-sized chunks (~150-300 words,
sentence-boundary aware) that each stand alone well enough to generate one
or two questions from. This is what anchors generated questions to the
actual video content instead of the topic in general.
"""

import re


def _ensure_nltk_punkt():
    import nltk
    for pkg in ("punkt_tab", "punkt"):
        try:
            nltk.data.find(f"tokenizers/{pkg}")
            return
        except LookupError:
            continue
    nltk.download("punkt_tab", quiet=True)


def split_sentences(text: str) -> list[str]:
    """Sentence-tokenize `text`. Falls back to a regex splitter if NLTK's
    punkt data isn't available (e.g. no network to download it)."""
    try:
        _ensure_nltk_punkt()
        from nltk.tokenize import sent_tokenize
        return [s.strip() for s in sent_tokenize(text) if s.strip()]
    except Exception:
        # Regex fallback: split on sentence-ending punctuation followed by
        # whitespace + a capital letter. Not perfect, but dependency-free.
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
        return [s.strip() for s in parts if s.strip()]


def chunk_transcript(text: str, target_words: int = 220, min_words: int = 80) -> list[str]:
    """
    Groups sentences into chunks of roughly `target_words` words each,
    without splitting a sentence across chunks. The last chunk is merged
    into the previous one if it's too short to stand alone.
    """
    sentences = split_sentences(text)
    chunks: list[str] = []
    current: list[str] = []
    current_words = 0

    for sent in sentences:
        n = len(sent.split())
        if current and current_words + n > target_words:
            chunks.append(" ".join(current))
            current, current_words = [], 0
        current.append(sent)
        current_words += n

    if current:
        chunk_text = " ".join(current)
        if chunks and len(chunk_text.split()) < min_words:
            chunks[-1] = chunks[-1] + " " + chunk_text
        else:
            chunks.append(chunk_text)

    return chunks
