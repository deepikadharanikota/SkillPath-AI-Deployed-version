"""
simulated_learner.py
---------------------
A lightweight simulated "learner" used to pretrain the DQN offline before
it ever meets a real user, so the agent isn't starting from pure random
noise on day one. This is standard RL practice (train in a simulator,
fine-tune online with real interaction data via /api/feedback).

The simulation models a learner whose quiz/code performance depends on
how well the chosen difficulty matches their current mastery of the
recommended topic, and increases that topic's mastery a little each time
it's studied (with diminishing returns) and applies fatigue that builds
up over a session and resets between sessions.
"""

import numpy as np
from environment import (
    TOPICS, DIFFICULTIES, decode_action,
    build_state, compute_reward, topic_alignment_score,
)

DIFF_LEVEL = {"beginner": 0.2, "intermediate": 0.5, "advanced": 0.85}


class SimulatedLearner:
    def __init__(self, seed=None):
        self.rng = np.random.default_rng(seed)
        self.reset()

    def reset(self):
        # Random starting mastery per topic (mimics resume-derived priors)
        self.mastery = {t: float(self.rng.uniform(0.0, 0.3)) for t in TOPICS}
        self.recent_scores = []
        self.fatigue = 0.0
        self.steps_this_session = 0
        return self._state()

    def _state(self):
        return build_state(self.mastery, self.recent_scores, self.fatigue)

    def step(self, action: int):
        topic, difficulty = decode_action(action)
        target_level = DIFF_LEVEL[difficulty]
        current = self.mastery[topic]

        # Performance peaks when difficulty matches current mastery level;
        # too easy or too hard both hurt the score.
        gap = abs(target_level - current)
        base_perf = np.clip(1.0 - gap * 1.8, 0.05, 1.0)
        noise = self.rng.normal(0, 0.08)
        quiz_score = float(np.clip((base_perf + noise) * 100, 0, 100))
        code_score = float(np.clip((base_perf + self.rng.normal(0, 0.08)) * 100, 0, 100))

        # Mastery grows a bit, with diminishing returns, biased by performance
        gain = (base_perf * 0.08) * (1 - current)
        self.mastery[topic] = float(np.clip(current + gain, 0, 1))

        self.recent_scores.append(quiz_score)
        self.steps_this_session += 1
        self.fatigue = float(np.clip(self.steps_this_session / 12.0, 0, 1))

        alignment = topic_alignment_score(topic, self.mastery)
        reward = compute_reward(quiz_score, code_score, gain, self.fatigue, alignment)

        done = self.fatigue >= 1.0  # session ends when learner is worn out
        next_state = self._state()
        if done:
            self.reset()

        info = {"topic": topic, "difficulty": difficulty,
                 "quiz_score": quiz_score, "code_score": code_score}
        return next_state, reward, done, info
