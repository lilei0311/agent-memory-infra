"""Issue #1 Stage 1 robustness matrix.

Config is locked. Do not retune seeds, alpha, K, or the world after seeing results.
Phase A is the 0% noise / 100% feedback control and is reused as the
Phase B 0% and Phase C 100% rows.
"""

from __future__ import annotations

import random
from copy import deepcopy

from memory_infra.learner import FeedbackLearner
from memory_infra.memory import MemoryItem, MemoryStore
from memory_infra.policy import LearnedPolicy
from memory_infra.retrieval import retrieve

SEEDS = [7, 11, 19, 23, 42]
TASKS = 500
K = 3
QUERY = [1.0, 0.0]
ALPHA0 = 0.5
STEP = 0.05
WINDOW = 50
NOISE_LEVELS = [0.0, 0.05, 0.10, 0.20, 0.30]
FEEDBACK_RATES = [1.0, 0.75, 0.50, 0.25, 0.10]


def build_store(rng: random.Random) -> MemoryStore:
    store = MemoryStore()
    store.add(MemoryItem("near-fail-1", "similar but failed", [1.0, 0.05], failure=8))
    store.add(MemoryItem("near-fail-2", "similar but failed", [0.98, 0.10], failure=6))
    store.add(MemoryItem("far-ok-1", "less similar but worked", [0.72, 0.70], success=8))
    store.add(MemoryItem("far-ok-2", "less similar but worked", [0.70, 0.72], success=7))
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


def true_outcome(memory_id: str, rng: random.Random) -> bool:
    if memory_id.startswith("far-ok"):
        return True
    if memory_id.startswith("near-fail"):
        return False
    return rng.random() < 0.5


def run_one(seed: int, noise: float, feedback_rate: float, adaptive: bool) -> dict:
    store = build_store(random.Random(seed))
    policy = LearnedPolicy(alpha=ALPHA0) if adaptive else None
    learner = FeedbackLearner(step=STEP)
    outcome_rng = random.Random(seed + 1000)
    noise_rng = random.Random(seed + 2000)
    sparse_rng = random.Random(seed + 3000)
    successes: list[int] = []
    precisions: list[float] = []
    wastes: list[float] = []
    alphas: list[float | None] = []
    top1s: list[str] = []
    for t in range(TASKS):
        ranked = retrieve(store, QUERY, policy if adaptive else None, K, task_id=f"s{seed}-t{t}")
        top_ids = [tr.memory_id for tr in ranked]
        top1 = top_ids[0]
        truth = true_outcome(top1, outcome_rng)
        successes.append(int(truth))
        precisions.append(sum(i.startswith("far-ok") for i in top_ids) / K)
        wastes.append(sum(i.startswith("near-fail") for i in top_ids) / K)
        top1s.append(top1)
        if adaptive and policy is not None:
            observed: bool | None = None
            if sparse_rng.random() < feedback_rate:
                observed = truth
                if noise_rng.random() < noise:
                    observed = not observed
            base_top = retrieve(store, QUERY, None, 1, task_id=f"s{seed}-t{t}-base")[0].memory_id
            learner.observe(store, policy, top1, observed, baseline_id=base_top)
            alphas.append(policy.alpha)
        else:
            alphas.append(None)
    last = top1s[-100:]
    mode = max(set(last), key=last.count)
    return {
        "seed": seed,
        "task_success_rate": sum(successes) / TASKS,
        "useful_retrieval_precision": sum(precisions) / TASKS,
        "retrieval_waste": sum(wastes) / TASKS,
        "error_rate": 1 - sum(successes) / TASKS,
        "final_alpha": alphas[-1],
        "top1_last100_mode": mode,
        "top1_last100_stability": last.count(mode) / 100,
        "curve_success": [sum(successes[i:i + WINDOW]) / WINDOW for i in range(0, TASKS, WINDOW)],
        "curve_alpha": [alphas[i + WINDOW - 1] for i in range(0, TASKS, WINDOW)],
    }


def main() -> None:
    print("locked", {"seeds": SEEDS, "tasks": TASKS, "k": K, "alpha0": ALPHA0, "step": STEP})
    for seed in SEEDS:
        row = run_one(seed, 0.0, 1.0, True)
        print("A", seed, round(row["task_success_rate"], 4), row["final_alpha"])


if __name__ == "__main__":
    main()
