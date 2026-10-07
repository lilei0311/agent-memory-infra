from memory_infra.learner import FeedbackLearner
from memory_infra.memory import MemoryItem, MemoryStore
from memory_infra.policy import LearnedPolicy


def test_missing_feedback_does_not_update_item_or_alpha() -> None:
    store = MemoryStore()
    store.add(MemoryItem("far-ok", "worked", [0.7, 0.7], success=5))
    policy = LearnedPolicy(alpha=0.5)
    FeedbackLearner().observe(store, policy, "far-ok", None, baseline_id="near-fail")
    assert store.get("far-ok").success == 5
    assert store.get("far-ok").failure == 0
    assert policy.alpha == 0.5


def test_observed_flip_is_not_the_true_label() -> None:
    """Noise may flip the label the learner writes; the true bit stays separate."""
    truth = True
    observed = not truth
    store = MemoryStore()
    store.add(MemoryItem("far-ok", "worked", [0.7, 0.7]))
    policy = LearnedPolicy(alpha=0.5)
    FeedbackLearner().observe(store, policy, "far-ok", observed, baseline_id="near-fail")
    assert store.get("far-ok").failure == 1
    assert store.get("far-ok").success == 0
    assert truth is True
