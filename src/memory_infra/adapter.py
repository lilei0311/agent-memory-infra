"""Storage-agnostic service boundary over the frozen V0.2 mechanism.

Callers and an LLM may submit observations and signals only. Durable
lifecycle, identity, relation, and trace writes stay inside GraphMemory.
This module does not add a database or change transition semantics.
"""

from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Mapping

from memory_infra.graph import GraphMemory

ALLOWED_SIGNALS = (
    "promote",
    "open_thread",
    "extend",
    "split",
    "merge",
    "reopen",
    "link_causal",
    "contradict",
    "begin_reconsolidation",
    "resolve_reconsolidation",
    "consolidate",
    "decay",
    "retrieve",
)

FORBIDDEN_FIELDS = frozenset(
    {
        "lifecycle_state",
        "candidate_status",
        "status",
        "member_event_ids",
        "accessibility",
        "evidence_ref",
        "relation_id",
        "trace",
        "overwrite",
        "delete",
    }
)


class BoundaryError(ValueError):
    """Caller attempted to own a mechanism-owned write."""


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


class MemoryAdapter:
    """In-memory reference adapter. Future stores implement DurableStorePort."""

    def __init__(self, seed: int = 7, context_budget: int = 4, policy: str = "none") -> None:
        self._graph = GraphMemory(seed=seed, context_budget=context_budget, policy=policy)

    @property
    def seed(self) -> int:
        return self._graph.seed

    def submit_observation(self, content: str, source: str = "caller") -> str:
        if not content:
            raise BoundaryError("observation content is required")
        return self._graph.add_point(content, source).point_id

    def submit_signal(self, name: str, **payload: object) -> Mapping:
        overlap = FORBIDDEN_FIELDS.intersection(payload)
        if overlap:
            raise BoundaryError(f"caller cannot set mechanism-owned fields: {sorted(overlap)}")
        if name not in ALLOWED_SIGNALS:
            raise BoundaryError(f"unsupported signal: {name}")
        handler = getattr(self, f"_signal_{name}")
        result = handler(**payload)
        return _freeze({"signal": name, "result": result})

    def retrieve(self, query: str) -> Mapping:
        event = self._graph.retrieve(query)
        return _freeze(
            {
                "retrieval_id": event.retrieval_id,
                "query": event.query_context,
                "selected": list(event.selected_refs),
                "timestamp": event.timestamp,
            }
        )

    def read_lifecycle(self, target_id: str) -> Mapping:
        state = self._graph.states.get(target_id)
        if state is None:
            raise BoundaryError(f"unknown target: {target_id}")
        return _freeze(
            {
                "target_id": state.target_id,
                "lifecycle_state": state.lifecycle_state.value,
                "accessibility": state.accessibility,
                "recency": state.recency,
                "retrieval_history": list(state.retrieval_history),
                "contradiction_history": list(state.contradiction_history),
            }
        )

    def read_event(self, event_id: str) -> Mapping:
        event = self._graph.events.get(event_id)
        if event is None:
            raise BoundaryError(f"unknown event: {event_id}")
        return _freeze(
            {
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "source": event.source,
                "observation": event.observation,
                "evidence_ref": event.evidence_ref,
                "thread_id": event.thread_id,
            }
        )

    def read_relations(self) -> tuple:
        rows = [
            {
                "relation_id": rel.relation_id,
                "source_id": rel.source_id,
                "target_id": rel.target_id,
                "relation_type": rel.relation_type,
                "evidence_ref": rel.evidence_ref,
                "inferred": rel.inferred,
            }
            for rel in self._graph.relations.values()
        ]
        return _freeze(rows)

    def inspect_trace(self) -> tuple:
        return _freeze(self._graph.snapshot()["trace"])

    def trace_digest(self) -> str:
        payload = json.dumps(self._graph.snapshot()["trace"], sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def _signal_promote(self, point_id: str, reason: str) -> dict:
        event = self._graph.promote(point_id, reason)
        return {"event_id": event.event_id, "evidence_ref": event.evidence_ref}

    def _signal_open_thread(self, event_id: str, topic: str, goal: str | None = None) -> dict:
        thread = self._graph.open_thread(event_id, topic, goal)
        return {"thread_id": thread.thread_id, "status": thread.status}

    def _signal_extend(self, thread_id: str, event_id: str, signal: str) -> dict:
        self._graph.extend(thread_id, event_id, signal)
        thread = self._graph.threads[thread_id]
        return {"thread_id": thread.thread_id, "members": list(thread.member_event_ids)}

    def _signal_split(self, thread_id: str, event_id: str, new_topic: str) -> dict:
        child = self._graph.split(thread_id, event_id, new_topic)
        return {"thread_id": child.thread_id, "parent_thread_id": child.parent_thread_id}

    def _signal_merge(self, left_id: str, right_id: str, signal: str) -> dict:
        thread = self._graph.merge(left_id, right_id, signal)
        return {"thread_id": thread.thread_id, "status": thread.status}

    def _signal_reopen(self, thread_id: str, signal: str) -> dict:
        thread = self._graph.reopen(thread_id, signal)
        return {"thread_id": thread.thread_id, "status": thread.status}

    def _signal_link_causal(self, source_id: str, target_id: str, kind: str, evidence: str, inferred: bool = False) -> dict:
        rel = self._graph.link_causal(source_id, target_id, kind, evidence, inferred)
        return {"relation_id": rel.relation_id, "relation_type": rel.relation_type}

    def _signal_contradict(self, left_event: str, right_event: str, evidence: str) -> dict:
        rel = self._graph.contradict(left_event, right_event, evidence)
        return {"relation_id": rel.relation_id, "relation_type": rel.relation_type}

    def _signal_begin_reconsolidation(self, event_id: str, evidence: str) -> dict:
        self._graph.begin_reconsolidation(event_id, evidence)
        return self._state_view(event_id)

    def _signal_resolve_reconsolidation(self, event_id: str, decision: str, evidence: str) -> dict:
        self._graph.resolve_reconsolidation(event_id, decision, evidence)
        return self._state_view(event_id)

    def _signal_consolidate(self, event_id: str, evidence: str) -> dict:
        self._graph.consolidate(event_id, evidence)
        return self._state_view(event_id)

    def _signal_decay(self, target_id: str) -> dict:
        self._graph.decay(target_id)
        return self._state_view(target_id)

    def _state_view(self, target_id: str) -> dict:
        state = self._graph.states[target_id]
        return {"target_id": state.target_id, "lifecycle_state": state.lifecycle_state.value}

    def _signal_retrieve(self, query: str) -> dict:
        event = self._graph.retrieve(query)
        return {"retrieval_id": event.retrieval_id, "selected": list(event.selected_refs)}


class DurableStorePort:
    """Future storage seam. Not implemented in Stage 2.

    A later store may persist the adapter snapshot. It must not assign
    identifiers, lifecycle states, or relation provenance.
    """

    def load_snapshot(self) -> Mapping | None:
        raise NotImplementedError("storage integration is out of scope for Stage 2")

    def save_snapshot(self, snapshot: Mapping) -> None:
        raise NotImplementedError("storage integration is out of scope for Stage 2")
