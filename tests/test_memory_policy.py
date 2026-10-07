from memory_infra.memory import MemoryItem, MemoryStore
from memory_infra.policy import LearnedPolicy
from memory_infra.retrieval import retrieve


def test_policy_prefers_high_utility_over_near_failure() -> None:
    store = MemoryStore()
    store.add(MemoryItem("near-fail", "similar but failed", [1.0, 0.1], failure=5))
    store.add(MemoryItem("far-ok", "less similar but worked", [0.7, 0.7], success=5))
    query = [1.0, 0.0]
    assert retrieve(store, query).ids[0] == "near-fail"
    assert retrieve(store, query, LearnedPolicy(alpha=1.0)).ids[0] == "far-ok"
