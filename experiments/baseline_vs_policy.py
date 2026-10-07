"""V0.1 experiment: does historical feedback beat relevance-only retrieval?

Setup (synthetic, fixed seed):
  - 10 memories, 2D embeddings.
  - 2 "near-fail" items: high similarity to the query, but repeated failures.
  - 2 "far-ok" items: slightly lower similarity, but repeated successes.
  - 6 neutral items: mixed history.

Baseline: score = cosine similarity.
Adaptive: score = similarity + alpha * utility (Laplace-smoothed).

Both policies see the identical candidate set and seed.
Each round: retrieve top-k=3, observe outcome, update alpha.

Expected output (illustrative, actual numbers vary by seed):

  round | baseline_top | policy_top | alpha
  -----+--------------+-----------+------
      0 | near-fail    | near-fail | 0.50
      1 | near-fail    | far-ok    | 0.55
      2 | near-fail    | far-ok    | 0.60
      ...
     20 | near-fail    | far-ok    | 1.20

  Summary:
    baseline success rate : 0.40   (picks near-fail most rounds)
    policy   success rate : 0.85   (converges to far-ok)
    alpha trajectory      : 0.50 -> 1.20 (monotone-ish rise)

Pass criteria for the core hypothesis:
  1. policy success rate > baseline success rate
  2. alpha rises across rounds (policy learns utility matters)
  3. policy top-1 converges to the high-utility item
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


def run_round(
    store: MemoryStore,
    query: list[float],
    policy: LearnedPolicy,
    learner: FeedbackLearner,
    task_id: str,
    success_fn,
) -> tuple[str, str, float]:
    base = retrieve(store, query, task_id=task_id)
    pol = retrieve(store, query, policy, task_id=task_id)
    base_id, pol_id = base[0].memory_id, pol[0].memory_id
    # outcome follows the policy's pick (the system acts on its own choice)
    success = success_fn(pol_id)
    learner.observe(store, policy, pol_id, success, baseline_id=base_id)
    return base_id, pol_id, policy.alpha


def main() -> None:
    rng = random.Random(SEED)
    store = build_store(rng)
    policy = LearnedPolicy(alpha=0.5)
    learner = FeedbackLearner(step=0.05)
    query = [1.0, 0.0]  # points at the near-fail cluster

    def success_fn(memory_id: str) -> bool:
        # far-ok items succeed; near-fail items fail; neutrals coin-flip
        if memory_id.startswith("far-ok"):
            return True
        if memory_id.startswith("near-fail"):
            return False
        return rng.random() < 0.5

    print(f"{'round':>5} | {'baseline_top':<12} | {'policy_top':<12} | {'alpha':>5}")
    print(f"{'-'*5}-+-{'-'*12}-+-{'-'*12}-+-{'-'*5}")
    base_ok = pol_ok = 0
    for r in range(1, ROUNDS + 1):
        base_id, pol_id, alpha = run_round(
            store, query, policy, learner, task_id=f"t{r:03d}", success_fn=success_fn
        )
        base_ok += success_fn.__wrapped__(base_id) if False else (1 if not base_id.startswith("near-fail") and (base_id.startswith("far-ok") or rng.random() < 0.5) else 0)
        # recount baseline properly: baseline picks near-fail -> fail
        base_ok = sum(1 for _ in range(r) if True)  # placeholder replaced below
        pol_ok += 1 if pol_id.startswith("far-ok") else (0 if pol_id.startswith("near-fail") else 1)
        if r in (1, 5, 10, 15, 20) or r <= 3:
            print(f"{r:>5} | {base_id:<12} | {pol_id:<12} | {alpha:>5.2f}")

    # clean summary recompute
    rng2 = random.Random(SEED)
    store2 = build_store(rng2)
    policy2 = LearnedPolicy(alpha=0.5)
    learner2 = FeedbackLearner(step=0.05)
    b_ok = p_ok = 0
    for r in range(1, ROUNDS + 1):
        base = retrieve(store2, query, task_id=f"t{r:03d}")
        pol = retrieve(store2, query, policy2, task_id=f"t{r:03d}")
        b_id, p_id = base[0].memory_id, pol[0].memory_id
        p_success = p_id.startswith("far-ok") or (not p_id.startswith("near-fail") and rng2.random() < 0.5)
        b_success = b_id.startswith("far-ok") or (not b_id.startswith("near-fail") and rng2.random() < 0.5)
        learner2.observe(store2, policy2, p_id, p_success, baseline_id=b_id)
        b_ok += int(b_success)
        p_ok += int(p_success)

    print()
    print(f"baseline success rate : {b_ok / ROUNDS:.2f}")
    print(f"policy   success rate : {p_ok / ROUNDS:.2f}")
    print(f"alpha trajectory      : 0.50 -> {policy2.alpha:.2f}")
    print()
    print("Pass criteria:")
    print(f"  1. policy > baseline     : {p_ok > b_ok}")
    print(f"  2. alpha rises           : {policy2.alpha > 0.5}")
    print(f"  3. policy converges to far-ok : {pol[0].memory_id.startswith('far-ok')}")


if __name__ == "__main__":
    main()
