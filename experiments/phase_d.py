"""Issue #1 Phase D. Does not modify Phase A/B/C worlds or results.

Locked before results. Do not retune seeds, alpha, step, cap, K, or
the success band to make adaptive win. Alpha cap stays 2.0.
"""

from __future__ import annotations

import csv
import math
import random
from collections import Counter
from copy import deepcopy
from pathlib import Path

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
ALPHA_CAP = 2.0
WINDOW = 50
P_LOW = 0.3
P_HIGH = 0.9
SWITCH_AT = 250
D1_POOL = 50
D3_POOLS = [10, 50, 100, 500, 1000]
OUT = Path(__file__).resolve().parent / "results"


def build_world(seed: int, n: int) -> list[dict]:
    rng = random.Random(seed)
    items = []
    for i in range(n):
        angle = (2 * math.pi * i) / n + rng.uniform(-0.05, 0.05)
        p = rng.uniform(P_LOW, P_HIGH)
        items.append(
            {
                "id": f"m{i:04d}",
                "embedding": [math.cos(angle), math.sin(angle)],
                "p_early": p,
                "p_late": (P_LOW + P_HIGH) - p,
            }
        )
    return items


def outcome_table(seed: int, world: list[dict], nonstationary: bool) -> dict[tuple[int, str], bool]:
    rng = random.Random(seed + 1000)
    table: dict[tuple[int, str], bool] = {}
    for t in range(TASKS):
        late = nonstationary and t >= SWITCH_AT
        for item in world:
            p = item["p_late"] if late else item["p_early"]
            table[(t, item["id"])] = rng.random() < p
    return table


def store_from(world: list[dict]) -> MemoryStore:
    store = MemoryStore()
    for item in world:
        store.add(MemoryItem(item["id"], item["id"], item["embedding"]))
    return store


def run_pair(seed: int, n: int, nonstationary: bool) -> dict:
    world = build_world(seed, n)
    table = outcome_table(seed, world, nonstationary)
    base = store_from(world)
    adap = store_from(world)
    policy = LearnedPolicy(alpha=ALPHA0)
    learner = FeedbackLearner(step=STEP, alpha_max=ALPHA_CAP)
    b_succ: list[int] = []
    a_succ: list[int] = []
    b_ids: list[str] = []
    a_ids: list[str] = []
    utils: list[float] = []
    scores: list[float] = []
    alphas: list[float] = []
    sat_task = None
    for t in range(TASKS):
        b_ranked = retrieve(base, QUERY, None, K, task_id=f"d-b-{seed}-{t}")
        a_ranked = retrieve(adap, QUERY, policy, K, task_id=f"d-a-{seed}-{t}")
        b_top = b_ranked[0].memory_id
        a_top = a_ranked[0].memory_id
        b_ok = table[(t, b_top)]
        a_ok = table[(t, a_top)]
        b_succ.append(int(b_ok))
        a_succ.append(int(a_ok))
        b_ids.append(b_top)
        a_ids.append(a_top)
        item = adap.get(a_top)
        utils.append(item.utility)
        scores.append(a_ranked[0].scores[0])
        base_top = retrieve(adap, QUERY, None, 1, task_id=f"d-basepick-{seed}-{t}")[0].memory_id
        learner.observe(adap, policy, a_top, a_ok, baseline_id=base_top)
        alphas.append(policy.alpha)
        if sat_task is None and policy.alpha >= ALPHA_CAP:
            sat_task = t
    windows = []
    for i in range(0, TASKS, WINDOW):
        sl = slice(i, i + WINDOW)
        a_mode = Counter(a_ids[sl]).most_common(1)[0][0]
        windows.append(
            {
                "window_end": i + WINDOW,
                "baseline_success": sum(b_succ[sl]) / WINDOW,
                "adaptive_success": sum(a_succ[sl]) / WINDOW,
                "selected_memory": a_mode,
                "baseline_selected": Counter(b_ids[sl]).most_common(1)[0][0],
                "utility": sum(utils[sl]) / WINDOW,
                "policy_score": sum(scores[sl]) / WINDOW,
                "alpha": alphas[i + WINDOW - 1],
            }
        )
    learn_at = next(
        (w["window_end"] for w in windows if w["adaptive_success"] > w["baseline_success"] + 0.02),
        None,
    )
    drop_at = None
    peak = windows[0]["adaptive_success"]
    for w in windows[1:]:
        peak = max(peak, w["adaptive_success"])
        if peak - w["adaptive_success"] >= 0.08:
            drop_at = w["window_end"]
            break
    return {
        "seed": seed,
        "pool": n,
        "nonstationary": nonstationary,
        "baseline_success": sum(b_succ) / TASKS,
        "adaptive_success": sum(a_succ) / TASKS,
        "final_alpha": alphas[-1],
        "alpha_sat_task": sat_task,
        "learn_window_end": learn_at,
        "degrade_window_end": drop_at,
        "pre_switch_adaptive": sum(a_succ[:SWITCH_AT]) / SWITCH_AT,
        "post_switch_adaptive": sum(a_succ[SWITCH_AT:]) / (TASKS - SWITCH_AT),
        "pre_switch_baseline": sum(b_succ[:SWITCH_AT]) / SWITCH_AT,
        "post_switch_baseline": sum(b_succ[SWITCH_AT:]) / (TASKS - SWITCH_AT),
        "windows": windows,
        "alpha_trace_seed_only": alphas,
    }


def mean(rows: list[dict], key: str) -> float:
    vals = [r[key] for r in rows if r[key] is not None]
    return sum(vals) / len(vals) if vals else float("nan")


def write_curves(path: Path, rows: list[dict]) -> None:
    fields = [
        "phase", "pool", "nonstationary", "seed", "window_end",
        "baseline_success", "adaptive_success", "selected_memory",
        "baseline_selected", "utility", "policy_score", "alpha",
    ]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            for win in row["windows"]:
                w.writerow(
                    {
                        "phase": row["phase"],
                        "pool": row["pool"],
                        "nonstationary": row["nonstationary"],
                        "seed": row["seed"],
                        **win,
                    }
                )


def fmt(x: float | None) -> str:
    if x is None:
        return "none"
    return f"{x:.4f}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    d1 = [run_pair(s, D1_POOL, False) for s in SEEDS]
    d2 = [run_pair(s, D1_POOL, True) for s in SEEDS]
    d3 = {n: [run_pair(s, n, False) for s in SEEDS] for n in D3_POOLS}
    for row in d1:
        row["phase"] = "D1"
    for row in d2:
        row["phase"] = "D2"
    curve_rows = d1 + d2
    for n, rows in d3.items():
        for row in rows:
            row["phase"] = "D3"
        curve_rows.extend(rows)
    write_curves(OUT / "phase_d_curves.csv", curve_rows)

    lines = [
        "# Issue #1 Phase D",
        "",
        "A/B/C results were not modified. Alpha cap was not raised.",
        "",
        "Locked config: seeds 7/11/19/23/42, tasks 500, K=3, alpha0=0.5, step=0.05, cap=2.0, window=50.",
        "Success probability is continuous in [0.3, 0.9], independent of cosine. Initial counts are 0.",
        "Baseline and adaptive share the candidate set, seed, and Bernoulli table. Baseline store is not updated.",
        "D1/D2 pool is 50. D2 flips p to 1.2-p at task 250. D3 uses the stationary D1 rule.",
        "",
        "## D1 continuous utility",
        "",
        f"mean baseline {fmt(mean(d1, 'baseline_success'))} adaptive {fmt(mean(d1, 'adaptive_success'))}",
        f"mean final alpha {fmt(mean(d1, 'final_alpha'))}",
        "",
        "| seed | baseline | adaptive | final alpha | sat task | learn window | degrade window |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in d1:
        lines.append(
            f"| {r['seed']} | {fmt(r['baseline_success'])} | {fmt(r['adaptive_success'])} | {fmt(r['final_alpha'])} | {r['alpha_sat_task']} | {r['learn_window_end']} | {r['degrade_window_end']} |"
        )
    lines += [
        "",
        "Seed 7 windows:",
        "",
        "| window | baseline | adaptive | selected | utility | score | alpha |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for w in d1[0]["windows"]:
        lines.append(
            f"| {w['window_end']} | {fmt(w['baseline_success'])} | {fmt(w['adaptive_success'])} | {w['selected_memory']} | {fmt(w['utility'])} | {fmt(w['policy_score'])} | {fmt(w['alpha'])} |"
        )
    lines += [
        "",
        "## D2 non-stationary",
        "",
        f"mean baseline {fmt(mean(d2, 'baseline_success'))} adaptive {fmt(mean(d2, 'adaptive_success'))}",
        f"pre switch baseline/adaptive {fmt(mean(d2, 'pre_switch_baseline'))} / {fmt(mean(d2, 'pre_switch_adaptive'))}",
        f"post switch baseline/adaptive {fmt(mean(d2, 'post_switch_baseline'))} / {fmt(mean(d2, 'post_switch_adaptive'))}",
        "",
        "| seed | baseline | adaptive | pre a | post a | sat task | learn window | degrade window |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in d2:
        lines.append(
            f"| {r['seed']} | {fmt(r['baseline_success'])} | {fmt(r['adaptive_success'])} | {fmt(r['pre_switch_adaptive'])} | {fmt(r['post_switch_adaptive'])} | {r['alpha_sat_task']} | {r['learn_window_end']} | {r['degrade_window_end']} |"
        )
    lines += [
        "",
        "Seed 7 windows:",
        "",
        "| window | baseline | adaptive | selected | utility | score | alpha |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for w in d2[0]["windows"]:
        lines.append(
            f"| {w['window_end']} | {fmt(w['baseline_success'])} | {fmt(w['adaptive_success'])} | {w['selected_memory']} | {fmt(w['utility'])} | {fmt(w['policy_score'])} | {fmt(w['alpha'])} |"
        )
    lines += [
        "",
        "## D3 pool sweep",
        "",
        "| pool | baseline | adaptive | delta | mean sat task | seeds saturated |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for n in D3_POOLS:
        rows = d3[n]
        sats = [r["alpha_sat_task"] for r in rows if r["alpha_sat_task"] is not None]
        b = mean(rows, "baseline_success")
        a = mean(rows, "adaptive_success")
        sat_mean = sum(sats) / len(sats) if sats else float("nan")
        lines.append(
            f"| {n} | {fmt(b)} | {fmt(a)} | {fmt(a - b)} | {fmt(sat_mean)} | {len(sats)}/{len(rows)} |"
        )
    lines += [
        "",
        "## Reading",
        "",
        "Discrimination is whether adaptive success separates from baseline on the same Bernoulli table, not whether alpha moves.",
        "Alpha saturation remains a limitation of the current rule. Cap was not raised.",
        "D2 post-switch drop, if present, is historical utility becoming stale. Cumulative counts do not forget.",
        "D3 delta versus pool size is the distractor degradation curve.",
        "Do not start cold-start, distribution-shift, or Stage 2 from this run.",
        "",
    ]
    (OUT / "phase_d.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
