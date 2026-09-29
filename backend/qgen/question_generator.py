"""
question_generator.py
-----------------------
Turns a (candidate answer, source sentence) pair into an actual quiz
question, using a local T5 model fine-tuned for answer-aware question
generation.

Two backends:
  - T5QuestionGenerator: the real thing (iarfmoose/t5-base-question-
    generator via HuggingFace `transformers`). Needs `pip install
    transformers torch` and a one-time model download (~850MB, requires
    internet the first time it runs; cached locally by HuggingFace after
    that).
  - ClozeQuestionGenerator: a dependency-free rule-based fallback that
    blanks out the answer term in its source sentence. Lower quality, but
    works with zero downloads/network — used automatically if the T5
    model can't be loaded (e.g. no internet, no `transformers` installed).

`get_question_generator()` picks whichever backend is actually usable.
"""

from abc import ABC, abstractmethod


class QuestionGenerator(ABC):
    @abstractmethod
    def generate(self, answer: str, context_sentence: str) -> str:
        """Return a question string whose answer is `answer`, grounded in
        `context_sentence` (drawn from the video transcript)."""
        raise NotImplementedError


class T5QuestionGenerator(QuestionGenerator):
    """Wraps iarfmoose/t5-base-question-generator. This is the model that
    actually reads the video's transcript sentence and writes a natural
    question about it — this is the 'AI-generated, not static' part."""

    MODEL_NAME = "iarfmoose/t5-base-question-generator"

    def __init__(self):
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.MODEL_NAME)

    def generate(self, answer: str, context_sentence: str, max_length: int = 64) -> str:
        # Input format this model was fine-tuned on: "answer: <answer>  context: <context> </s>"
        input_text = f"answer: {answer}  context: {context_sentence} </s>"
        features = self.tokenizer([input_text], return_tensors="pt", truncation=True)
        output_ids = self.model.generate(
            input_ids=features["input_ids"],
            attention_mask=features["attention_mask"],
            max_length=max_length,
            num_beams=4,
        )
        question = self.tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
        if question and not question.endswith("?"):
            question += "?"
        return question


class ClozeQuestionGenerator(QuestionGenerator):
    """Dependency-free fallback: blanks out the answer term in its source
    sentence and asks the learner to identify it. Lower quality than the
    T5 model but requires no downloads, so the pipeline still works
    end-to-end (e.g. for testing, or if the model can't be fetched)."""

    def generate(self, answer: str, context_sentence: str) -> str:
        blanked = context_sentence.replace(answer, "ـ" * min(len(answer), 8), 1)
        blanked = blanked.replace("ـ" * min(len(answer), 8), "_____", 1)
        if answer not in context_sentence:
            blanked = context_sentence
        return f"Fill in the blank based on the video: \"{blanked}\""


def get_question_generator() -> QuestionGenerator:
    """Tries to load the real T5 model; falls back to the cloze generator
    if the model/network/torch isn't available."""
    try:
        return T5QuestionGenerator()
    except Exception:
        return ClozeQuestionGenerator()
