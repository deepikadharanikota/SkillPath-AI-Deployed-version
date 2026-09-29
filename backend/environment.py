"""
environment.py
---------------
Defines the RL problem for SkillPath AI: state representation, the action
space (which topic + difficulty to recommend next), and the reward signal.
This replaces the hand-written if/else "adaptDifficulty" logic in the old
agentUtils.js with an actual Markov Decision Process that the DQNAgent
learns to act in.

STATE  (12-dim vector):
    [mastery_0 .. mastery_7]   -- current mastery (0-1) for each of the 8 topics
    [recent_0, recent_1, recent_2]  -- last 3 quiz scores (0-1), oldest first
    [fatigue]                  -- session fatigue signal (0-1)

ACTION (24 discrete actions):
    action = topic_index * len(DIFFICULTIES) + difficulty_index
    i.e. "recommend this topic, at this difficulty, next"

REWARD:
    Combines quiz/code performance, mastery gained, how well the
    recommended topic matched what the learner needed, and a fatigue
    penalty -- same shape as the product's original design intent, but
    now the thing that decided the action is the network being trained
    on this reward, not a hardcoded threshold.
"""

import numpy as np

TOPICS = [
    "Python", "Machine Learning", "Deep Learning", "Statistics",
    "NLP", "Computer Vision", "MLOps", "Data Engineering", "DevOps"
]

DIFFICULTIES = ["beginner", "intermediate", "advanced"]

STATE_DIM = len(TOPICS) + 3 + 1  # mastery vector + 3 recent scores + fatigue
ACTION_DIM = len(TOPICS) * len(DIFFICULTIES)


def encode_action(topic: str, difficulty: str) -> int:
    return TOPICS.index(topic) * len(DIFFICULTIES) + DIFFICULTIES.index(difficulty)


def decode_action(action: int):
    topic_idx, diff_idx = divmod(int(action), len(DIFFICULTIES))
    return TOPICS[topic_idx], DIFFICULTIES[diff_idx]


def build_state(topic_mastery: dict, recent_scores: list, fatigue: float) -> np.ndarray:
    """
    topic_mastery: {topic_name: 0..1}
    recent_scores: list of the last (up to 3) quiz scores, each 0..100
    fatigue: 0..1
    """
    mastery_vec = [float(topic_mastery.get(t, 0.0)) for t in TOPICS]

    scores = [s / 100.0 for s in recent_scores[-3:]]
    while len(scores) < 3:
        scores.insert(0, 0.0)

    state = np.array(mastery_vec + scores + [float(fatigue)], dtype=np.float64)
    assert state.shape[0] == STATE_DIM
    return state


def compute_reward(
    quiz_score: float,      # 0-100
    code_score: float,      # 0-100
    mastery_gain: float,    # 0-1, how much mastery increased on the studied topic
    fatigue: float,         # 0-1
    topic_alignment: float, # 0-1, how well the recommended topic matched the
                             # learner's weakest/most relevant gap
) -> float:
    perf = (quiz_score + code_score) / 200.0
    reward = perf * 0.4 + mastery_gain * 0.3 + topic_alignment * 0.2 - fatigue * 0.1
    return float(np.clip(reward, -1.0, 1.0))


def topic_alignment_score(recommended_topic: str, topic_mastery: dict) -> float:
    """
    Reward-shaping helper: recommending a topic the learner is weak in
    (low mastery) is more aligned with the goal of closing skill gaps than
    recommending something already mastered. Returns 0..1.
    """
    mastery = float(topic_mastery.get(recommended_topic, 0.0))
    return float(np.clip(1.0 - mastery, 0.0, 1.0))
