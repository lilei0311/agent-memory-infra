from dataclasses import dataclass, field


@dataclass
class RetrievalTrace:
    mode: str
    ids: list[str]
    similarities: list[float]
    scores: list[float]
    notes: dict[str, str] = field(default_factory=dict)
