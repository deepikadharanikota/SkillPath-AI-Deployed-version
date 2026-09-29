"""
qgen
----
AI-generated quiz question pipeline for SkillPath AI.

Replaces the static QUIZ_BANK in data.py with questions generated from the
actual video transcripts of each course module, using a local/offline NLP
stack (no LLM API, no per-question cost):

    transcript_fetcher.py  -> pull captions for a VIDEO_DB entry
    chunker.py             -> split transcript into semantic chunks
    answer_extractor.py    -> find candidate "facts" (answers) per chunk
    question_generator.py  -> T5 question-generation model (+ rule-based
                               fallback when the model/network isn't available)
    difficulty.py           -> label each question easy / medium / hard
    distractors.py          -> build wrong MCQ options
    cache.py                -> persist generated questions to disk, keyed
                               the same way QUIZ_BANK is keyed today
    pipeline.py              -> orchestrates all of the above end-to-end

See generate_quiz_bank.py for the offline batch-generation entry point,
and main.py's go_to_quiz() for how the generated bank is consumed at
runtime (falls back to the static QUIZ_BANK if nothing has been
generated for a topic yet).
"""
