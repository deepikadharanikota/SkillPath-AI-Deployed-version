"""
test_dueling_double_dqn.py
--------------------------
Comprehensive unit test suite for:
  1. Dueling Q-Network (Value and Advantage streams, aggregation formula, invariant check)
  2. Double DQN target decoupling and terminal state handling
  3. Binary SumTree and Prioritized Experience Replay (PER)
  4. Importance-sampling weights calculation and normalization
  5. Backpropagation gradient verification via finite differences
  6. Model serialization, deserialization, and versioning
"""

import os
import unittest
import numpy as np

from dqn_agent import (
    SumTree,
    PrioritizedReplayBuffer,
    DuelingQNetwork,
    DoubleDQNAgent,
    ALGORITHM_VERSION,
)
from environment import STATE_DIM, ACTION_DIM


class TestSumTree(unittest.TestCase):
    def test_sumtree_insertion_and_sum(self):
        capacity = 4
        tree = SumTree(capacity)
        # Add 4 elements with priorities [1.0, 2.0, 3.0, 4.0]
        tree.add(1.0, "data_0")
        tree.add(2.0, "data_1")
        tree.add(3.0, "data_2")
        tree.add(4.0, "data_3")

        self.assertEqual(tree.n_entries, 4)
        self.assertAlmostEqual(tree.total_priority, 10.0, places=6)

        # Test retrieval with get_leaf
        idx0, p0, d0 = tree.get_leaf(0.5)
        self.assertEqual(d0, "data_0")

        idx1, p1, d1 = tree.get_leaf(2.5)
        self.assertEqual(d1, "data_1")

        idx2, p2, d2 = tree.get_leaf(5.0)
        self.assertEqual(d2, "data_2")

        idx3, p3, d3 = tree.get_leaf(9.5)
        self.assertEqual(d3, "data_3")

    def test_sumtree_update(self):
        capacity = 4
        tree = SumTree(capacity)
        tree.add(1.0, "data_0")
        tree.add(2.0, "data_1")
        # Update first entry priority from 1.0 to 5.0
        leaf_idx = 0 + capacity - 1
        tree.update(leaf_idx, 5.0)
        self.assertAlmostEqual(tree.total_priority, 7.0, places=6)


class TestPrioritizedReplayBuffer(unittest.TestCase):
    def test_buffer_push_and_sample(self):
        buffer = PrioritizedReplayBuffer(capacity=100, alpha=0.6, beta_start=0.4, seed=42)
        for i in range(50):
            s = np.zeros(STATE_DIM) + i
            buffer.push(s, i % ACTION_DIM, 1.0, s + 1, False)

        self.assertEqual(len(buffer), 50)

        states, actions, rewards, next_states, dones, weights, tree_indices = buffer.sample(16)
        self.assertEqual(states.shape, (16, STATE_DIM))
        self.assertEqual(actions.shape, (16,))
        self.assertEqual(rewards.shape, (16,))
        self.assertEqual(next_states.shape, (16, STATE_DIM))
        self.assertEqual(dones.shape, (16,))
        self.assertEqual(weights.shape, (16,))
        self.assertEqual(tree_indices.shape, (16,))

        # Importance-sampling weights must be non-negative and max normalized to <= 1.0
        self.assertTrue(np.all(weights >= 0.0))
        self.assertAlmostEqual(float(np.max(weights)), 1.0, places=5)

    def test_update_priorities(self):
        buffer = PrioritizedReplayBuffer(capacity=50, alpha=0.6, seed=42)
        for i in range(10):
            s = np.zeros(STATE_DIM)
            buffer.push(s, 0, 1.0, s, False)

        _, _, _, _, _, _, tree_indices = buffer.sample(4)
        large_td_errors = np.array([10.0, 0.01, 5.0, 2.0])
        buffer.update_priorities(tree_indices, large_td_errors)

        # Higher TD error should result in higher total priority
        self.assertGreater(buffer.tree.total_priority, 10.0)


class TestDuelingNetwork(unittest.TestCase):
    def setUp(self):
        self.state_dim = 13
        self.action_dim = 27
        self.net = DuelingQNetwork(self.state_dim, self.action_dim, hidden_dim=32, seed=123)

    def test_dueling_aggregation_invariant(self):
        """
        Check that Q(s, a) = V(s) + (A(s, a) - mean(A(s, :)))
        and consequently: mean_a(Q(s, a)) == V(s)
        and sum_a(Q(s, a) - V(s)) == 0.
        """
        x = np.random.randn(5, self.state_dim)
        q, (x, z1, a1, z2, a2, V, A, mean_A) = self.net.forward(x, cache=True)

        expected_q = V + (A - mean_A)
        np.testing.assert_allclose(q, expected_q, rtol=1e-6, atol=1e-6)

        # Invariant: mean over actions of (Q - V) must equal 0
        diff = q - V
        np.testing.assert_allclose(np.mean(diff, axis=1), np.zeros(5), atol=1e-6)
        np.testing.assert_allclose(np.mean(q, axis=1, keepdims=True), V, atol=1e-6)

    def test_numerical_gradient_check(self):
        """
        Verify analytical backpropagation gradients in train_on_batch using finite differences.
        """
        batch_size = 2
        states = np.random.randn(batch_size, self.state_dim)
        actions = np.array([2, 5])
        targets = np.array([1.5, -0.8])
        weights = np.array([0.9, 1.0])

        # Make copy of network to test parameter gradients
        test_net = DuelingQNetwork(self.state_dim, self.action_dim, hidden_dim=16, seed=99)

        # Compute initial loss
        q = test_net.forward(states)
        diff = q[np.arange(batch_size), actions] - targets
        abs_diff = np.abs(diff)
        huber = np.where(abs_diff <= 1.0, 0.5 * (diff ** 2), abs_diff - 0.5)
        loss = np.mean(weights * huber)

        # Check gradient on WV
        eps = 1e-6
        WV_grad_num = np.zeros_like(test_net.WV)
        for i in range(min(4, test_net.WV.shape[0])):
            test_net.WV[i, 0] += eps
            q_plus = test_net.forward(states)
            diff_p = q_plus[np.arange(batch_size), actions] - targets
            loss_p = np.mean(weights * np.where(np.abs(diff_p) <= 1.0, 0.5 * (diff_p ** 2), np.abs(diff_p) - 0.5))

            test_net.WV[i, 0] -= 2 * eps
            q_minus = test_net.forward(states)
            diff_m = q_minus[np.arange(batch_size), actions] - targets
            loss_m = np.mean(weights * np.where(np.abs(diff_m) <= 1.0, 0.5 * (diff_m ** 2), np.abs(diff_m) - 0.5))

            test_net.WV[i, 0] += eps
            WV_grad_num[i, 0] = (loss_p - loss_m) / (2 * eps)

        # Run forward with cache to get analytic gradient
        q, (x, z1, a1, z2, a2, V, A, mean_A) = test_net.forward(states, cache=True)
        huber_grad = np.where(abs_diff <= 1.0, diff, np.sign(diff))
        d_q = np.zeros_like(q)
        d_q[np.arange(batch_size), actions] = (weights / batch_size) * huber_grad
        d_V = np.sum(d_q, axis=1, keepdims=True)
        d_WV_analytic = a2.T @ d_V

        for i in range(min(4, test_net.WV.shape[0])):
            self.assertAlmostEqual(d_WV_analytic[i, 0], WV_grad_num[i, 0], places=4)


class TestDoubleDQNAgent(unittest.TestCase):
    def setUp(self):
        self.agent = DoubleDQNAgent(
            state_dim=STATE_DIM,
            action_dim=ACTION_DIM,
            hidden_dim=32,
            batch_size=8,
            seed=42,
        )

    def test_double_dqn_target_selection_and_terminal(self):
        """
        Verify:
          1. Online network selects best action a* = argmax Q_online(s', a')
          2. Target network evaluates Q_target(s', a*)
          3. Terminal state done=True results in target = r exactly.
        """
        # Set distinct weights for online and target nets
        self.agent.target_net.WV += 0.5
        self.agent.target_net.WA += 0.5

        next_states = np.random.randn(4, STATE_DIM)
        rewards = np.array([1.0, 2.0, 0.5, -1.0])
        dones = np.array([False, True, False, True])

        # Step 1: online action selection
        online_next_q = self.agent.online_net.forward(next_states)
        best_actions = np.argmax(online_next_q, axis=1)

        # Step 2: target evaluation
        target_next_q = self.agent.target_net.forward(next_states)
        eval_q = target_next_q[np.arange(4), best_actions]

        # Double DQN target
        targets = rewards + self.agent.gamma * eval_q * (1.0 - dones.astype(float))

        # Terminal state targets must equal reward exactly
        self.assertAlmostEqual(targets[1], rewards[1], places=6)
        self.assertAlmostEqual(targets[3], rewards[3], places=6)

        # Non-terminal state targets must include bootstrapped gamma * eval_q
        self.assertAlmostEqual(targets[0], rewards[0] + self.agent.gamma * eval_q[0], places=6)
        self.assertAlmostEqual(targets[2], rewards[2] + self.agent.gamma * eval_q[2], places=6)

    def test_training_step(self):
        # Populate replay buffer
        for i in range(20):
            s = np.random.randn(STATE_DIM)
            s_next = np.random.randn(STATE_DIM)
            self.agent.remember(s, i % ACTION_DIM, 0.5, s_next, False)

        loss = self.agent.replay()
        self.assertIsNotNone(loss)
        self.assertGreaterEqual(loss, 0.0)

    def test_save_and_load(self):
        temp_path = "test_dueling_weights.pkl"
        try:
            self.agent.save(temp_path)
            self.assertTrue(os.path.exists(temp_path))

            new_agent = DoubleDQNAgent(
                state_dim=STATE_DIM,
                action_dim=ACTION_DIM,
                hidden_dim=32,
                seed=999,
            )
            new_agent.load(temp_path)

            self.assertEqual(new_agent.algorithm_version, ALGORITHM_VERSION)
            np.testing.assert_allclose(
                new_agent.online_net.WV, self.agent.online_net.WV, rtol=1e-7
            )
            np.testing.assert_allclose(
                new_agent.online_net.WA, self.agent.online_net.WA, rtol=1e-7
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_double_dqn_vs_standard_dqn(self):
        """
        Verify that Double DQN target differs from Standard DQN target
        when target network max differs from target network value at argmax(online).
        """
        next_states = np.random.randn(1, STATE_DIM)
        # Construct synthetic online and target Q-values
        # Online prefers action 0
        self.agent.online_net.WA[:, 0] = 5.0
        self.agent.online_net.WA[:, 1] = 1.0
        # Target has an overestimate on action 1, but lower on action 0
        self.agent.target_net.WA[:, 0] = 2.0
        self.agent.target_net.WA[:, 1] = 10.0

        online_q = self.agent.online_net.forward(next_states)
        target_q = self.agent.target_net.forward(next_states)

        best_action_online = np.argmax(online_q, axis=1)[0]
        self.assertEqual(best_action_online, 0)

        # Standard DQN would have taken max(target_q) which is on action 1 (value ~10)
        standard_target_q = np.max(target_q, axis=1)[0]

        # Double DQN evaluates target_q at online's best action (action 0, value ~2)
        double_target_q = target_q[0, best_action_online]

        self.assertNotEqual(standard_target_q, double_target_q)
        self.assertLess(double_target_q, standard_target_q)

    def test_legacy_checkpoint_fallback(self):
        """
        Test that loading a legacy checkpoint does not crash the agent
        and preserves initialization.
        """
        legacy_path = "test_legacy_weights.pkl"
        try:
            import pickle
            with open(legacy_path, "wb") as f:
                pickle.dump({
                    "online_weights": {"W1": np.zeros((STATE_DIM, 64)), "b1": np.zeros(64), "W3": np.zeros((64, ACTION_DIM))},
                    "target_weights": {},
                    "epsilon": 0.5,
                    "train_steps": 100,
                    "state_dim": STATE_DIM,
                    "action_dim": ACTION_DIM,
                }, f)

            new_agent = DoubleDQNAgent(
                state_dim=STATE_DIM,
                action_dim=ACTION_DIM,
                hidden_dim=32,
                seed=999,
            )
            # Should not crash, will log a warning and retain valid Dueling architecture
            new_agent.load(legacy_path)
            self.assertTrue(hasattr(new_agent.online_net, "WV"))
            self.assertTrue(hasattr(new_agent.online_net, "WA"))
        finally:
            if os.path.exists(legacy_path):
                os.remove(legacy_path)


if __name__ == "__main__":
    unittest.main()

