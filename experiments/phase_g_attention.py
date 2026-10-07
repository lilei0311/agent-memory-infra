"""Issue 6 attention comparison. Config locked before the run."""

from memory_infra.graph import GraphMemory, Signals

SEEDS = [7, 11, 19, 23, 42]
BUDGET = 4
POLICIES = ("none", "focus", "divergent", "automatic")
STREAM = [
    ("T1", False), ("T1", False), ("T2", False), ("T3", False), ("T1", False),
    ("T2", True), ("T3", True), ("T1", False), ("T4", True), ("T1", False),
]


def run(seed: int, policy: str) -> dict:
    g = GraphMemory(seed=seed, context_budget=BUDGET, policy=policy)
    threads = {}
    for topic in ("T1", "T2", "T3", "T4"):
        first = g.promote(g.add_point(topic).point_id, "task-relevance")
        threads[topic] = g.open_thread(first.event_id, topic).thread_id
        for n in range(2):
            extra = g.promote(g.add_point(f"{topic}-{n}").point_id, "repeated-reference")
            g.extend(threads[topic], extra.event_id, "same-topic")
    target_hits = other = switches = recovered = 0
    diversities = []
    active_counts = []
    cross = 0
    used = 0
    prev = None
    for topic, diverge in STREAM:
        g.observe(Signals(
            topic=topic,
            topic_continuity=prev == topic,
            topic_switch=prev is not None and prev != topic,
            thread_reference=threads[topic],
            divergence=diverge,
        ))
        ctx = g.assemble(topic)
        used += len(ctx) / BUDGET
        threads_in = {i.thread_id for i in ctx}
        target = threads[topic]
        target_hits += sum(1 for i in ctx if i.thread_id == target) / max(1, len(ctx))
        other += sum(1 for i in ctx if i.thread_id != target) / max(1, len(ctx))
        if len(threads_in) > 1:
            cross += 1
        diversities.append(len(threads_in) / 4)
        active_counts.append(len(threads_in))
        if prev and prev != topic:
            switches += 1
            if any(i.thread_id == target for i in ctx):
                recovered += 1
        prev = topic
    return {
        "target_thread_precision": target_hits / len(STREAM),
        "irrelevant_context_ratio": other / len(STREAM),
        "cross_thread_contamination": cross / len(STREAM),
        "topic_switch_recovery": recovered / switches,
        "context_budget_utilization": used / len(STREAM),
        "divergent_active_thread_count": sum(active_counts) / len(active_counts),
        "diversity": sum(diversities) / len(diversities),
        "cross_thread_retrieval_rate": cross / len(STREAM),
    }


def mean(rows, key):
    return sum(r[key] for r in rows) / len(rows)


def main() -> None:
    print("locked", {"seeds": SEEDS, "budget": BUDGET, "stream": len(STREAM)})
    for policy in POLICIES:
        rows = [run(s, policy) for s in SEEDS]
        print(policy, {k: round(mean(rows, k), 4) for k in rows[0]})


if __name__ == "__main__":
    main()
