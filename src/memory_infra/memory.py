from dataclasses import dataclass, field

from memory_infra.dedup import ItemDedupPolicy, item_key, resolve_action


@dataclass
class MemoryItem:
    id: str
    text: str
    embedding: list[float]
    tags: list[str] = field(default_factory=list)
    success: int = 0
    failure: int = 0

    @property
    def utility(self) -> float:
        """Historical usefulness in [-1, 1].

        Laplace-smoothed so a single failure cannot fully erase
        a memory with a long success history (sparse-feedback guard).
        """
        return (self.success - self.failure) / (self.success + self.failure + 1)


@dataclass(frozen=True)
class StoreDedupResult:
    """Outcome of ``MemoryStore.add_deduped``.

    ``action`` is ``added``, ``skipped``, ``merged``, or ``kept_latest``.
    ``item`` is the item kept in the store.
    """

    action: str
    item: MemoryItem
    key: str


class MemoryStore:
    def __init__(self) -> None:
        self.items: dict[str, MemoryItem] = {}
        # Content key -> id. Only ``add_deduped`` writes this index.
        self._dedup_keys: dict[str, str] = {}

    def add(self, item: MemoryItem) -> None:
        """Store by id. Same id overwrites. Same text does not collapse.

        Experiments rely on this. Content dedup is ``add_deduped``.
        """

        self.items[item.id] = item

    def add_deduped(self, item: MemoryItem, policy: ItemDedupPolicy | None = None) -> StoreDedupResult:
        """Store a copy of ``item`` under ``policy`` (default ``skip`` + near).

        A new content key inserts the copy. An existing key follows the
        policy and keeps the original id. ``add`` and ``add_deduped`` do not
        share an index: an item inserted only with ``add`` is invisible here.
        """

        chosen = policy if policy is not None else ItemDedupPolicy()
        key = item_key(item.text, near=chosen.near)
        existing_id = self._dedup_keys.get(key)
        if existing_id is None:
            if item.id in self.items:
                raise ValueError(f"memory id already stored: {item.id}")
            stored = MemoryItem(
                item.id,
                item.text,
                list(item.embedding),
                tags=list(item.tags),
                success=item.success,
                failure=item.failure,
            )
            self.items[item.id] = stored
            self._dedup_keys[key] = item.id
            return StoreDedupResult("added", stored, key)
        existing = self.items[existing_id]
        action = resolve_action(chosen, existing.text, item.text)
        if action == "skip":
            return StoreDedupResult("skipped", existing, key)
        if action == "merge":
            for tag in item.tags:
                if tag not in existing.tags:
                    existing.tags.append(tag)
            existing.success += item.success
            existing.failure += item.failure
            return StoreDedupResult("merged", existing, key)
        if action != "keep_latest":
            raise RuntimeError(f"unexpected dedup action: {action}")
        existing.text = item.text
        existing.embedding = list(item.embedding)
        existing.tags = list(item.tags)
        existing.success = item.success
        existing.failure = item.failure
        return StoreDedupResult("kept_latest", existing, key)

    def get(self, item_id: str) -> MemoryItem:
        return self.items[item_id]

    def all(self) -> list[MemoryItem]:
        return list(self.items.values())
