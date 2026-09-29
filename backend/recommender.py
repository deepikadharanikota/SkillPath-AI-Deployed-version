"""
recommender.py
---------------
Replaces `my-app/src/utils/apiUtils.js`. The old JS file's job was to call
an LLM from the browser and ask it to *pretend* to be a DQN ("Return ONLY
valid JSON: {topic, difficulty, ...}"), with a hardcoded fallback used
whenever that call failed (which, running client-side with no API key,
it always did in practice).

This module removes the LLM role-play entirely. The actual trained
DQNAgent (dqn_agent.py) — a real neural network with real backpropagation,
epsilon-greedy exploration, and experience replay — makes every
topic/difficulty decision. This file just:

  1. Builds the state vector for the agent (via environment.build_state)
  2. Asks the agent to act
  3. Wraps the agent's decision in a friendly, templated explanation for
     the learner, in the same spirit as the old prompt's requested output
     shape (topic, difficulty, strategy, explanation, encouragement)

No network calls, no external LLM dependency required to run the app.
"""

import random

from data import TOPICS
from environment import build_state, decode_action, encode_action
from agent_utils import compute_topic_knowledge, adapt_difficulty


_STRATEGY_EXPLANATIONS = {
    "gap-filling": "This fills a skill gap your target role needs — closing it moves you closer to being job-ready.",
    "skill-reinforcement": "You've already got some background here — let's turn that into real depth.",
    "progression": "You're on a roll in this subject — let's keep the momentum going.",
    "review": "A quick pass over this will lock in what you've already learned.",
    "reinforcement": "Let's reinforce this topic before moving on, so it really sticks.",
}

_ENCOURAGEMENTS = [
    "Every lesson makes you better. 💪",
    "You've got this — one module at a time.",
    "Small steps, big progress. Keep going!",
    "Consistency beats intensity. Nice work showing up.",
    "You're closer to your goal than you were yesterday.",
]


def _pick_strategy(topic, extracted_skills, role_skills):
    if topic not in extracted_skills and topic in role_skills:
        return "gap-filling"
    if topic in extracted_skills:
        return "skill-reinforcement"
    return "progression"


# ─── Initial learning plan (first recommendation, before any quiz data) ───
def get_initial_recommendation(agent, target_role, extracted_skills, role_skills):
    gaps = [s for s in role_skills if s not in extracted_skills]

    # Seed topic mastery purely from resume-derived skill overlap
    topic_mastery = {
        t: compute_topic_knowledge(t, extracted_skills, {}, [])
        for t in TOPICS
    }
    state = build_state(topic_mastery, [], 0.0)
    action, q_values = agent.act(state, explore=False)
    _, difficulty = decode_action(action) # Keep DQN's difficulty choice, but we will override topic

    # Force the initial topic to align with the target role and skill gaps
    from data import ROLE_TO_TOPIC
    
    # 1. Fallback to the configured primary topic for this role
    topic = ROLE_TO_TOPIC.get(target_role)
    
    # 2. Or, if the role isn't mapped, fallback to a sensible default
    if not topic:
        topic = "Machine Learning"

    strategy = _pick_strategy(topic, extracted_skills, role_skills)
    explanation = (
        f"Based on your resume, {topic} looks like the best place to start "
        f"for a {target_role} — {_STRATEGY_EXPLANATIONS.get(strategy, 'this sets a strong foundation.')}"
    )

    return {
        "topic": topic,
        "difficulty": difficulty,
        "strategy": strategy,
        "explanation": explanation,
        "skill_gaps": gaps[:3],
        "estimated_modules": 3,
        "q_values": q_values.tolist(),
        "state": state.tolist(),
        "encoded_action": encode_action(topic, difficulty),
    }


# ─── Next topic/module recommendation after completing a module ──────────
def get_next_recommendation(
    agent,
    target_role,
    completed_topic,
    completed_module,
    quiz_score,
    code_score,
    difficulty,
    topic_mastery,
    recent_history,
    fatigue,
):
    recent_scores = [h["quizScore"] for h in recent_history[-3:]]
    state = build_state(topic_mastery, recent_scores, fatigue)
    action, q_values = agent.act(state, explore=False)
    topic, agent_difficulty = decode_action(action)

    # Blend the agent's difficulty choice with the simple, explainable
    # threshold rule — if they disagree, trust the explainable rule (it's
    # directly tied to *this* topic's last 3 scores, which the agent's
    # global state vector only partially captures).
    rule_difficulty = adapt_difficulty(completed_topic, recent_history, difficulty)
    final_difficulty = rule_difficulty if topic == completed_topic else agent_difficulty

    strategy = (
        "progression" if topic == completed_topic
        else "reinforcement" if topic in [h["topic"] for h in recent_history]
        else "gap-filling"
    )

    if topic == completed_topic:
        explanation = "You're making good progress here — let's keep building on it."
    else:
        explanation = f"Time to switch things up — {topic} needs some attention next."

    encouragement = random.choice(_ENCOURAGEMENTS)

    return {
        "action": "continue_topic" if topic == completed_topic else "switch_topic",
        "topic": topic,
        "difficulty": final_difficulty,
        "strategy": strategy,
        "explanation": explanation,
        "encouragement": encouragement,
        "q_values": q_values.tolist(),
        "state": state.tolist(),
        "encoded_action": encode_action(topic, final_difficulty),
    }


# ─── Evaluate a code submission (heuristic — no LLM required) ─────────────
_TOPIC_KEYWORDS = {
    "Python": ["def ", "class ", "for ", "if ", "return"],
    "Machine Learning": ["fit(", "predict(", "sklearn", "train_test_split", "model"],
    "Deep Learning": ["torch", "tensorflow", "keras", "nn.", "layer"],
    "Statistics": ["mean", "std", "scipy", "stats", "p-value", "confidence"],
    "NLP": ["token", "nltk", "spacy", "transformers", "tfidf", "tf-idf"],
    "Computer Vision": ["cv2", "opencv", "image", "conv", "pixel"],
    "MLOps": ["docker", "flask", "mlflow", "pipeline", "deploy"],
    "Data Engineering": ["pandas", "spark", "etl", "csv", "dataframe"],
}


def evaluate_code(code: str, topic: str, difficulty: str, module_key: str) -> dict:
    code = code or ""
    stripped = code.strip()
    if not stripped:
        return {"score": 0, "feedback": "No code submitted.", "strengths": "", "improvements": ""}

    lower = stripped.lower()
    keywords = _TOPIC_KEYWORDS.get(topic, [])
    keyword_hits = sum(1 for kw in keywords if kw.lower() in lower)

    has_comment = "#" in stripped
    length_score = min(1.0, len(stripped) / 200.0)
    keyword_score = min(1.0, keyword_hits / max(1, len(keywords) // 2 or 1))

    score = round(35 + length_score * 25 + keyword_score * 30 + (10 if has_comment else 0))
    score = max(10, min(100, score))

    if score >= 80:
        feedback = "Great work — this clearly demonstrates the concept."
        strengths = "Good use of the relevant tools/keywords for this topic."
    elif score >= 55:
        feedback = "Solid attempt — you're on the right track."
        strengths = "Code submitted and touches on the right ideas."
    else:
        feedback = "Good effort! Keep practicing — try to use more of the topic's core tools."
        strengths = "You gave it a try, which is the important part."

    improvements = (
        "Add a few comments to explain your logic." if not has_comment
        else "Try expanding this with a bit more detail or an extra example."
    )

    return {
        "score": score,
        "feedback": feedback,
        "strengths": strengths,
        "improvements": improvements,
    }
