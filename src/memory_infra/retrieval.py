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
) -> RetrievalTrace:
    scored: list[tuple[MemoryItem, float, float]] = []
    for item in store.all():
        sim = cosine(query, item.embedding)
        score = sim if policy is None else policy.score(sim, item.utility)
        scored.append((item, sim, score))
    scored.sort(key=lambda row: row[2], reverse=True)
    top = scored[:k]
    return RetrievalTrace(
        mode="baseline" if policy is None else "policy",
        ids=[item.id for item, _, _ in top],
        similarities=[sim for _, sim, _ in top],
        scores=[score for _, _, score in top],
    )
