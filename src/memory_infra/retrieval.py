import re
from collections import Counter

from memory_infra.memory import MemoryItem, MemoryStore
from memory_infra.policy import LearnedPolicy
from memory_infra.trace import RetrievalTrace

_TOKEN = re.compile(r"[a-z0-9]+")


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def text_relevance(query: str, text: str) -> float:
    """Bag-of-words cosine between a query string and observation text.

    Tokens are lowercase alphanumeric runs. The vector cosine is the
    existing ``cosine`` helper. This does not change ``retrieve`` (the
    frozen V0.1 cosine-plus-utility policy layer).
    """

    if not query or not text:
        return 0.0
    query_counts = Counter(_TOKEN.findall(query.lower()))
    text_counts = Counter(_TOKEN.findall(text.lower()))
    if not query_counts or not text_counts:
        return 0.0
    vocab = sorted(set(query_counts) | set(text_counts))
    query_vec = [float(query_counts[token]) for token in vocab]
    text_vec = [float(text_counts[token]) for token in vocab]
    return cosine(query_vec, text_vec)


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
