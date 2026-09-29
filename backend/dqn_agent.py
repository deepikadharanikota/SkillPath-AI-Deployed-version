"""
dqn_agent.py
------------
A Dueling Double Deep Q-Network with Prioritized Experience Replay (PER),
implemented from scratch in pure NumPy — real dual-stream forward pass,
exact analytic backpropagation with importance-sampling weighted Huber loss,
Double DQN target decoupling, binary SumTree prioritized sampling,
and target network synchronization.

Architecture:
  - Shared Feature Trunk:
      z1 = x @ W1 + b1, a1 = ReLU(z1)      (state_dim -> 64)
      z2 = a1 @ W2 + b2, a2 = ReLU(z2)     (64 -> 64)
  - Value Stream V(s):
      V(s) = a2 @ WV + bV                  (64 -> 1)
  - Advantage Stream A(s, a):
      A(s, a) = a2 @ WA + bA               (64 -> action_dim)
  - Aggregation Layer:
      Q(s, a) = V(s) + (A(s, a) - mean_a'(A(s, a')))

Double DQN Target:
  a* = argmax_a' Q_online(s', a')
  target = r + gamma * (1 - done) * Q_target(s', a*)

Prioritized Experience Replay (PER):
  - Binary SumTree for O(log N) updates and sampling
  - Priority p_i = (|TD_error_i| + epsilon)^alpha
  - Importance-sampling weights w_i = (N * P(i))^(-beta) / max_j(w_j)
  - Weighted Huber Loss backpropagation
"""

import os
import pickle
import random
import logging
import numpy as np

logger = logging.getLogger(__name__)

ALGORITHM_VERSION = "Dueling-Double-DQN-PER-v1"


# ─────────────────────────────────────────────────────────────────────────
# 1. Binary SumTree for Prioritized Experience Replay
# ─────────────────────────────────────────────────────────────────────────
class SumTree:
    """
    A binary tree data structure where parent nodes store the sum of their
    children. Leaves store the priorities of transitions, providing:
      - O(log N) sampling of transitions proportional to priority
      - O(log N) updates to priorities
    """
    def __init__(self, capacity: int):
        self.capacity = capacity
        # A binary tree with `capacity` leaves has 2 * capacity - 1 nodes
        self.tree = np.zeros(2 * capacity - 1, dtype=np.float64)
        self.data = [None] * capacity
        self.write = 0
        self.n_entries = 0

    def add(self, priority: float, data):
        """Insert new data with given priority."""
        idx = self.write + self.capacity - 1
        self.data[self.write] = data
        self.update(idx, priority)

        self.write = (self.write + 1) % self.capacity
        if self.n_entries < self.capacity:
            self.n_entries += 1

    def update(self, tree_idx: int, priority: float):
        """Update leaf priority and propagate change up the tree."""
        change = priority - self.tree[tree_idx]
        self.tree[tree_idx] = priority
        while tree_idx != 0:
            tree_idx = (tree_idx - 1) // 2
            self.tree[tree_idx] += change

    @property
    def total_priority(self) -> float:
        return float(self.tree[0])

    def get_leaf(self, val: float):
        """
        Traverse down to find leaf matching cumulative priority sample val.
        Returns (tree_index, priority, data).
        """
        parent_idx = 0
        while True:
            left_child_idx = 2 * parent_idx + 1
            right_child_idx = left_child_idx + 1

            # Leaf reached
            if left_child_idx >= len(self.tree):
                leaf_idx = parent_idx
                break

            if val <= self.tree[left_child_idx]:
                parent_idx = left_child_idx
            else:
                val -= self.tree[left_child_idx]
                parent_idx = right_child_idx

        data_idx = leaf_idx - self.capacity + 1
        return leaf_idx, float(self.tree[leaf_idx]), self.data[data_idx]


# ─────────────────────────────────────────────────────────────────────────
# 2. Prioritized Experience Replay Buffer
# ─────────────────────────────────────────────────────────────────────────
class PrioritizedReplayBuffer:
    """
    Prioritized Experience Replay (PER) buffer using proportional prioritization:
      p_i = (|TD_error_i| + epsilon)^alpha
    and importance-sampling weights:
      w_i = (N * P(i))^(-beta) / max_j(w_j)
    """
    def __init__(
        self,
        capacity: int = 10000,
        alpha: float = 0.6,
        beta_start: float = 0.4,
        beta_increment: float = 0.0005,
        epsilon: float = 1e-6,
        seed: int = None,
    ):
        self.tree = SumTree(capacity)
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta_start
        self.beta_start = beta_start
        self.beta_increment = beta_increment
        self.epsilon = epsilon
        self.max_priority = 1.0  # Initial priority for new transitions
        self._rng = np.random.default_rng(seed)

    def push(self, state, action, reward, next_state, done):
        """Add transition to buffer with highest priority so it gets visited."""
        transition = (
            np.asarray(state, dtype=np.float64),
            int(action),
            float(reward),
            np.asarray(next_state, dtype=np.float64),
            bool(done),
        )
        priority = (self.max_priority + self.epsilon) ** self.alpha
        self.tree.add(priority, transition)

    def sample(self, batch_size: int):
        """
        Sample a prioritized batch using stratified sampling across B segments.
        Returns:
          states, actions, rewards, next_states, dones, is_weights, tree_indices
        """
        if self.tree.n_entries == 0:
            raise ValueError("Cannot sample from an empty buffer.")

        total_p = self.tree.total_priority
        # Avoid divide-by-zero if tree sum is negligible
        if total_p <= 0.0 or np.isnan(total_p):
            total_p = 1.0

        segment = total_p / batch_size
        self.beta = min(1.0, self.beta + self.beta_increment)

        tree_indices = []
        priorities = []
        batch = []

        for i in range(batch_size):
            a = segment * i
            b = segment * (i + 1)
            v = float(self._rng.uniform(a, b))
            idx, p, data = self.tree.get_leaf(v)

            # Robust fallback for uninitialized leaf slots
            if data is None:
                valid_idx = int(self._rng.integers(0, self.tree.n_entries))
                leaf_idx = valid_idx + self.capacity - 1
                idx = leaf_idx
                p = float(self.tree.tree[leaf_idx])
                data = self.tree.data[valid_idx]

            priorities.append(max(p, self.epsilon))
            tree_indices.append(idx)
            batch.append(data)

        states, actions, rewards, next_states, dones = zip(*batch)

        # Importance-sampling weights
        probs = np.array(priorities, dtype=np.float64) / total_p
        probs = np.maximum(probs, 1e-12)
        weights = (self.tree.n_entries * probs) ** (-self.beta)
        max_w = np.max(weights)
        if max_w > 0:
            weights /= max_w
        else:
            weights = np.ones_like(weights)

        return (
            np.stack(states),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float64),
            np.stack(next_states),
            np.array(dones, dtype=bool),
            np.array(weights, dtype=np.float64),
            np.array(tree_indices, dtype=np.int64),
        )

    def update_priorities(self, tree_indices, td_errors):
        """Update priorities for sampled transitions based on absolute TD error."""
        for idx, td in zip(tree_indices, td_errors):
            abs_td = float(np.abs(td))
            priority = (abs_td + self.epsilon) ** self.alpha
            self.max_priority = max(self.max_priority, abs_td)
            self.tree.update(int(idx), priority)

    def __len__(self):
        return self.tree.n_entries


# Drop-in alias for existing code
ReplayBuffer = PrioritizedReplayBuffer


# ─────────────────────────────────────────────────────────────────────────
# 3. Dueling Q-Network with Shared Trunk, Value & Advantage Streams
# ─────────────────────────────────────────────────────────────────────────
class DuelingQNetwork:
    """
    Dueling Deep Q-Network in NumPy:
      Shared feature trunk:
        z1 = x @ W1 + b1, a1 = ReLU(z1)
        z2 = a1 @ W2 + b2, a2 = ReLU(z2)
      Value stream:
        V(s) = a2 @ WV + bV                  (batch, 1)
      Advantage stream:
        A(s, a) = a2 @ WA + bA               (batch, action_dim)
      Q-value combination:
        Q(s, a) = V(s) + (A(s, a) - mean_a'(A(s, a')))
    """
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 64, lr: float = 1e-3, seed: int = None):
        rng = np.random.default_rng(seed)
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim
        self.lr = lr

        # Shared feature trunk
        self.W1 = rng.normal(0, np.sqrt(2.0 / state_dim), (state_dim, hidden_dim))
        self.b1 = np.zeros(hidden_dim)
        self.W2 = rng.normal(0, np.sqrt(2.0 / hidden_dim), (hidden_dim, hidden_dim))
        self.b2 = np.zeros(hidden_dim)

        # Value stream: output shape (hidden_dim, 1)
        self.WV = rng.normal(0, np.sqrt(2.0 / hidden_dim), (hidden_dim, 1))
        self.bV = np.zeros(1)

        # Advantage stream: output shape (hidden_dim, action_dim)
        self.WA = rng.normal(0, np.sqrt(2.0 / hidden_dim), (hidden_dim, action_dim))
        self.bA = np.zeros(action_dim)

        # Adam optimizer parameters
        self._param_names = ["W1", "b1", "W2", "b2", "WV", "bV", "WA", "bA"]
        self._m = {k: np.zeros_like(getattr(self, k)) for k in self._param_names}
        self._v = {k: np.zeros_like(getattr(self, k)) for k in self._param_names}
        self._t = 0

    @staticmethod
    def _relu(x):
        return np.maximum(0, x)

    @staticmethod
    def _relu_grad(x):
        return (x > 0).astype(np.float64)

    def forward(self, x, cache: bool = False):
        """
        Forward pass.
        x: (batch, state_dim)
        Returns:
          q_values: (batch, action_dim)
        """
        x = np.asarray(x, dtype=np.float64)
        z1 = x @ self.W1 + self.b1
        a1 = self._relu(z1)
        z2 = a1 @ self.W2 + self.b2
        a2 = self._relu(z2)

        # Value stream: (batch, 1)
        V = a2 @ self.WV + self.bV
        # Advantage stream: (batch, action_dim)
        A = a2 @ self.WA + self.bA

        # Aggregation: Q(s, a) = V(s) + (A(s, a) - mean(A(s, :)))
        mean_A = np.mean(A, axis=1, keepdims=True)
        q = V + (A - mean_A)

        if cache:
            return q, (x, z1, a1, z2, a2, V, A, mean_A)
        return q

    def predict(self, state):
        """Convenience wrapper for single state: (state_dim,) -> (action_dim,)"""
        x = np.asarray(state, dtype=np.float64).reshape(1, -1)
        return self.forward(x)[0]

    def _adam_step(self, grads, beta1=0.9, beta2=0.999, eps=1e-8):
        self._t += 1
        for name in self._param_names:
            grad = grads[name]
            self._m[name] = beta1 * self._m[name] + (1 - beta1) * grad
            self._v[name] = beta2 * self._v[name] + (1 - beta2) * (grad ** 2)
            m_hat = self._m[name] / (1.0 - beta1 ** self._t)
            v_hat = self._v[name] / (1.0 - beta2 ** self._t)
            update = self.lr * m_hat / (np.sqrt(v_hat) + eps)
            setattr(self, name, getattr(self, name) - update)

    def train_on_batch(self, states, actions, targets, weights, huber_delta: float = 1.0):
        """
        Backpropagation with Importance-Sampling Weighted Huber Loss:
          actions: (batch,) taken actions
          targets: (batch,) target Q values for taken actions
          weights: (batch,) PER importance-sampling weights
        """
        batch_size = states.shape[0]
        q, (x, z1, a1, z2, a2, V, A, mean_A) = self.forward(states, cache=True)

        # Compute TD error on taken actions: (current - target)
        current_q_taken = q[np.arange(batch_size), actions]
        diff = current_q_taken - targets  # shape (batch,)

        # Huber loss derivative:
        #   h'(diff) = diff if |diff| <= delta else delta * sign(diff)
        abs_diff = np.abs(diff)
        huber_grad = np.where(abs_diff <= huber_delta, diff, huber_delta * np.sign(diff))

        # Full dL/dq matrix: weighted by PER weights w_i / batch_size
        d_q = np.zeros_like(q)
        d_q[np.arange(batch_size), actions] = (weights / batch_size) * huber_grad

        # ── Backpropagation through Dueling Aggregation Layer ──
        # Q = V + A - mean(A)
        # dL/dV = sum_a (dL/dQ)
        d_V = np.sum(d_q, axis=1, keepdims=True)  # (batch, 1)
        # dL/dA = dL/dQ - mean_a(dL/dQ)
        d_A = d_q - np.mean(d_q, axis=1, keepdims=True)  # (batch, action_dim)

        # Gradients for Value stream
        d_WV = a2.T @ d_V  # (hidden_dim, 1)
        d_bV = np.sum(d_V, axis=0)  # (1,)

        # Gradients for Advantage stream
        d_WA = a2.T @ d_A  # (hidden_dim, action_dim)
        d_bA = np.sum(d_A, axis=0)  # (action_dim,)

        # Backpropagation into shared layer 2 activations a2
        d_a2 = d_V @ self.WV.T + d_A @ self.WA.T  # (batch, hidden_dim)

        # Layer 2 gradients
        d_z2 = d_a2 * self._relu_grad(z2)
        d_W2 = a1.T @ d_z2
        d_b2 = np.sum(d_z2, axis=0)
        d_a1 = d_z2 @ self.W2.T

        # Layer 1 gradients
        d_z1 = d_a1 * self._relu_grad(z1)
        d_W1 = x.T @ d_z1
        d_b1 = np.sum(d_z1, axis=0)

        grads = {
            "W1": d_W1, "b1": d_b1,
            "W2": d_W2, "b2": d_b2,
            "WV": d_WV, "bV": d_bV,
            "WA": d_WA, "bA": d_bA,
        }
        self._adam_step(grads)

        # Compute scalar Huber loss for reporting
        huber_losses = np.where(
            abs_diff <= huber_delta,
            0.5 * (diff ** 2),
            huber_delta * (abs_diff - 0.5 * huber_delta)
        )
        total_loss = float(np.mean(weights * huber_losses))
        return total_loss

    def get_weights(self):
        return {k: getattr(self, k).copy() for k in self._param_names}

    def set_weights(self, weights):
        for k in self._param_names:
            if k in weights:
                setattr(self, k, weights[k].copy())


# Drop-in alias for existing code
QNetwork = DuelingQNetwork


# ─────────────────────────────────────────────────────────────────────────
# 4. Double DQN Agent with Dueling Network and Prioritized Replay
# ─────────────────────────────────────────────────────────────────────────
class DoubleDQNAgent:
    """
    Dueling Double Deep Q-Network Agent with Prioritized Experience Replay.
    Combines:
      1. Dueling network architecture: separates V(s) and A(s, a).
      2. Double DQN target calculation: online network chooses action,
         target network evaluates it to eliminate overestimation bias.
      3. Prioritized Experience Replay (PER): proportional TD-error sampling
         with importance-sampling loss correction.
    """
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dim: int = 64,
        lr: float = 1e-3,
        gamma: float = 0.95,
        epsilon_start: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
        buffer_capacity: int = 10000,
        batch_size: int = 32,
        target_update_every: int = 25,
        alpha: float = 0.6,
        beta_start: float = 0.4,
        beta_increment: float = 0.0005,
        epsilon_per: float = 1e-6,
        seed: int = 42,
    ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update_every = target_update_every
        self._train_steps = 0
        self.algorithm_version = ALGORITHM_VERSION

        # Dual Dueling Networks: Online and Target
        self.online_net = DuelingQNetwork(state_dim, action_dim, hidden_dim, lr, seed=seed)
        self.target_net = DuelingQNetwork(state_dim, action_dim, hidden_dim, lr, seed=seed)
        self.target_net.set_weights(self.online_net.get_weights())

        # Prioritized Experience Replay Buffer
        self.replay_buffer = PrioritizedReplayBuffer(
            capacity=buffer_capacity,
            alpha=alpha,
            beta_start=beta_start,
            beta_increment=beta_increment,
            epsilon=epsilon_per,
            seed=seed,
        )

    def act(self, state, explore: bool = True):
        """
        Epsilon-greedy action selection.
        Returns: (action_index, q_values)
        """
        q_values = self.online_net.predict(state)
        if explore and random.random() < self.epsilon:
            action = random.randrange(self.action_dim)
        else:
            action = int(np.argmax(q_values))
        return action, q_values

    def remember(self, state, action, reward, next_state, done):
        """Store experience transition into Prioritized Experience Replay buffer."""
        self.replay_buffer.push(state, action, reward, next_state, done)

    def replay(self):
        """
        One training step using Dueling Double DQN + PER:
          1. Sample prioritized batch with importance-sampling weights
          2. Double DQN target:
               a* = argmax_a' Q_online(s', a')
               target = r + gamma * (1 - done) * Q_target(s', a*)
          3. Calculate TD errors: target - Q_online(s, a)
          4. Update PER priorities using new TD errors
          5. Weighted Huber Loss backpropagation on online network
          6. Periodically update target network
          7. Anneal epsilon
        """
        if len(self.replay_buffer) < self.batch_size:
            return None

        states, actions, rewards, next_states, dones, is_weights, tree_indices = (
            self.replay_buffer.sample(self.batch_size)
        )

        # ── Double DQN Target Decoupling ──
        # 1. Online network selects best action: a* = argmax Q_online(s', a')
        next_q_online = self.online_net.forward(next_states)
        best_next_actions = np.argmax(next_q_online, axis=1)

        # 2. Target network evaluates that chosen action: Q_target(s', a*)
        next_q_target = self.target_net.forward(next_states)
        eval_next_q = next_q_target[np.arange(self.batch_size), best_next_actions]

        # 3. Target calculation with terminal state handling
        targets = rewards + self.gamma * eval_next_q * (1.0 - dones.astype(np.float64))

        # Current Q-values for taken actions
        current_q = self.online_net.forward(states)
        current_taken_q = current_q[np.arange(self.batch_size), actions]

        # ── Prioritized Experience Replay Priority Update ──
        td_errors = targets - current_taken_q
        self.replay_buffer.update_priorities(tree_indices, td_errors)

        # ── Online Network Backpropagation ──
        loss = self.online_net.train_on_batch(states, actions, targets, is_weights)

        # Target network synchronization
        self._train_steps += 1
        if self._train_steps % self.target_update_every == 0:
            self.update_target()

        # Anneal exploration rate
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        return loss

    def update_target(self):
        """Hard copy online network weights to target network."""
        self.target_net.set_weights(self.online_net.get_weights())

    def save(self, path: str):
        """Save Dueling Double DQN model and metadata."""
        data = {
            "algorithm_version": self.algorithm_version,
            "online_weights": self.online_net.get_weights(),
            "target_weights": self.target_net.get_weights(),
            "epsilon": self.epsilon,
            "train_steps": self._train_steps,
            "state_dim": self.state_dim,
            "action_dim": self.action_dim,
            "buffer_beta": self.replay_buffer.beta,
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)
        logger.info(f"Saved {self.algorithm_version} model to {path}")

    def load(self, path: str):
        """
        Load weights and state.
        Gracefully handles legacy standard DQN checkpoints by detecting missing
        value/advantage stream weights and safely reinitializing.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file {path} does not exist.")

        with open(path, "rb") as f:
            data = pickle.load(f)

        version = data.get("algorithm_version", "legacy-standard-dqn")
        logger.info(f"Loading RL model checkpoint: version={version}")

        online_w = data.get("online_weights", {})
        # Check if checkpoint has Dueling architecture parameters (WV, WA)
        if "WV" in online_w and "WA" in online_w:
            self.online_net.set_weights(online_w)
            self.target_net.set_weights(data.get("target_weights", online_w))
            self.epsilon = data.get("epsilon", self.epsilon)
            self._train_steps = data.get("train_steps", 0)
            if "buffer_beta" in data:
                self.replay_buffer.beta = data["buffer_beta"]
            logger.info(f"Successfully loaded Dueling Double DQN weights (step={self._train_steps}, epsilon={self.epsilon:.3f})")
        else:
            logger.warning(
                f"Checkpoint {path} contains legacy standard DQN weights (incompatible shapes). "
                f"Initializing new Dueling Double DQN architecture with random weights."
            )
            # Retain fresh He-initialized weights for Dueling architecture


# Drop-in alias for drop-in compatibility across the entire application
DQNAgent = DoubleDQNAgent
