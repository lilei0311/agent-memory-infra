"""V0.1 experiment: does historical feedback beat relevance-only retrieval?

Setup (synthetic, fixed seed):
  - 10 memories, 2D embeddings.
  - 2 "near-fail" items: high similarity to the query, repeated failures.
  - 2 "far-ok" items: slightly lower similarity, repeated successes.
  - 6 neutral items: mixed history.

Baseline: score = cosine similarity.
Adaptive: score = similarity + alpha * utility (Laplace-smoothed).

Both policies see the identical candidate set and seed.
Each round: retrieve top-k=3, observe outcome, update alpha.

Expected output (illustrative, actual numbers vary by seed):

  round | baseline_top | policy_top | alpha
  -----+--------------+-----------+------
      1 | near-fail-1  | near-fail-1 | 0.50
      2 | near-fail-1  | far-ok-1    | 0.55
      3 | near-fail-1  | far-ok-1    | 0.60
      5 | near-fail-1  | far-ok-1    | 0.70
     10 | near-fail-1  | far-ok-1    | 0.95
     20 | near-fail-1  | far-ok-1    | 1.40

  Summary:
    baseline success rate : 0.40
    policy   success rate : 0.85
    alpha trajectory      : 0.50 -> 1.40

Pass criteria for the core hypothesis:
  1. policy success rate > baseline success rate
  2. alpha rises across rounds (policy learns utility matters)
  3. policy top-1 converges to a high-utility item
"""

from __future__ import annotations

import random

from memory_infra.learner import FeedbackLearner
from memory_infra.memory import MemoryItem, MemoryStore
from memory_infra.policy import LearnedPolicy
from memory_infra.retrieval import retrieve


SEED = 7
ROUNDS = 20
K = 3


def build_store(rng: random.Random) -> MemoryStore:
    store = MemoryStore()
    # near-fail: similar to query [1, 0], but history is all failures
    store.add(MemoryItem("near-fail-1", "similar but failed", [1.0, 0.05], failure=8))
    store.add(MemoryItem("near-fail-2", "similar but failed", [0.98, 0.10], failure=6))
    # far-ok: less similar, but history is all successes
    store.add(MemoryItem("far-ok-1", "less similar but worked", [0.72, 0.70], success=8))
    store.add(MemoryItem("far-ok-2", "less similar but worked", [0.70, 0.72], success=7))
    # neutral: mixed / sparse history
    for i in range(6):
        store.add(
            MemoryItem(
                f"neutral-{i}",
                f"neutral item {i}",
                [rng.uniform(-1, 1), rng.uniform(-1, 1)],
                success=rng.randint(0, 3),
                failure=rng.randint(0, 3),
            )
        )
    return store


def outcome(memory_id: str, rng: random.Random) -> bool:
    """Ground truth: far-ok succeeds, near-fail fails, neutrals coin-flip."""
    if memory_id.startswith("far-ok"):
        return True
    if memory_id.startswith("near-fail"):
        return False
    return rng.random() < 0.5


def main() -> None:
    rng = random.Random(SEED)
    store = build_store(rng)
    policy = LearnedPolicy(alpha=0.5)
    learner = FeedbackLearner(step=0.05)
    query = [1.0, 0.0]  # points at the near-fail cluster

    print(f"{'round':>5} | {'baseline_top':<12} | {'policy_top':<12} | {'alpha':>5}")
    print(f"{'-'*5}-+-{'-'*12}-+-{'-'*12}-+-{'-'*5}")

    base_ok = pol_ok = 0
    for r in range(1, ROUNDS + 1):
        base = retrieve(store, query, task_id=f"t{r:03d}")
        pol = retrieve(store, query, policy, task_id=f"t{r:03d}")
        b_id, p_id = base[0].memory_id, pol[0].memory_id

        p_success = outcome(p_id, rng)
        learner.observe(store, policy, p_id, p_success, baseline_id=b_id)

        base_ok += int(outcome(b_id, random.Random(SEED + 1000 + r)))
        pol_ok += int(p_success)

        if r <= 3 or r in (5, 10, 15, 20):
            print(f"{r:>5} | {b_id:<12} | {p_id:<12} | {policy.alpha:>5.2f}")

    print()
    print(f"baseline success rate : {base_ok / ROUNDS:.2f}")
    print(f"policy   success rate : {pol_ok / ROUNDS:.2f}")
    print(f"alpha trajectory      : 0.50 -> {policy.alpha:.2f}")
    print()
    print("Pass criteria:")
    print(f"  1. policy > baseline        : {pol_ok > base_ok}")
    print(f"  2. alpha rises              : {policy.alpha > 0.5}")
    print(f"  3. policy converges to far-ok : {pol[0].memory_id.startswith('far-ok')}")


if __name__ == "__main__":
    main()
