"""
train_offline.py
-----------------
Runs a full Dueling Double DQN + Prioritized Experience Replay (PER) training loop
against the simulated learner and saves the trained weights to dqn_weights.pkl,
which the FastAPI backend loads on startup.

Usage:
    python train_offline.py --episodes 300
"""

import argparse
import numpy as np

from dqn_agent import DQNAgent, ALGORITHM_VERSION
from environment import STATE_DIM, ACTION_DIM
from simulated_learner import SimulatedLearner


def train(episodes=300, max_steps=12, seed=42, save_path="dqn_weights.pkl"):
    print(f"==================================================")
    print(f"RL Algorithm: {ALGORITHM_VERSION}")
    print(f"State Dim: {STATE_DIM} | Action Dim: {ACTION_DIM} | Target Episodes: {episodes}")
    print(f"==================================================")

    agent = DQNAgent(state_dim=STATE_DIM, action_dim=ACTION_DIM, seed=seed)
    env = SimulatedLearner(seed=seed)

    episode_rewards = []

    for ep in range(1, episodes + 1):
        state = env.reset()
        total_reward = 0.0
        losses = []

        for step in range(max_steps):
            action, q_vals = agent.act(state, explore=True)
            next_state, reward, done, info = env.step(action)

            agent.remember(state, action, reward, next_state, done)
            loss = agent.replay()
            if loss is not None:
                losses.append(loss)

            state = next_state
            total_reward += reward
            if done:
                break

        episode_rewards.append(total_reward)

        if ep % 20 == 0 or ep == 1:
            avg_reward = float(np.mean(episode_rewards[-20:]))
            avg_loss = float(np.mean(losses)) if losses else 0.0
            # Sample sample state to evaluate average predicted Q-value
            sample_state = env._state()
            q_est = agent.online_net.predict(sample_state)
            avg_q = float(np.mean(q_est))
            max_q = float(np.max(q_est))

            print(f"Episode {ep:4d}/{episodes} | "
                  f"Avg Reward (last 20): {avg_reward:+.3f} | "
                  f"Loss: {avg_loss:.4f} | "
                  f"Epsilon: {agent.epsilon:.3f} | "
                  f"PER Beta: {agent.replay_buffer.beta:.3f} | "
                  f"Avg Q: {avg_q:+.3f} | Max Q: {max_q:+.3f} | "
                  f"Buffer: {len(agent.replay_buffer)}")

    agent.save(save_path)
    print(f"\nSuccessfully saved trained {ALGORITHM_VERSION} weights to {save_path}")
    return agent


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=300)
    parser.add_argument("--save-path", type=str, default="dqn_weights.pkl")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    train(episodes=args.episodes, save_path=args.save_path, seed=args.seed)
