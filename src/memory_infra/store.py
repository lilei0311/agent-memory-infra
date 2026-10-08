"""Stage 3 persistence seam. Storage does not own mechanism transitions.

Snapshots are versioned copies of mechanism-owned state. A store may
save and load that copy. It must not allocate identifiers or rewrite
lifecycle, thread, relation, or trace semantics.
"""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import secrets
import weakref
from typing import Mapping

from memory_infra.adapter import DurableStorePort
from memory_infra.graph import (
    AttentionMode,
    AttentionProfile,
    AttentionState,
    ContextItem,
    Event,
    GraphMemory,
    Lifecycle,
    MemoryPoint,
    MemoryState,
    PointStatus,
    Relation,
    RetrievalEvent,
    Thread,
    Transition,
)

SNAPSHOT_VERSION = 1
PRODUCER = "mechanism"
# Private capability table. Not a snapshot field and not an attribute of the
# store, service, or graph objects exposed to callers.
_SEALS: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
REQUIRED_KEYS = (
    "version",
    "producer",
    "config",
    "counters",
    "points",
    "events",
    "threads",
    "relations",
    "states",
    "retrievals",
    "contexts",
    "attention",
    "trace",
    "integrity",
    "authenticity",
)
CALLER_OWNERSHIP_FIELDS = frozenset(
    {
        "assign_ids",
        "rewrite_lifecycle",
        "rewrite_threads",
        "rewrite_relations",
        "caller_lifecycle",
        "overwrite",
        "delete",
    }
)


class SnapshotError(ValueError):
    """Malformed or incompatible snapshot rejected before restore."""


def _canonical(payload: Mapping) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _integrity(body: Mapping) -> str:
    """Public checksum only. Not proof of mechanism authorship."""
    return hashlib.sha256(_canonical(body).encode()).hexdigest()


def _mechanism_seal(body: Mapping, seal_key: bytes) -> str:
    return hmac.new(seal_key, _canonical(body).encode(), hashlib.sha256).hexdigest()


def new_seal_key() -> bytes:
    """Instance key. Not a source constant and not part of the snapshot."""
    return secrets.token_bytes(32)


def _bind_seal(owner: object, seal_key: bytes) -> None:
    _SEALS[owner] = seal_key


def _seal_for(owner: object) -> bytes | None:
    return _SEALS.get(owner)


def _enum_value(value) -> str:
    return value.value if hasattr(value, "value") else value


def export_snapshot(graph: GraphMemory) -> dict:
    """Copy mechanism-owned state. Does not run a transition."""
    body = {
        "version": SNAPSHOT_VERSION,
        "producer": PRODUCER,
        "config": {
            "seed": graph.seed,
            "policy": graph.policy,
            "context_budget": graph.attention.context_budget,
        },
        "counters": {
            "tick": graph.tick,
            "n": graph._n,
            "last_topic": graph._last_topic,
        },
        "points": {key: _point(value) for key, value in graph.points.items()},
        "events": {key: _event(value) for key, value in graph.events.items()},
        "threads": {key: _thread(value) for key, value in graph.threads.items()},
        "relations": {key: _relation(value) for key, value in graph.relations.items()},
        "states": {key: _state(value) for key, value in graph.states.items()},
        "retrievals": [_retrieval(value) for value in graph.retrievals],
        "contexts": [[_context(item) for item in ctx] for ctx in graph.contexts],
        "attention": _attention(graph.attention),
        "trace": [_transition(value) for value in graph.log],
    }
    seal_key = _seal_for(graph)
    if not isinstance(seal_key, bytes) or not seal_key:
        raise SnapshotError("mechanism seal is missing; snapshot cannot be authored")
    snapshot = dict(body)
    snapshot["integrity"] = _integrity(body)
    snapshot["authenticity"] = _mechanism_seal(body, seal_key)
    return snapshot


def validate_snapshot(snapshot: Mapping, seal_key: bytes | None = None) -> dict:
    if not isinstance(snapshot, Mapping):
        raise SnapshotError("snapshot must be a mapping")
    extra = set(snapshot) - set(REQUIRED_KEYS) - CALLER_OWNERSHIP_FIELDS
    owned = set(snapshot) & CALLER_OWNERSHIP_FIELDS
    if owned:
        raise SnapshotError(f"caller cannot own persistence fields: {sorted(owned)}")
    if extra:
        raise SnapshotError(f"unknown snapshot fields: {sorted(extra)}")
    missing = [key for key in REQUIRED_KEYS if key not in snapshot]
    if missing:
        raise SnapshotError(f"missing snapshot fields: {missing}")
    if snapshot["version"] != SNAPSHOT_VERSION:
        raise SnapshotError(f"incompatible snapshot version: {snapshot['version']}")
    if snapshot["producer"] != PRODUCER:
        raise SnapshotError("snapshot producer must be the mechanism")
    body = {key: snapshot[key] for key in REQUIRED_KEYS if key not in {"integrity", "authenticity"}}
    if snapshot["integrity"] != _integrity(body):
        raise SnapshotError("snapshot integrity mismatch; caller rewrite rejected")
    if not isinstance(seal_key, bytes) or not seal_key:
        raise SnapshotError("snapshot authenticity rejected; no mechanism-owned seal is bound")
    seal = snapshot["authenticity"]
    if not isinstance(seal, str) or not hmac.compare_digest(seal, _mechanism_seal(body, seal_key)):
        raise SnapshotError("snapshot authenticity rejected; caller rewrite is not mechanism-authored")
    _check_records(body)
    return copy.deepcopy(dict(snapshot))


def restore_graph(snapshot: Mapping, seal_key: bytes | None = None) -> GraphMemory:
    """Install a validated snapshot. Does not replay or retune transitions."""
    data = validate_snapshot(snapshot, seal_key)
    config = data["config"]
    graph = GraphMemory(
        seed=config["seed"],
        context_budget=config["context_budget"],
        policy=config["policy"],
    )
    counters = data["counters"]
    graph.tick = counters["tick"]
    graph._n = counters["n"]
    graph._last_topic = counters["last_topic"]
    graph.points = {key: MemoryPoint(**_with_enum(row, "candidate_status", PointStatus)) for key, row in data["points"].items()}
    graph.events = {key: Event(**row) for key, row in data["events"].items()}
    graph.threads = {key: Thread(**row) for key, row in data["threads"].items()}
    graph.relations = {key: Relation(**row) for key, row in data["relations"].items()}
    graph.states = {key: MemoryState(**_with_enum(row, "lifecycle_state", Lifecycle)) for key, row in data["states"].items()}
    graph.retrievals = [RetrievalEvent(**row) for row in data["retrievals"]]
    graph.contexts = [[ContextItem(**item) for item in ctx] for ctx in data["contexts"]]
    graph.attention = _restore_attention(data["attention"])
    graph.log = [Transition(**_with_tuples(row, ("signals", "evidence_refs"))) for row in data["trace"]]
    if isinstance(seal_key, bytes) and seal_key:
        _bind_seal(graph, seal_key)
    return graph


class InMemoryDurableStore(DurableStorePort):
    """Reference store for deterministic tests. No database dependency."""

    def __init__(self) -> None:
        self._snapshot: dict | None = None

    def save_snapshot(self, snapshot: Mapping) -> None:
        self._snapshot = validate_snapshot(snapshot, _seal_for(self))

    def load_snapshot(self) -> dict | None:
        if self._snapshot is None:
            return None
        return copy.deepcopy(self._snapshot)


class MemoryService:
    """Narrow agent-agnostic facade for load/save and request/response."""

    def __init__(
        self,
        store: DurableStorePort | None = None,
        seed: int = 7,
        context_budget: int = 4,
        policy: str = "none",
    ) -> None:
        self.store = store if store is not None else InMemoryDurableStore()
        # Binding is mechanism-only. A caller-supplied store method named
        # bind_seal is ignored so a pre-bound attacker key cannot be adopted.
        bound = _seal_for(self.store)
        seal_key = bound if isinstance(bound, bytes) and bound else new_seal_key()
        if bound is None:
            _bind_seal(self.store, seal_key)
        self.adapter = self._new_adapter(seed, context_budget, policy)
        _bind_seal(self.adapter._graph, seal_key)

    def save(self) -> Mapping:
        snapshot = export_snapshot(self.adapter._graph)
        self.store.save_snapshot(snapshot)
        return {"ok": True, "op": "save", "integrity": snapshot["integrity"]}

    def load(self) -> Mapping:
        snapshot = self.store.load_snapshot()
        if snapshot is None:
            raise SnapshotError("no snapshot to load")
        seal_key = _seal_for(self.store)
        self.adapter._graph = restore_graph(snapshot, seal_key)
        return {"ok": True, "op": "load", "integrity": snapshot["integrity"]}

    def request(self, op: str, payload: Mapping | None = None) -> Mapping:
        body = dict(payload or {})
        owned = set(body) & CALLER_OWNERSHIP_FIELDS
        if owned:
            raise SnapshotError(f"caller cannot own mechanism fields: {sorted(owned)}")
        if op == "save":
            return self.save()
        if op == "load":
            return self.load()
        if op == "observe":
            point_id = self.adapter.submit_observation(body["content"], body.get("source", "caller"))
            return {"ok": True, "op": op, "point_id": point_id}
        if op == "signal":
            name = body.pop("name")
            return {"ok": True, "op": op, "result": self.adapter.submit_signal(name, **body)}
        if op == "retrieve":
            return {"ok": True, "op": op, "result": self.adapter.retrieve(body["query"])}
        if op == "read_lifecycle":
            return {"ok": True, "op": op, "result": self.adapter.read_lifecycle(body["target_id"])}
        if op == "read_event":
            return {"ok": True, "op": op, "result": self.adapter.read_event(body["event_id"])}
        if op == "read_relations":
            return {"ok": True, "op": op, "result": self.adapter.read_relations()}
        if op == "inspect_trace":
            return {"ok": True, "op": op, "result": self.adapter.inspect_trace()}
        raise SnapshotError(f"unsupported service op: {op}")

    @staticmethod
    def _new_adapter(seed: int, context_budget: int, policy: str):
        from memory_infra.adapter import MemoryAdapter

        return MemoryAdapter(seed=seed, context_budget=context_budget, policy=policy)


def _check_records(body: Mapping) -> None:
    points = body["points"]
    events = body["events"]
    threads = body["threads"]
    relations = body["relations"]
    states = body["states"]
    known = set(points) | set(events) | set(threads)
    for key, row in points.items():
        if row.get("point_id") != key:
            raise SnapshotError("point id is mechanism-owned and must match its key")
        if row.get("candidate_status") not in {item.value for item in PointStatus}:
            raise SnapshotError("invalid point status")
    for key, row in events.items():
        if row.get("event_id") != key:
            raise SnapshotError("event id is mechanism-owned and must match its key")
    for key, row in threads.items():
        if row.get("thread_id") != key:
            raise SnapshotError("thread id is mechanism-owned and must match its key")
        if any(member not in events for member in row.get("member_event_ids", [])):
            raise SnapshotError("thread membership references an unknown event")
    for key, row in relations.items():
        if row.get("relation_id") != key:
            raise SnapshotError("relation id is mechanism-owned and must match its key")
        if row.get("source_id") not in known or row.get("target_id") not in known:
            raise SnapshotError("relation endpoints must already exist")
        if not isinstance(row.get("evidence_ref"), str) or not row["evidence_ref"]:
            raise SnapshotError("relation evidence ref is required")
    for key, row in states.items():
        if row.get("target_id") != key or key not in known:
            raise SnapshotError("lifecycle target must match an existing mechanism id")
        if row.get("lifecycle_state") not in {item.value for item in Lifecycle}:
            raise SnapshotError("invalid lifecycle state")
    for row in body["trace"]:
        if not isinstance(row.get("evidence_refs"), list):
            raise SnapshotError("trace evidence refs must stay inspectable")


def _with_enum(row: Mapping, field_name: str, enum_cls):
    data = dict(row)
    data[field_name] = enum_cls(data[field_name])
    return data


def _with_tuples(row: Mapping, fields: tuple[str, ...]) -> dict:
    data = dict(row)
    for field_name in fields:
        data[field_name] = tuple(data[field_name])
    return data


def _point(value: MemoryPoint) -> dict:
    row = dict(value.__dict__)
    row["candidate_status"] = _enum_value(value.candidate_status)
    return row


def _event(value: Event) -> dict:
    return dict(value.__dict__)


def _thread(value: Thread) -> dict:
    row = dict(value.__dict__)
    row["member_event_ids"] = list(value.member_event_ids)
    return row


def _relation(value: Relation) -> dict:
    return dict(value.__dict__)


def _state(value: MemoryState) -> dict:
    row = dict(value.__dict__)
    row["lifecycle_state"] = _enum_value(value.lifecycle_state)
    for field_name in (
        "reinforcement_history",
        "contradiction_history",
        "retrieval_history",
        "usefulness_history",
    ):
        row[field_name] = list(getattr(value, field_name))
    return row


def _retrieval(value: RetrievalEvent) -> dict:
    row = dict(value.__dict__)
    row["candidate_refs"] = list(value.candidate_refs)
    row["selected_refs"] = list(value.selected_refs)
    return row


def _context(value: ContextItem) -> dict:
    row = dict(value.__dict__)
    row["provenance"] = dict(value.provenance)
    return row


def _attention(value: AttentionState) -> dict:
    return {
        "active_thread_distribution": dict(value.active_thread_distribution),
        "current_anchor": value.current_anchor,
        "mode": _enum_value(value.mode),
        "context_budget": value.context_budget,
        "transition_reason": value.transition_reason,
        "detection_signals": list(value.detection_signals),
        "timestamp": value.timestamp,
        "historical_attention_profile": {
            key: {
                "distribution": dict(profile.distribution),
                "anchor": profile.anchor,
                "mode": profile.mode,
            }
            for key, profile in value.historical_attention_profile.items()
        },
    }


def _restore_attention(row: Mapping) -> AttentionState:
    history = {
        key: AttentionProfile(**profile)
        for key, profile in row["historical_attention_profile"].items()
    }
    return AttentionState(
        active_thread_distribution=dict(row["active_thread_distribution"]),
        current_anchor=row["current_anchor"],
        mode=AttentionMode(row["mode"]),
        context_budget=row["context_budget"],
        transition_reason=row["transition_reason"],
        detection_signals=tuple(row["detection_signals"]),
        timestamp=row["timestamp"],
        historical_attention_profile=history,
    )


def _transition(value: Transition) -> dict:
    return {
        "tick": value.tick,
        "kind": value.kind,
        "target_id": value.target_id,
        "source_state": value.source_state,
        "target_state": value.target_state,
        "trigger": value.trigger,
        "signals": list(value.signals),
        "reason": value.reason,
        "evidence_refs": list(value.evidence_refs),
    }
