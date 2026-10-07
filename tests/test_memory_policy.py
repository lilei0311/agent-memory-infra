import pytest
from memory_infra.learner import FeedbackLearner
from memory_infra.memory import MemoryItem, MemoryStore
from memory_infra.policy import LearnedPolicy
from memory_infra.retrieval import retrieve


def _store() -> MemoryStore:
    store = MemoryStore()
    store.add(MemoryItem("near-fail", "similar but failed", [1.0, 0.1], failure=5))
    store.add(MemoryItem("far-ok", "less similar but worked", [0.7, 0.7], success=5))
    return store


def test_policy_prefers_high_utility_over_near_failure() -> None:
    store = _store()
    query = [1.0, 0.0]
    base = retrieve(store, query, task_id="t1")
    learned = retrieve(store, query, LearnedPolicy(alpha=1.0), task_id="t1")
    assert base[0].memory_id == "near-fail"
    assert learned[0].memory_id == "far-ok"
    assert learned[0].task_id == "t1"
    assert learned[0].policy_version.startswith("adaptive-")
    assert learned[0].rank == 1


def test_learner_nudges_alpha_only_when_policy_beats_baseline() -> None:
    store = _store()
    policy = LearnedPolicy(alpha=0.8)
    FeedbackLearner().observe(store, policy, "far-ok", success=True, baseline_id="near-fail")
    assert policy.alpha == pytest.approx(0.85)
    assert store.get("far-ok").success == 6  # initial success=5, observe increments by 1


def test_learner_unchanged_when_same_pick() -> None:
    store = _store()
    policy = LearnedPolicy(alpha=0.8)
    FeedbackLearner().observe(store, policy, "near-fail", success=True, baseline_id="near-fail")
    assert policy.alpha == 0.8


def test_learner_lowers_alpha_on_policy_failure() -> None:
    store = _store()
    policy = LearnedPolicy(alpha=0.8)
    FeedbackLearner().observe(store, policy, "far-ok", success=False, baseline_id="near-fail")
    assert policy.alpha == 0.75


def test_utility_is_laplace_smoothed() -> None:
    item = MemoryItem("x", "", [], success=100, failure=1)
    assert item.utility > 0.9
    item.failure += 1
    assert item.utility > 0.9
