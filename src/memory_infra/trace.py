from dataclasses import dataclass, field


@dataclass
class RetrievalTrace:
    """One trace describes one memory-task interaction.

    Fields follow docs/PROTOCOLS.md Trace section:
    - trace_id, task_id, memory_id, retrieved, rank
    - used, task_success, user_feedback, policy_version
    - missing signals are unknown (None), never guessed
    - traces are append-only; raw conversation is not stored
    """

    trace_id: str
    task_id: str
    memory_id: str
    retrieved: bool
    rank: int
    mode: str
    policy_version: str
    used: bool | None = None
    task_success: bool | None = None
    user_feedback: float | None = None
    similarities: list[float] = field(default_factory=list)
    scores: list[float] = field(default_factory=list)
    notes: dict[str, str] = field(default_factory=dict)
