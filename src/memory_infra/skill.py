"""Stage 8 Skill/API packaging seam.

In-process, transport-neutral capability boundary over CallerSession.
The seam binds caller identity and forwards observations/signals/reads.
It does not own IDs, lifecycle, thread membership, relations, trace,
attention, or durable transitions.

Process restart is a packaging handoff: reopen() builds a new SkillApi
over a new MemoryService and supplies the mechanism-owned seal out of
band. It does not return the seal and does not allocate mechanism ids.
"""

from __future__ import annotations

from typing import Mapping

from memory_infra.bootstrap import SkillBootstrap

from memory_infra.store import (
    CallerSession,
    FileDurableStore,
    InMemoryDurableStore,
    MemoryService,
    SnapshotError,
    _restart_capability,
)

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

__all__ = ["SUPPORTED_OPS", "SkillApi", "SkillBootstrap", "SkillCaller", "SnapshotError"]


class SkillApi:
    """Public capability surface. Holds no durable mechanism state."""

    def __init__(
        self,
        service: MemoryService,
        *,
        seed: int = 7,
        context_budget: int = 4,
        policy: str = "none",
    ) -> None:
        self._service = service
        self._seed = seed
        self._budget = context_budget
        self._policy = policy

    @classmethod
    def open_memory(
        cls,
        *,
        seed: int = 7,
        context_budget: int = 4,
        policy: str = "none",
    ) -> "SkillApi":
        service = MemoryService(
            store=InMemoryDurableStore(),
            seed=seed,
            context_budget=context_budget,
            policy=policy,
        )
        return cls(service, seed=seed, context_budget=context_budget, policy=policy)

    @classmethod
    def open_file(
        cls,
        path,
        *,
        seed: int = 7,
        context_budget: int = 4,
        policy: str = "none",
    ) -> "SkillApi":
        service = MemoryService(
            store=FileDurableStore(path),
            seed=seed,
            context_budget=context_budget,
            policy=policy,
        )
        return cls(service, seed=seed, context_budget=context_budget, policy=policy)

    def reopen(self) -> "SkillApi":
        """New service over the saved store. Seal stays mechanism-owned."""
        store = self._service.store
        if isinstance(store, FileDurableStore):
            store = FileDurableStore(store.path, seal_key=_restart_capability(store))
        service = MemoryService(
            store=store,
            seed=self._seed,
            context_budget=self._budget,
            policy=self._policy,
        )
        return SkillApi(service, seed=self._seed, context_budget=self._budget, policy=self._policy)

    def invoke(self, caller_id: str, op: str, payload: Mapping | None = None) -> Mapping:
        if op not in SUPPORTED_OPS:
            raise SnapshotError("unsupported skill operation")
        session = CallerSession(self._service, caller_id)
        return session.request(op, payload)

    def open_caller(self, caller_id: str) -> "SkillCaller":
        return SkillCaller(self, caller_id)


class SkillCaller:
    """Bound caller handle. Local to the seam; not a second state owner."""

    def __init__(self, api: SkillApi, caller_id: str) -> None:
        self._api = api
        self.caller_id = caller_id

    def invoke(self, op: str, payload: Mapping | None = None) -> Mapping:
        return self._api.invoke(self.caller_id, op, payload)
