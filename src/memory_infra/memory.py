from dataclasses import dataclass, field


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


class MemoryStore:
    def __init__(self) -> None:
        self.items: dict[str, MemoryItem] = {}

    def add(self, item: MemoryItem) -> None:
        self.items[item.id] = item

    def get(self, item_id: str) -> MemoryItem:
        return self.items[item_id]

    def all(self) -> list[MemoryItem]:
        return list(self.items.values())
