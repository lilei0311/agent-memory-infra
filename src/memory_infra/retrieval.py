from memory_infra.memory import MemoryItem, MemoryStore
from memory_infra.policy import LearnedPolicy
from memory_infra.trace import RetrievalTrace


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def retrieve(
    store: MemoryStore,
    query: list[float],
    policy: LearnedPolicy | None = None,
    k: int = 3,
    task_id: str = "unknown",
) -> list[RetrievalTrace]:
    """Rank memories and return one trace per retrieved item.

    Baseline: score = cosine similarity.
    Adaptive: score = similarity + alpha * utility.
    """
    scored: list[tuple[MemoryItem, float, float]] = []
    for item in store.all():
        sim = cosine(query, item.embedding)
        score = sim if policy is None else policy.score(sim, item.utility)
        scored.append((item, sim, score))
    scored.sort(key=lambda row: row[2], reverse=True)
    top = scored[:k]
    mode = "baseline" if policy is None else "policy"
    policy_version = "baseline-v0.1" if policy is None else f"adaptive-v0.1-alpha{policy.alpha}"
    return [
        RetrievalTrace(
            trace_id=f"{task_id}-{item.id}",
            task_id=task_id,
            memory_id=item.id,
            retrieved=True,
            rank=rank,
            mode=mode,
            policy_version=policy_version,
            similarities=[sim],
            scores=[score],
        )
        for rank, (item, sim, score) in enumerate(top, start=1)
    ]
