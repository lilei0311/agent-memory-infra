"""Stage 8 Skill/API packaging seam.

In-process, transport-neutral capability boundary over CallerSession.
The seam binds caller identity and forwards observations/signals/reads.
It does not own IDs, lifecycle, thread membership, relations, trace,
attention, or durable transitions.
"""

from __future__ import annotations

from typing import Mapping

from memory_infra.store import CallerSession, MemoryService, SnapshotError

SUPPORTED_OPS = (
    "observe",
    "signal",
    "retrieve",
    "read_lifecycle",
    "read_event",
    "read_relations",
    "inspect_trace",
    "read_caller_context",
    "save",
    "load",
)


class SkillApi:
    """Public capability surface. Holds no durable mechanism state."""

    def __init__(self, service: MemoryService) -> None:
        self._service = service

    def invoke(self, caller_id: str, op: str, payload: Mapping | None = None) -> Mapping:
        if op not in SUPPORTED_OPS:
            raise SnapshotError("unsupported skill operation")
        session = CallerSession(self._service, caller_id)
        return session.request(op, payload)

    def open_caller(self, caller_id: str) -> SkillCaller:
        return SkillCaller(self, caller_id)


class SkillCaller:
    """Bound caller handle. Local to the seam; not a second state owner."""

    def __init__(self, api: SkillApi, caller_id: str) -> None:
        self._api = api
        self.caller_id = caller_id

    def invoke(self, op: str, payload: Mapping | None = None) -> Mapping:
        return self._api.invoke(self.caller_id, op, payload)
