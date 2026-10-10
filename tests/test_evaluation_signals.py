"""Focused contract tests for evaluation-signal separation.

Does not alter policy, frozen assets, or Phase H parameters.
"""

from memory_infra.learner import FeedbackLearner
from memory_infra.memory import MemoryItem, MemoryStore
from memory_infra.policy import LearnedPolicy
from memory_infra.trace import RetrievalTrace


def test_missing_success_is_unknown_and_does_not_update_learning_state() -> None:
    store = MemoryStore()
    store.add(MemoryItem("m1", "text", [1.0, 0.0], success=3, failure=1))
    policy = LearnedPolicy(alpha=0.5)
    result = FeedbackLearner().observe(store, policy, "m1", None, baseline_id="other")
    item = store.get("m1")
    assert item.success == 3
    assert item.failure == 1
    assert item.utility == (3 - 1) / (3 + 1 + 1)
    assert policy.alpha == 0.5
    assert result is policy


def test_trace_evaluation_signals_default_to_none_not_guessed() -> None:
    trace = RetrievalTrace(
        trace_id="t1",
        task_id="task1",
        memory_id="m1",
        retrieved=True,
        rank=1,
        mode="adaptive",
        policy_version="v0.1",
    )
    assert trace.used is None
    assert trace.task_success is None
    assert trace.user_feedback is None


def test_learning_feedback_and_evaluation_signals_are_distinct_types() -> None:
    # Learning path consumes bool|None and mutates counts.
    # Evaluation path records on Trace without mutating policy.
    store = MemoryStore()
    store.add(MemoryItem("m1", "text", [1.0, 0.0]))
    policy = LearnedPolicy()
    FeedbackLearner().observe(store, policy, "m1", True)
    assert store.get("m1").success == 1

    trace = RetrievalTrace(
        trace_id="t2",
        task_id="task2",
        memory_id="m1",
        retrieved=True,
        rank=1,
        mode="baseline",
        policy_version="v0.1",
        task_success=True,  # evaluation signal, not written back
        user_feedback=1.0,
    )
    # Policy and counts are unaffected by constructing a Trace
    assert policy.alpha == 0.5
    assert store.get("m1").success == 1
    assert trace.task_success is True
    assert trace.user_feedback == 1.0
