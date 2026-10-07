"""Graph-only V0.2 memory dynamics. Does not touch V0.1 scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Lifecycle(str, Enum):
    FORMING = "FORMING"
    LABILE = "LABILE"
    STABLE = "STABLE"
    REACTIVATED = "REACTIVATED"
    RECONSOLIDATING = "RECONSOLIDATING"
    UPDATED = "UPDATED"
    DORMANT = "DORMANT"
    WEAKENED = "WEAKENED"
    INACCESSIBLE = "INACCESSIBLE"


class PointStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    PROMOTED = "PROMOTED"
    LINKED = "LINKED"
    DISCARDED = "DISCARDED"


class AttentionMode(str, Enum):
    NONE = "none"
    FOCUS = "focus"
    DIVERGENT = "divergent"
    COMBINED = "combined"


@dataclass
class Transition:
    tick: int
    kind: str
    target_id: str
    signal: str
    result: str


@dataclass
class MemoryPoint:
    point_id: str
    created_at: int
    source: str
    content: str
    evidence_ref: str
    candidate_status: PointStatus = PointStatus.CANDIDATE
    promotion_reason: str | None = None


@dataclass
class Event:
    event_id: str
    timestamp: int
    source: str
    observation: str
    evidence_ref: str
    thread_id: str | None = None


@dataclass
class Relation:
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str
    created_at: int
    evidence_ref: str
    inferred: bool = False


@dataclass
class Thread:
    thread_id: str
    created_at: int
    member_event_ids: list[str] = field(default_factory=list)
    topic: str = ""
    status: str = "active"
    parent_thread_id: str | None = None


@dataclass
class MemoryState:
    target_id: str
    lifecycle: Lifecycle = Lifecycle.FORMING
    accessibility: float = 1.0
    retrieval_count: int = 0


@dataclass
class RetrievalEvent:
    retrieval_id: str
    timestamp: int
    query_context: str
    candidate_refs: list[str]
    selected_refs: list[str]
    mode: str


class GraphMemory:
    """Mechanism layer. Signals are inputs; this object owns transitions."""

    def __init__(self, seed: int = 0, context_budget: int = 4) -> None:
        self.seed = seed
        self.context_budget = context_budget
        self.tick = 0
        self.points: dict[str, MemoryPoint] = {}
        self.events: dict[str, Event] = {}
        self.threads: dict[str, Thread] = {}
        self.relations: dict[str, Relation] = {}
        self.states: dict[str, MemoryState] = {}
        self.retrievals: list[RetrievalEvent] = []
        self.log: list[Transition] = []
        self._n = 0
        self.focus_thread: str | None = None
        self.mode = AttentionMode.NONE

    def _id(self, prefix: str) -> str:
        self._n += 1
        return f"{prefix}-{self.seed}-{self._n}"

    def _rec(self, kind: str, target: str, signal: str, result: str) -> None:
        self.log.append(Transition(self.tick, kind, target, signal, result))

    def add_point(self, content: str, source: str = "stream") -> MemoryPoint:
        self.tick += 1
        pid = self._id("pt")
        point = MemoryPoint(pid, self.tick, source, content, f"ev-{pid}")
        self.points[pid] = point
        self._rec("point.create", pid, "observation", PointStatus.CANDIDATE.value)
        return point

    def promote(self, point_id: str, reason: str) -> Event:
        point = self.points[point_id]
        if not reason:
            raise ValueError("promotion requires an explicit reason")
        self.tick += 1
        eid = self._id("ev")
        event = Event(eid, self.tick, point.source, point.content, point.evidence_ref)
        self.events[eid] = event
        self.states[eid] = MemoryState(eid, Lifecycle.LABILE)
        point.candidate_status = PointStatus.PROMOTED
        point.promotion_reason = reason
        self._rec("point.promote", eid, reason, Lifecycle.LABILE.value)
        return event

    def open_thread(self, event_id: str, topic: str) -> Thread:
        self.tick += 1
        tid = self._id("th")
        thread = Thread(tid, self.tick, [event_id], topic)
        self.threads[tid] = thread
        self.events[event_id].thread_id = tid
        self.states[tid] = MemoryState(tid, Lifecycle.LABILE)
        self._rec("thread.create", tid, f"first-event:{event_id}", "active")
        return thread

    def extend(self, thread_id: str, event_id: str, signal: str) -> None:
        self.tick += 1
        thread = self.threads[thread_id]
        prev = thread.member_event_ids[-1]
        thread.member_event_ids.append(event_id)
        self.events[event_id].thread_id = thread_id
        self._rel(prev, event_id, "temporal.before", signal)
        self._rec("thread.extend", thread_id, signal, event_id)

    def split(self, thread_id: str, event_id: str, new_topic: str) -> Thread:
        self.tick += 1
        parent = self.threads[thread_id]
        if event_id in parent.member_event_ids:
            parent.member_event_ids.remove(event_id)
        child = Thread(self._id("th"), self.tick, [event_id], new_topic, parent_thread_id=thread_id)
        self.threads[child.thread_id] = child
        self.events[event_id].thread_id = child.thread_id
        self.states[child.thread_id] = MemoryState(child.thread_id, Lifecycle.LABILE)
        self._rel(thread_id, child.thread_id, "contextual.changed_context", new_topic)
        self._rec("thread.split", child.thread_id, new_topic, thread_id)
        return child

    def merge(self, left_id: str, right_id: str, signal: str) -> Thread:
        self.tick += 1
        left, right = self.threads[left_id], self.threads[right_id]
        for eid in right.member_event_ids:
            if eid not in left.member_event_ids:
                left.member_event_ids.append(eid)
                self.events[eid].thread_id = left_id
        right.status = "merged"
        self._rel(left_id, right_id, "referential.same_thread", signal)
        self._rec("thread.merge", left_id, signal, right_id)
        return left

    def reopen(self, thread_id: str, signal: str) -> None:
        self.tick += 1
        self.threads[thread_id].status = "active"
        state = self.states[thread_id]
        state.lifecycle = Lifecycle.REACTIVATED
        state.accessibility = 1.0
        self._rec("thread.reopen", thread_id, signal, Lifecycle.REACTIVATED.value)

    def contradict(self, left_event: str, right_event: str, evidence: str) -> Relation:
        self.tick += 1
        rel = self._rel(left_event, right_event, "evidential.contradicts", evidence)
        for eid in (left_event, right_event):
            self.states[eid].lifecycle = Lifecycle.WEAKENED
        self._rec("relation.contradict", rel.relation_id, evidence, "both-kept")
        return rel

    def _rel(self, source: str, target: str, kind: str, evidence: str) -> Relation:
        rid = self._id("rel")
        rel = Relation(rid, source, target, kind, self.tick, evidence)
        self.relations[rid] = rel
        return rel

    def decay(self, target_id: str) -> None:
        self.tick += 1
        state = self.states[target_id]
        state.accessibility = max(0.0, state.accessibility - 0.5)
        state.lifecycle = Lifecycle.DORMANT if state.accessibility <= 0.5 else state.lifecycle
        if state.accessibility == 0.0:
            state.lifecycle = Lifecycle.INACCESSIBLE
        self._rec("state.decay", target_id, "time", state.lifecycle.value)

    def retrieve(self, query: str, mode: AttentionMode | None = None) -> RetrievalEvent:
        self.tick += 1
        mode = mode or self.mode
        candidates = [eid for eid, st in self.states.items() if st.accessibility > 0 and eid in self.events]
        selected = self._allocate(candidates, mode)
        for eid in selected:
            st = self.states[eid]
            st.retrieval_count += 1
            if st.lifecycle == Lifecycle.DORMANT:
                st.lifecycle = Lifecycle.REACTIVATED
                st.accessibility = 1.0
                self._rec("retrieval.reactivate", eid, query, Lifecycle.REACTIVATED.value)
        rec = RetrievalEvent(self._id("ret"), self.tick, query, candidates, selected, mode.value)
        self.retrievals.append(rec)
        self._rec("retrieval.log", rec.retrieval_id, query, ",".join(selected))
        return rec

    def set_attention(self, mode: AttentionMode, focus_thread: str | None = None) -> None:
        self.mode = mode
        self.focus_thread = focus_thread
        self._rec("attention.set", focus_thread or "*", mode.value, mode.value)

    def assemble(self, query: str, mode: AttentionMode | None = None) -> list[dict]:
        rec = self.retrieve(query, mode)
        return [
            {
                "event_id": eid,
                "thread_id": self.events[eid].thread_id,
                "content": self.events[eid].observation,
                "evidence_ref": self.events[eid].evidence_ref,
            }
            for eid in rec.selected_refs
        ]

    def _allocate(self, candidates: list[str], mode: AttentionMode) -> list[str]:
        by_thread: dict[str, list[str]] = {}
        for eid in candidates:
            tid = self.events[eid].thread_id or eid
            by_thread.setdefault(tid, []).append(eid)
        budget = self.context_budget
        picked: list[str] = []
        if mode == AttentionMode.FOCUS and self.focus_thread in by_thread:
            picked.extend(by_thread[self.focus_thread][: max(1, budget - 1)])
            for tid, ids in by_thread.items():
                if tid != self.focus_thread and len(picked) < budget:
                    picked.append(ids[0])
        elif mode == AttentionMode.DIVERGENT:
            for tid, ids in by_thread.items():
                if len(picked) < budget:
                    picked.append(ids[0])
        elif mode == AttentionMode.COMBINED and self.focus_thread in by_thread:
            picked.extend(by_thread[self.focus_thread][: max(1, budget // 2)])
            for tid, ids in by_thread.items():
                if tid != self.focus_thread and len(picked) < budget:
                    picked.append(ids[0])
        else:
            picked = candidates[:budget]
        return picked[:budget]

    def replay_signature(self) -> tuple:
        return (self.seed, tuple((t.kind, t.target_id, t.signal, t.result) for t in self.log))
