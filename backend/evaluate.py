"""
evaluate.py
-----------
Evaluation harness for the SkillPath AI DQN. Answers the two questions
that actually matter for an RL system:

  1. Did training converge? (reward, loss, epsilon over time)
  2. Does the trained policy beat sane baselines? (greedy DQN vs random,
     vs a naive round-robin schedule, vs a simple heuristic rule)

Everything runs against `SimulatedLearner` (the same simulator
`train_offline.py` trains on), using matched random seeds across
policies so comparisons are apples-to-apples.

Usage:
    python evaluate.py                              # evaluate existing dqn_weights.pkl
    python evaluate.py --retrain --episodes 300      # retrain with full logging, then evaluate
    python evaluate.py --eval-episodes 300           # more evaluation episodes = tighter estimates

Outputs:
    metrics/training_curves.png   (if --retrain)
    metrics/policy_comparison.png
    metrics/summary.json
    A printed console report
"""

import argparse
import json
import os
import random as pyrandom

import numpy as np

from dqn_agent import DQNAgent, ALGORITHM_VERSION
from environment import STATE_DIM, ACTION_DIM, TOPICS, DIFFICULTIES, encode_action
from simulated_learner import SimulatedLearner

OUT_DIR = os.path.join(os.path.dirname(__file__), "metrics")
WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "dqn_weights.pkl")


# ─────────────────────────────────────────────────────────────────────────
# 1. Training diagnostics — reward / loss / epsilon / PER beta over time
# ─────────────────────────────────────────────────────────────────────────
def train_with_logging(episodes=300, max_steps=12, seed=42, save_path=WEIGHTS_PATH):
    print(f"Training {ALGORITHM_VERSION} agent for {episodes} episodes...")
    agent = DQNAgent(state_dim=STATE_DIM, action_dim=ACTION_DIM, seed=seed)
    env = SimulatedLearner(seed=seed)

    log = {"episode": [], "reward": [], "loss": [], "epsilon": [], "avg_quiz_score": [], "beta": []}

    for ep in range(1, episodes + 1):
        state = env.reset()
        total_reward, losses, quiz_scores = 0.0, [], []

        for _ in range(max_steps):
            action, _ = agent.act(state, explore=True)
            next_state, reward, done, info = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            loss = agent.replay()
            if loss is not None:
                losses.append(loss)
            quiz_scores.append(info["quiz_score"])
            state = next_state
            total_reward += reward
            if done:
                break

        log["episode"].append(ep)
        log["reward"].append(total_reward)
        log["loss"].append(float(np.mean(losses)) if losses else np.nan)
        log["epsilon"].append(agent.epsilon)
        log["avg_quiz_score"].append(float(np.mean(quiz_scores)))
        log["beta"].append(agent.replay_buffer.beta)

        if ep % 20 == 0 or ep == 1:
            avg_r = float(np.mean(log["reward"][-20:]))
            cur_loss = log['loss'][-1] if not np.isnan(log['loss'][-1]) else 0.0
            print(f"episode {ep:4d} | avg_reward(last20)={avg_r:+.3f} "
                  f"| loss={cur_loss:.4f} | epsilon={agent.epsilon:.3f} "
                  f"| PER_beta={agent.replay_buffer.beta:.3f} | buffer={len(agent.replay_buffer)}")

    agent.save(save_path)
    print(f"\nSaved trained {ALGORITHM_VERSION} weights to {save_path}")
    return agent, log


def plot_training_curves(log, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ep = log["episode"]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))

    def smooth(vals, window=10):
        vals = np.array(vals, dtype=np.float64)
        if len(vals) < window:
            return vals
        kernel = np.ones(window) / window
        return np.convolve(vals, kernel, mode="valid")

    axes[0, 0].plot(ep, log["reward"], alpha=0.3, color="tab:blue")
    sm = smooth(log["reward"])
    axes[0, 0].plot(ep[-len(sm):], sm, color="tab:blue", label="10-ep moving avg")
    axes[0, 0].set_title("Episode reward")
    axes[0, 0].set_xlabel("episode")
    axes[0, 0].legend()

    axes[0, 1].plot(ep, log["loss"], color="tab:red")
    axes[0, 1].set_title("Training loss (MSE, per replay step)")
    axes[0, 1].set_xlabel("episode")

    axes[1, 0].plot(ep, log["epsilon"], color="tab:green")
    axes[1, 0].set_title("Epsilon (exploration rate)")
    axes[1, 0].set_xlabel("episode")

    axes[1, 1].plot(ep, log["avg_quiz_score"], alpha=0.3, color="tab:purple")
    sm2 = smooth(log["avg_quiz_score"])
    axes[1, 1].plot(ep[-len(sm2):], sm2, color="tab:purple", label="10-ep moving avg")
    axes[1, 1].set_title("Avg simulated quiz score per episode")
    axes[1, 1].set_xlabel("episode")
    axes[1, 1].legend()

    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────
# 2. Baseline policies to compare the trained DQN against
# ─────────────────────────────────────────────────────────────────────────
def policy_dqn(agent):
    def _act(state, env, step_idx):
        action, _ = agent.act(state, explore=False)
        return action
    return _act


def policy_random():
    def _act(state, env, step_idx):
        return pyrandom.randrange(ACTION_DIM)
    return _act


def policy_round_robin_beginner():
    """Naive baseline: cycle through topics in a fixed order, always
    'beginner' difficulty — no adaptation at all."""
    def _act(state, env, step_idx):
        topic = TOPICS[step_idx % len(TOPICS)]
        return encode_action(topic, "beginner")
    return _act


def policy_rule_based():
    """Heuristic baseline: recommend the topic the learner is currently
    weakest in, at a difficulty matched to their mastery level. This is
    the kind of hand-written if/else rule the DQN is meant to improve on."""
    def _act(state, env, step_idx):
        topic = min(TOPICS, key=lambda t: env.mastery[t])
        mastery = env.mastery[topic]
        difficulty = "beginner" if mastery < 0.35 else "intermediate" if mastery < 0.7 else "advanced"
        return encode_action(topic, difficulty)
    return _act


POLICIES = {
    "dqn_greedy": policy_dqn,
    "random": lambda: policy_random(),
    "round_robin_beginner": lambda: policy_round_robin_beginner(),
    "rule_based_weakest_topic": lambda: policy_rule_based(),
}


def run_policy(policy_fn, episodes, max_steps=12, seed_offset=1000):
    """Runs `episodes` fixed-length episodes, re-seeding SimulatedLearner
    identically for every policy (seed = seed_offset + episode_index) so
    all policies face the exact same sequence of underlying learners."""
    ep_rewards, quiz_scores, code_scores, topic_diversity = [], [], [], []

    for i in range(episodes):
        env = SimulatedLearner(seed=seed_offset + i)
        state = env.reset()
        total_reward = 0.0
        topics_seen = set()
        ep_quiz, ep_code = [], []

        for step_idx in range(max_steps):
            action = policy_fn(state, env, step_idx)
            topic = TOPICS[action // len(DIFFICULTIES)]
            topics_seen.add(topic)

            next_state, reward, done, info = env.step(action)
            ep_quiz.append(info["quiz_score"])
            ep_code.append(info["code_score"])
            total_reward += reward
            state = next_state
            if done:
                break

        ep_rewards.append(total_reward)
        quiz_scores.append(float(np.mean(ep_quiz)))
        code_scores.append(float(np.mean(ep_code)))
        topic_diversity.append(len(topics_seen))

    return {
        "avg_episode_reward": float(np.mean(ep_rewards)),
        "std_episode_reward": float(np.std(ep_rewards)),
        "avg_quiz_score": float(np.mean(quiz_scores)),
        "avg_code_score": float(np.mean(code_scores)),
        "avg_topic_diversity": float(np.mean(topic_diversity)),
        "episodes": episodes,
        "_episode_rewards": ep_rewards,  # kept for paired significance testing
    }


def paired_bootstrap_ci(rewards_a, rewards_b, n_boot=5000, seed=0):
    """95% bootstrap CI for mean(rewards_a - rewards_b), using the fact
    that both lists came from matched seeds (same underlying learner
    sequence), so a simple paired difference is valid."""
    rng = np.random.default_rng(seed)
    diffs = np.array(rewards_a) - np.array(rewards_b)
    n = len(diffs)
    boot_means = np.array([
        rng.choice(diffs, size=n, replace=True).mean() for _ in range(n_boot)
    ])
    lo, hi = np.percentile(boot_means, [2.5, 97.5])
    return float(diffs.mean()), float(lo), float(hi)


def plot_policy_comparison(results, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = list(results.keys())
    rewards = [results[n]["avg_episode_reward"] for n in names]
    reward_err = [results[n]["std_episode_reward"] for n in names]
    quiz = [results[n]["avg_quiz_score"] for n in names]
    diversity = [results[n]["avg_topic_diversity"] for n in names]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))

    axes[0].bar(names, rewards, yerr=reward_err, color="tab:blue", capsize=4)
    axes[0].set_title("Avg episode reward")
    axes[0].tick_params(axis="x", rotation=25)

    axes[1].bar(names, quiz, color="tab:purple")
    axes[1].set_title("Avg simulated quiz score")
    axes[1].tick_params(axis="x", rotation=25)

    axes[2].bar(names, diversity, color="tab:orange")
    axes[2].set_title("Avg distinct topics/episode (of 8)")
    axes[2].tick_params(axis="x", rotation=25)

    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--retrain", action="store_true", help="retrain from scratch with full logging first")
    parser.add_argument("--episodes", type=int, default=300, help="training episodes (only used with --retrain)")
    parser.add_argument("--eval-episodes", type=int, default=200, help="evaluation episodes per policy")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    if args.retrain:
        print(f"=== Training for {args.episodes} episodes (with full logging) ===")
        agent, log = train_with_logging(episodes=args.episodes, seed=args.seed)
        plot_training_curves(log, os.path.join(OUT_DIR, "training_curves.png"))
        print(f"Saved training_curves.png")
    else:
        agent = DQNAgent(state_dim=STATE_DIM, action_dim=ACTION_DIM, seed=args.seed)
        if os.path.exists(WEIGHTS_PATH):
            agent.load(WEIGHTS_PATH)
            print(f"Loaded existing weights from {WEIGHTS_PATH} (epsilon={agent.epsilon:.3f}, "
                  f"train_steps={agent._train_steps})")
        else:
            print("No dqn_weights.pkl found — evaluating an UNTRAINED agent. "
                  "Run with --retrain for a meaningful comparison.")

    print(f"\n=== Evaluating {args.eval_episodes} episodes per policy (greedy, matched seeds) ===")
    results = {}
    for name, factory in POLICIES.items():
        policy_fn = factory(agent) if name == "dqn_greedy" else factory()
        results[name] = run_policy(policy_fn, args.eval_episodes)
        r = results[name]
        print(f"{name:26s} | reward={r['avg_episode_reward']:+.3f} ± {r['std_episode_reward']:.3f}"
              f" | quiz={r['avg_quiz_score']:5.1f}% | topic_diversity={r['avg_topic_diversity']:.1f}/8")

    plot_policy_comparison(results, os.path.join(OUT_DIR, "policy_comparison.png"))

    print("\n=== Paired comparison vs dqn_greedy (95% bootstrap CI on mean reward diff) ===")
    dqn_rewards = results["dqn_greedy"]["_episode_rewards"]
    paired = {}
    for name in POLICIES:
        if name == "dqn_greedy":
            continue
        mean_diff, lo, hi = paired_bootstrap_ci(dqn_rewards, results[name]["_episode_rewards"])
        significant = lo > 0 or hi < 0
        verdict = ("DQN better" if mean_diff > 0 else "DQN worse") if significant else "no significant difference"
        paired[name] = {"mean_diff": mean_diff, "ci_95": [lo, hi], "significant": significant}
        print(f"dqn_greedy vs {name:26s} | diff={mean_diff:+.4f}  95% CI=[{lo:+.4f}, {hi:+.4f}]  -> {verdict}")

    # Strip the raw per-episode arrays before serializing
    summary_for_json = {
        name: {k: v for k, v in r.items() if not k.startswith("_")}
        for name, r in results.items()
    }
    summary_for_json["paired_vs_dqn_greedy"] = paired

    with open(os.path.join(OUT_DIR, "summary.json"), "w") as f:
        json.dump(summary_for_json, f, indent=2)

    dqn_r = results["dqn_greedy"]["avg_episode_reward"]
    best_baseline = max(
        (v["avg_episode_reward"] for k, v in results.items() if k != "dqn_greedy")
    )
    print(f"\nDQN vs best baseline reward: {dqn_r:+.3f} vs {best_baseline:+.3f} "
          f"({'+' if dqn_r > best_baseline else ''}{(dqn_r - best_baseline):.3f})")
    print(f"\nSaved: {OUT_DIR}/policy_comparison.png, {OUT_DIR}/summary.json")


if __name__ == "__main__":
    main()
