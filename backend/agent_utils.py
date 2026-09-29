"""
agent_utils.py
--------------
Direct Python port of `my-app/src/utils/agentUtils.js`. Handles:

  - Extracting skills from resume text
  - Estimating skill knowledge from resume signals
  - Building skill/state vectors
  - Computing reward (kept in sync with environment.compute_reward)
  - Simple threshold-based difficulty adaptation (used as a fallback /
    sanity check alongside the trained DQNAgent's own action choice)
  - Module progress helpers
  - Topic knowledge estimation for the dashboard

No JavaScript, no browser APIs — everything the old utils/agentUtils.js
did is done here in plain Python.
"""

import re

from data import SKILLS_DB, TOPICS, MODULE_KEYS
from environment import compute_reward as _env_compute_reward


# ─── Skill extraction from resume text ────────────────────────────────────
def extract_skills_from_text(text: str) -> list:
    text = text or ""
    lower = text.lower()
    found = [s for s in SKILLS_DB if s.lower() in lower]
    return found if found else ["Python", "Machine Learning", "NumPy"]


# ─── Estimate how much a user knows about each skill ──────────────────────
def estimate_skill_knowledge(text: str, skills: list) -> dict:
    lower = (text or "").lower()
    estimates = {}
    for skill in skills:
        skill_lower = skill.lower()
        occurrences = len(re.findall(re.escape(skill_lower), lower))

        idx = lower.find(skill_lower)
        window = text[max(0, idx - 80): idx + 80] if idx != -1 else ""
        has_years = bool(re.search(r"\d+\s*\+?\s*years?", window, re.IGNORECASE))
        has_projects = "project" in lower or "built" in lower or "developed" in lower
        has_cert = "certified" in lower or "certification" in lower

        score = 0.0
        if occurrences >= 3:
            score += 0.35
        elif occurrences == 2:
            score += 0.2
        elif occurrences == 1:
            score += 0.1
        if has_years:
            score += 0.25
        if has_projects:
            score += 0.15
        if has_cert:
            score += 0.1

        # Cap at 0.85 — nobody knows everything from a resume
        estimates[skill] = min(0.85, score)
    return estimates


# ─── Build skill vector ────────────────────────────────────────────────────
def build_skill_vector(skills: list) -> list:
    return [1 if s in skills else 0 for s in SKILLS_DB]


# ─── Compute reward ─────────────────────────────────────────────────────────
# quiz_score: 0-100, code_score: 0-100, mastery_gain: 0-1, fatigue: 0-1,
# topic_alignment: 0-1
# Delegates to environment.compute_reward so there is exactly one
# implementation of the reward function shared by the dashboard/UI code
# and the DQN training loop.
def compute_reward(quiz_score, code_score, mastery_gain, fatigue, topic_alignment) -> float:
    return _env_compute_reward(quiz_score, code_score, mastery_gain, fatigue, topic_alignment)


# ─── DQN Difficulty Adaptation Logic (rule-based fallback) ─────────────────
# The trained DQNAgent (see dqn_agent.py / environment.py) is the real
# decision-maker in recommender.py. This threshold rule is kept as a
# simple, explainable fallback/sanity-check, exactly mirroring the
# original adaptDifficulty() in agentUtils.js.
def adapt_difficulty(topic: str, history: list, current_difficulty: str) -> str:
    topic_history = [h for h in history if h["topic"] == topic][-3:]

    if len(topic_history) < 3:
        return current_difficulty  # Not enough data yet

    avg_score = sum(h["quizScore"] for h in topic_history) / len(topic_history)
    difficulties = ["beginner", "intermediate", "advanced"]
    current_idx = difficulties.index(current_difficulty)

    if avg_score >= 80 and current_idx < 2:
        return difficulties[current_idx + 1]
    elif avg_score < 50 and current_idx > 0:
        return difficulties[current_idx - 1]
    return current_difficulty


# ─── Module progress helpers ────────────────────────────────────────────────
def get_module_status(module_progress: dict, topic: str) -> dict:
    progress = module_progress.get(topic, {})
    return {m: progress.get(m, "locked") for m in MODULE_KEYS}


def get_next_module(module_progress: dict, topic: str):
    status = get_module_status(module_progress, topic)
    for m in MODULE_KEYS:
        if status.get(m) != "completed":
            return m
    return None  # All done


def is_topic_complete(module_progress: dict, topic: str) -> bool:
    return get_next_module(module_progress, topic) is None


# ─── Estimate topic knowledge from resume + completed quizzes ──────────────
_RELATED_SKILLS = {
    "Python": ["Python"],
    "Machine Learning": ["Machine Learning", "TensorFlow", "PyTorch", "Scikit-learn"],
    "Deep Learning": ["Deep Learning", "TensorFlow", "PyTorch"],
    "Statistics": ["Statistics", "Linear Algebra"],
    "NLP": ["NLP"],
    "Computer Vision": ["Computer Vision"],
    "MLOps": ["Docker", "Kubernetes", "Git", "AWS", "FastAPI"],
    "Data Engineering": ["SQL", "Spark", "Scala", "Pandas"],
}


def compute_topic_knowledge(topic, extracted_skills, module_progress, quiz_history) -> float:
    related = _RELATED_SKILLS.get(topic, [])
    match_count = len([s for s in related if s in extracted_skills])
    base = (match_count / len(related)) * 0.3 if related else 0.0

    status = get_module_status(module_progress, topic)
    completed_modules = len([m for m in MODULE_KEYS if status.get(m) == "completed"])

    topic_quizzes = [h for h in quiz_history if h["topic"] == topic]
    avg_quiz_score = (
        sum(h["quizScore"] for h in topic_quizzes) / len(topic_quizzes)
        if topic_quizzes else 0.0
    )

    module_boost = (completed_modules / max(len(MODULE_KEYS), 1)) * (avg_quiz_score / 100) * 0.7

    return min(1.0, base + module_boost)
