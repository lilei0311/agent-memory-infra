"""Issue #1 Phase E diagnostic. Does not modify A/B/C/D.

Locked before results. Same seeds, K, alpha, step, cap as Phase D.
Decay is observational only and does not replace V0.1.
"""

from __future__ import annotations

import csv
import math
import random
from collections import Counter, defaultdict
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
POOL = 50
P_LOW = 0.3
P_HIGH = 0.9
SWITCHES = [100, 200, 250, 300, 400]
HALF_LIVES = [None, 500, 250, 100, 50]
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


def outcome_table(seed: int, world: list[dict], switch_at: int) -> dict[tuple[int, str], bool]:
    rng = random.Random(seed + 1000)
    table: dict[tuple[int, str], bool] = {}
    for t in range(TASKS):
        late = t >= switch_at
        for item in world:
            p = item["p_late"] if late else item["p_early"]
            table[(t, item["id"])] = rng.random() < p
    return table


def store_from(world: list[dict]) -> MemoryStore:
    store = MemoryStore()
    for item in world:
        store.add(MemoryItem(item["id"], item["id"], item["embedding"]))
    return store


def apply_decay(store: MemoryStore, events: dict[str, list[tuple[int, bool]]], t: int, half_life: int) -> None:
    for item in store.all():
        success = 0.0
        failure = 0.0
        for ts, ok in events[item.id]:
            weight = 0.5 ** ((t - ts) / half_life)
            if ok:
                success += weight
            else:
                failure += weight
        item.success = success
        item.failure = failure


def run_pair(seed: int, switch_at: int, half_life: int | None) -> dict:
    world = build_world(seed, POOL)
    table = outcome_table(seed, world, switch_at)
    base = store_from(world)
    adap = store_from(world)
    policy = LearnedPolicy(alpha=ALPHA0)
    learner = FeedbackLearner(step=STEP, alpha_max=ALPHA_CAP)
    events: dict[str, list[tuple[int, bool]]] = defaultdict(list)
    b_succ: list[int] = []
    a_succ: list[int] = []
    b_ids: list[str] = []
    a_ids: list[str] = []
    utils: list[float] = []
    scores: list[float] = []
    alphas: list[float] = []
    disagree: list[int] = []
    for t in range(TASKS):
        if half_life is not None:
            apply_decay(adap, events, t, half_life)
        b_top = retrieve(base, QUERY, None, 1, task_id=f"e-b-{seed}-{t}")[0].memory_id
        a_ranked = retrieve(adap, QUERY, policy, K, task_id=f"e-a-{seed}-{t}")
        a_top = a_ranked[0].memory_id
        b_ok = table[(t, b_top)]
        a_ok = table[(t, a_top)]
        b_succ.append(int(b_ok))
        a_succ.append(int(a_ok))
        b_ids.append(b_top)
        a_ids.append(a_top)
        utils.append(adap.get(a_top).utility)
        scores.append(a_ranked[0].scores[0])
        base_top = retrieve(adap, QUERY, None, 1, task_id=f"e-basepick-{seed}-{t}")[0].memory_id
        disagree.append(int(a_top != base_top))
        if half_life is None:
            learner.observe(adap, policy, a_top, a_ok, baseline_id=base_top)
        else:
            events[a_top].append((t, a_ok))
            apply_decay(adap, events, t, half_life)
            if a_top != base_top:
                if a_ok:
                    policy.alpha = min(ALPHA_CAP, policy.alpha + STEP)
                else:
                    policy.alpha = max(0.0, policy.alpha - STEP)
        alphas.append(policy.alpha)
    windows = []
    for i in range(0, TASKS, WINDOW):
        sl = slice(i, i + WINDOW)
        windows.append(
            {
                "window_end": i + WINDOW,
                "baseline_success": sum(b_succ[sl]) / WINDOW,
                "adaptive_success": sum(a_succ[sl]) / WINDOW,
                "selected_memory": Counter(a_ids[sl]).most_common(1)[0][0],
                "utility": sum(utils[sl]) / WINDOW,
                "policy_score": sum(scores[sl]) / WINDOW,
                "alpha": alphas[i + WINDOW - 1],
                "disagreement_rate": sum(disagree[sl]) / WINDOW,
                "unique_top1": len(set(a_ids[sl])),
                "top1_changes": sum(a_ids[j] != a_ids[j - 1] for j in range(max(i, 1), i + WINDOW)),
            }
        )
    post = slice(switch_at, TASKS)
    pre = slice(0, switch_at)
    post_windows = [w for w in windows if w["window_end"] > switch_at and w["window_end"] - WINDOW >= switch_at]
    peak_alpha = max(alphas)
    peak_task = alphas.index(peak_alpha)
    drop_task = next((t for t in range(peak_task, TASKS) if alphas[t] <= 0.0), None)
    reach = next((w["window_end"] for w in post_windows if w["adaptive_success"] >= w["baseline_success"]), None)
    exceed = next((w["window_end"] for w in post_windows if w["adaptive_success"] > w["baseline_success"]), None)
    post_ids = a_ids[post]
    mode, mode_n = Counter(post_ids).most_common(1)[0]
    changes = sum(post_ids[i] != post_ids[i - 1] for i in range(1, len(post_ids)))
    return {
        "seed": seed,
        "switch": switch_at,
        "half_life": "infinite" if half_life is None else half_life,
        "baseline_success": sum(b_succ) / TASKS,
        "adaptive_success": sum(a_succ) / TASKS,
        "pre_baseline": sum(b_succ[pre]) / switch_at,
        "pre_adaptive": sum(a_succ[pre]) / switch_at,
        "post_baseline": sum(b_succ[post]) / (TASKS - switch_at),
        "post_adaptive": sum(a_succ[post]) / (TASKS - switch_at),
        "min_post_adaptive": min(w["adaptive_success"] for w in post_windows),
        "reach_baseline_window": reach,
        "exceed_baseline_window": exceed,
        "peak_alpha": peak_alpha,
        "peak_task": peak_task,
        "alpha_zero_task": drop_task,
        "alpha_drop_tasks": None if drop_task is None else drop_task - peak_task,
        "recovered_final": post_windows[-1]["adaptive_success"] >= post_windows[-1]["baseline_success"],
        "recovered_post_mean": sum(a_succ[post]) >= sum(b_succ[post]),
        "lock_share": mode_n / len(post_ids),
        "locked": mode_n / len(post_ids) >= 0.8,
        "post_top1_changes": changes,
        "post_unique_top1": len(set(post_ids)),
        "disagreement_rate": sum(disagree) / TASKS,
        "post_disagreement": sum(disagree[post]) / (TASKS - switch_at),
        "windows": windows,
    }


def mean(rows: list[dict], key: str) -> float:
    vals = [r[key] for r in rows if isinstance(r[key], (int, float))]
    return sum(vals) / len(vals) if vals else float("nan")


def fmt(x: float | None) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "none"
    return f"{x:.4f}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    e1 = {s: [run_pair(seed, s, None) for seed in SEEDS] for s in SWITCHES}
    e3 = {h: [run_pair(seed, 250, h) for seed in SEEDS] for h in HALF_LIVES}
    curve_rows = []
    for rows in e1.values():
        curve_rows.extend(rows)
    for h, rows in e3.items():
        if h is None:
            continue
        curve_rows.extend(rows)
    fields = [
        "phase", "switch", "half_life", "seed", "window_end", "baseline_success",
        "adaptive_success", "selected_memory", "utility", "policy_score", "alpha",
        "disagreement_rate", "unique_top1", "top1_changes",
    ]
    with (OUT / "phase_e_curves.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in curve_rows:
            phase = "E1" if row["half_life"] == "infinite" else "E3"
            for win in row["windows"]:
                writer.writerow(
                    {
                        "phase": phase,
                        "switch": row["switch"],
                        "half_life": row["half_life"],
                        "seed": row["seed"],
                        **win,
                    }
                )
    lines = [
        "# Issue #1 Phase E",
        "",
        "Diagnostic only. A/B/C/D were not modified. Alpha cap was not raised. No new exploration rule.",
        "",
        "Locked: seeds 7/11/19/23/42, tasks 500, pool 50, K=3, alpha0=0.5, step=0.05, cap=2.0, window=50.",
        "World matches Phase D2: p in [0.3, 0.9], late p = 1.2 - p. V0.1 is infinite half-life.",
        "Decay recomputes utility from event weights 0.5 ** ((t - t_obs) / half_life). Alpha rule is unchanged.",
        "Reach/exceed use post-switch windows only. Locked means post-switch top-1 mode share >= 0.8.",
        "",
        "## E1 staleness severity",
        "",
        "| switch | pre baseline | pre adaptive | post baseline | post adaptive | post delta |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for switch in SWITCHES:
        rows = e1[switch]
        pb, pa = mean(rows, "pre_baseline"), mean(rows, "pre_adaptive")
        ob, oa = mean(rows, "post_baseline"), mean(rows, "post_adaptive")
        lines.append(f"| {switch} | {fmt(pb)} | {fmt(pa)} | {fmt(ob)} | {fmt(oa)} | {fmt(oa - ob)} |")
    lines += [
        "",
        "## E2 recovery",
        "",
        "| switch | min post adaptive | mean reach window | mean exceed window | mean alpha drop tasks | seeds alpha to 0 | final recovered | post-mean recovered |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for switch in SWITCHES:
        rows = e1[switch]
        reach = [r["reach_baseline_window"] for r in rows if r["reach_baseline_window"] is not None]
        exceed = [r["exceed_baseline_window"] for r in rows if r["exceed_baseline_window"] is not None]
        drop = [r["alpha_drop_tasks"] for r in rows if r["alpha_drop_tasks"] is not None]
        zeros = sum(r["alpha_zero_task"] is not None for r in rows)
        final = sum(r["recovered_final"] for r in rows)
        post = sum(r["recovered_post_mean"] for r in rows)
        lines.append(
            f"| {switch} | {fmt(mean(rows, 'min_post_adaptive'))} | {fmt(sum(reach) / len(reach) if reach else None)} | {fmt(sum(exceed) / len(exceed) if exceed else None)} | {fmt(sum(drop) / len(drop) if drop else None)} | {zeros}/5 | {final}/5 | {post}/5 |"
        )
    lines += [
        "",
        "Switch 250 per seed, V0.1:",
        "",
        "| seed | pre a | post a | post b | min post | reach | exceed | peak alpha | drop tasks | final recovered | lock share | post changes | post unique | post disagree |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in e1[250]:
        lines.append(
            f"| {r['seed']} | {fmt(r['pre_adaptive'])} | {fmt(r['post_adaptive'])} | {fmt(r['post_baseline'])} | {fmt(r['min_post_adaptive'])} | {r['reach_baseline_window']} | {r['exceed_baseline_window']} | {fmt(r['peak_alpha'])} | {r['alpha_drop_tasks']} | {r['recovered_final']} | {fmt(r['lock_share'])} | {r['post_top1_changes']} | {r['post_unique_top1']} | {fmt(r['post_disagreement'])} |"
        )
    lines += [
        "",
        "## E3 decay diagnostic, switch 250",
        "",
        "| half-life | pre adaptive | post baseline | post adaptive | post delta | min post | seeds alpha to 0 | final recovered | post-mean recovered |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for h in HALF_LIVES:
        rows = e3[h]
        label = "infinite" if h is None else str(h)
        ob, oa = mean(rows, "post_baseline"), mean(rows, "post_adaptive")
        lines.append(
            f"| {label} | {fmt(mean(rows, 'pre_adaptive'))} | {fmt(ob)} | {fmt(oa)} | {fmt(oa - ob)} | {fmt(mean(rows, 'min_post_adaptive'))} | {sum(r['alpha_zero_task'] is not None for r in rows)}/5 | {sum(r['recovered_final'] for r in rows)}/5 | {sum(r['recovered_post_mean'] for r in rows)}/5 |"
        )
    lines += [
        "",
        "Seed 7 recovery windows, switch 250:",
        "",
        "| half-life | window | baseline | adaptive | selected | utility | score | alpha | disagree | unique |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for h in HALF_LIVES:
        row = e3[h][0]
        label = "infinite" if h is None else str(h)
        for w in row["windows"]:
            if w["window_end"] < 250:
                continue
            lines.append(
                f"| {label} | {w['window_end']} | {fmt(w['baseline_success'])} | {fmt(w['adaptive_success'])} | {w['selected_memory']} | {fmt(w['utility'])} | {fmt(w['policy_score'])} | {fmt(w['alpha'])} | {fmt(w['disagreement_rate'])} | {w['unique_top1']} |"
            )
    lines += [
        "",
        "## E4 exploration diagnosis, V0.1",
        "",
        "| switch | seeds locked | mean lock share | mean post top1 changes | mean post unique | mean post disagree |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for switch in SWITCHES:
        rows = e1[switch]
        lines.append(
            f"| {switch} | {sum(r['locked'] for r in rows)}/5 | {fmt(mean(rows, 'lock_share'))} | {fmt(mean(rows, 'post_top1_changes'))} | {fmt(mean(rows, 'post_unique_top1'))} | {fmt(mean(rows, 'post_disagreement'))} |"
        )
    lines += [
        "",
        "## Reading",
        "",
        "E1 post delta is the staleness severity at each switch. A negative delta means historical utility hurt after the flip.",
        "E2 recovery is a post-switch window at or above that window's baseline, not a claim that the old memory became valid again.",
        "E3 infinite is V0.1. Shorter half-life is a diagnostic scan, not a selected algorithm.",
        "E4 lock and low disagreement mean the current rule cannot leave a memory unless baseline disagreement and failures pull alpha down.",
        "Do not start cold-start, distribution-shift, or Stage 2 from this run.",
        "",
    ]
    (OUT / "phase_e.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
