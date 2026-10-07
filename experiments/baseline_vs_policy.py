"""Phase-1 check: does task feedback beat pure similarity?

Synthetic case: the nearest neighbor is a repeated failure;
a slightly farther item is a repeated success.
"""

from memory_infra.learner import FeedbackLearner
from memory_infra.memory import MemoryItem, MemoryStore
from memory_infra.policy import LearnedPolicy
from memory_infra.retrieval import retrieve


def build_store() -> MemoryStore:
    store = MemoryStore()
    store.add(MemoryItem("near-fail", "similar but failed", [1.0, 0.1], failure=5))
    store.add(MemoryItem("far-ok", "less similar but worked", [0.7, 0.7], success=5))
    return store


def main() -> None:
    store = build_store()
    query = [1.0, 0.0]
    policy = LearnedPolicy(alpha=0.8)
    base = retrieve(store, query, task_id="task_001")
    learned = retrieve(store, query, policy, task_id="task_001")
    print("baseline", [t.memory_id for t in base], [round(t.scores[0], 3) for t in base])
    print("policy  ", [t.memory_id for t in learned], [round(t.scores[0], 3) for t in learned])
    for t in learned:
        t.task_success = True
        t.used = True
    FeedbackLearner().observe(
        store, policy, learned[0].memory_id, success=True, baseline_id=base[0].memory_id
    )
    print("alpha   ", round(policy.alpha, 3))
    print("trace   ", learned[0])


if __name__ == "__main__":
    main()
