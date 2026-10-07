"""Phase H locked dynamics harness.

Isolates mechanism conditions. Does not call attention observe(), and does
not change Phase G seeds, stream, budget, or policies.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from memory_infra.graph import GraphMemory, Lifecycle

SEEDS = [7, 11, 19]
BUDGET = 4
POLICY = "none"
CONDITIONS = (
    "event_identity",
    "thread_lifecycle",
    "memory_lifecycle",
    "evidence_integrity",
    "deterministic_replay",
)


def _graph(seed: int) -> GraphMemory:
    return GraphMemory(seed=seed, context_budget=BUDGET, policy=POLICY)



def _relation_rows(graph: GraphMemory) -> list[dict]:
    return [
        {
            "relation_type": rel.relation_type,
            "source_id": rel.source_id,
            "target_id": rel.target_id,
            "evidence_ref": rel.evidence_ref,
        }
        for rel in graph.relations.values()
    ]


def trace_digest(graph: GraphMemory) -> str:
    payload = json.dumps(graph.snapshot()["trace"], sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def run_event_identity(seed: int) -> dict:
    g = _graph(seed)
    first = g.promote(g.add_point("same observation").point_id, "task-relevance")
    second = g.promote(g.add_point("same observation").point_id, "repeated-reference")
    return {
        "distinct_events": first.event_id != second.event_id,
        "distinct_evidence": first.evidence_ref != second.evidence_ref,
        "event_count": len(g.events),
        "trace": g.snapshot()["trace"],
        "trace_digest": trace_digest(g),
    }


def run_thread_lifecycle(seed: int) -> dict:
    g = _graph(seed)
    root = g.promote(g.add_point("start").point_id, "task-relevance")
    thread = g.open_thread(root.event_id, "alpha", goal="track")
    extra = g.promote(g.add_point("continue").point_id, "repeated-reference")
    g.extend(thread.thread_id, extra.event_id, "same-topic")
    branch_event = g.promote(g.add_point("branch").point_id, "divergent-goal")
    g.extend(thread.thread_id, branch_event.event_id, "same-topic")
    child = g.split(thread.thread_id, branch_event.event_id, "beta")
    other = g.promote(g.add_point("other").point_id, "task-relevance")
    other_thread = g.open_thread(other.event_id, "gamma")
    before = list(other_thread.member_event_ids)
    merged = g.merge(thread.thread_id, other_thread.thread_id, "same-goal")
    right_status_after_merge = g.threads[other_thread.thread_id].status
    reopened = g.reopen(other_thread.thread_id, "later-reference")
    kinds = {row.kind for row in g.log}
    return {
        "created": "thread.create" in kinds,
        "extended": "thread.extend" in kinds,
        "split": "thread.split" in kinds,
        "merged_status": right_status_after_merge == "merged",
        "right_status_after_merge": right_status_after_merge,
        "left_absorbed_right_member": bool(before) and before[0] in merged.member_event_ids,
        "reopened": reopened.status == "active",
        "members_unchanged_on_reopen": g.threads[other_thread.thread_id].member_event_ids == before,
        "child_topic": child.topic,
        "not_topic_return": all(row.reason != "topic-return-restore" for row in g.log),
        "relations": _relation_rows(g),
        "trace": g.snapshot()["trace"],
        "trace_digest": trace_digest(g),
    }


def run_memory_lifecycle(seed: int) -> dict:
    g = _graph(seed)
    event = g.promote(g.add_point("rule").point_id, "task-relevance")
    eid = event.event_id
    g.consolidate(eid, "repeat")
    g.retrieve("rule")
    g.begin_reconsolidation(eid, "after-retrieval")
    g.resolve_reconsolidation(eid, "confirm", "confirmed")
    confirmed = g.states[eid].lifecycle_state == Lifecycle.STABLE
    revised = g.promote(g.add_point("revise-me").point_id, "task-relevance")
    g.consolidate(revised.event_id, "repeat")
    g.retrieve("revise-me")
    g.begin_reconsolidation(revised.event_id, "after-retrieval")
    g.resolve_reconsolidation(revised.event_id, "revise", "new-outcome")
    weakened = g.promote(g.add_point("weaken-me").point_id, "task-relevance")
    g.consolidate(weakened.event_id, "repeat")
    g.retrieve("weaken-me")
    g.begin_reconsolidation(weakened.event_id, "after-retrieval")
    g.resolve_reconsolidation(weakened.event_id, "weaken", "conflict")
    dormant = g.promote(g.add_point("sleep").point_id, "task-relevance")
    g.consolidate(dormant.event_id, "repeat")
    g.decay(dormant.event_id)
    dormant_state = g.states[dormant.event_id].lifecycle_state.value
    evidence_before = g.events[dormant.event_id].evidence_ref
    g.retrieve("sleep")
    reactivated = g.states[dormant.event_id].lifecycle_state.value
    buried = g.promote(g.add_point("bury").point_id, "task-relevance")
    g.consolidate(buried.event_id, "repeat")
    g.decay(buried.event_id)
    g.decay(buried.event_id)
    inaccessible = g.states[buried.event_id].lifecycle_state.value
    buried_evidence = g.events[buried.event_id].evidence_ref
    pairs = {(row.source_state, row.target_state) for row in g.log if row.kind == "lifecycle"}
    return {
        "confirm": confirmed,
        "revise": g.states[revised.event_id].lifecycle_state == Lifecycle.UPDATED,
        "weaken": g.states[weakened.event_id].lifecycle_state == Lifecycle.WEAKENED,
        "dormant_before_retrieval": dormant_state,
        "reactivated": reactivated,
        "inaccessible": inaccessible,
        "evidence_kept": g.events[dormant.event_id].evidence_ref == evidence_before and bool(buried_evidence),
        "pairs": sorted(pairs),
        "trace": g.snapshot()["trace"],
        "trace_digest": trace_digest(g),
    }


def run_evidence_integrity(seed: int) -> dict:
    g = _graph(seed)
    left = g.promote(g.add_point("tea").point_id, "task-relevance")
    right = g.promote(g.add_point("coffee").point_id, "contradiction-signal")
    thread = g.open_thread(left.event_id, "drinks")
    g.extend(thread.thread_id, right.event_id, "same-topic")
    contra = g.contradict(left.event_id, right.event_id, "both-observed")
    causal = g.link_causal(right.event_id, left.event_id, "causal.caused_by", "observed-order", inferred=False)
    types = sorted({rel.relation_type for rel in g.relations.values()})
    return {
        "both_events_present": left.event_id in g.events and right.event_id in g.events,
        "distinct_evidence": left.evidence_ref != right.evidence_ref,
        "contradiction": contra.relation_type,
        "causal": causal.relation_type,
        "relation_types": types,
        "relations": _relation_rows(g),
        "endpoints_unchanged": g.events[left.event_id].observation == "tea" and g.events[right.event_id].observation == "coffee",
        "trace": g.snapshot()["trace"],
        "trace_digest": trace_digest(g),
    }


def run_replay(seed: int) -> dict:
    left = [run_event_identity(seed), run_thread_lifecycle(seed), run_memory_lifecycle(seed), run_evidence_integrity(seed)]
    right = [run_event_identity(seed), run_thread_lifecycle(seed), run_memory_lifecycle(seed), run_evidence_integrity(seed)]
    return {
        "match": left == right,
        "digests": [row["trace_digest"] for row in left],
    }


def run_seed(seed: int) -> dict:
    return {
        "seed": seed,
        "event_identity": run_event_identity(seed),
        "thread_lifecycle": run_thread_lifecycle(seed),
        "memory_lifecycle": run_memory_lifecycle(seed),
        "evidence_integrity": run_evidence_integrity(seed),
        "deterministic_replay": run_replay(seed),
    }


def main() -> None:
    print("locked", {"seeds": SEEDS, "budget": BUDGET, "policy": POLICY, "conditions": CONDITIONS})
    artifact = {
        "seeds": SEEDS,
        "budget": BUDGET,
        "policy": POLICY,
        "conditions": list(CONDITIONS),
        "runs": [],
    }
    for seed in SEEDS:
        row = run_seed(seed)
        traces = {}
        for name in ("event_identity", "thread_lifecycle", "memory_lifecycle", "evidence_integrity"):
            traces[name] = row[name].pop("trace")
        artifact["runs"].append({"seed": seed, "traces": traces})
        print(json.dumps(row, sort_keys=True))
    path = Path(__file__).resolve().parent / "results" / "phase_h_trace.json"
    payload = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    path.write_text(payload)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    print("trace_artifact", str(path), digest)


if __name__ == "__main__":
    main()
