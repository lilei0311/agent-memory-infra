"""Graph-only V0.2 mechanism layer. Does not touch V0.1 scoring."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
    UNFOCUSED = "unfocused"


@dataclass
class Transition:
    tick: int
    kind: str
    target_id: str
    source_state: str
    target_state: str
    trigger: str
    signals: tuple[str, ...]
    reason: str
    evidence_refs: tuple[str, ...]


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
    action: str | None = None
    feedback: str | None = None
    outcome: str | None = None
    context: str | None = None
    goal: str | None = None
    state_change: str | None = None
    thread_id: str | None = None
    episode_id: str | None = None


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
    goal: str | None = None
    status: str = "active"
    parent_thread_id: str | None = None


@dataclass
class MemoryState:
    target_id: str
    accessibility: float = 1.0
    confidence: float = 0.5
    contextual_fit: float = 0.0
    recency: float = 1.0
    reinforcement_history: list[str] = field(default_factory=list)
    contradiction_history: list[str] = field(default_factory=list)
    retrieval_history: list[str] = field(default_factory=list)
    usefulness_history: list[str] = field(default_factory=list)
    lifecycle_state: Lifecycle = Lifecycle.FORMING


@dataclass
class AttentionProfile:
    distribution: dict[str, float]
    anchor: str | None
    mode: str


@dataclass
class AttentionState:
    active_thread_distribution: dict[str, float] = field(default_factory=dict)
    current_anchor: str | None = None
    mode: AttentionMode = AttentionMode.UNFOCUSED
    context_budget: int = 4
    transition_reason: str = "init"
    detection_signals: tuple[str, ...] = ()
    timestamp: int = 0
    historical_attention_profile: dict[str, AttentionProfile] = field(default_factory=dict)


@dataclass
class RetrievalEvent:
    retrieval_id: str
    timestamp: int
    query_context: str
    candidate_refs: list[str]
    selected_refs: list[str]
    mode: str
    attention_anchor: str | None


@dataclass
class ContextItem:
    source_ref: str
    thread_id: str | None
    relevance: float
    attention_weight: float
    provenance: dict[str, str]
    event_id: str = ""
    content: str = ""


@dataclass
class Signals:
    topic: str | None = None
    topic_continuity: bool = False
    topic_switch: bool = False
    thread_reference: str | None = None
    unresolved_goal: str | None = None
    divergence: bool = False
    goal_continuity: bool = False
    goal: str | None = None


class GraphMemory:
    """Mechanism owns durable state. Callers may only supply observations/signals."""

    def __init__(self, seed: int = 0, context_budget: int = 4, policy: str = "automatic") -> None:
        self.seed = seed
        self.policy = policy
        self.tick = 0
        self.points: dict[str, MemoryPoint] = {}
        self.events: dict[str, Event] = {}
        self.threads: dict[str, Thread] = {}
        self.relations: dict[str, Relation] = {}
        self.states: dict[str, MemoryState] = {}
        self.retrievals: list[RetrievalEvent] = []
        self.contexts: list[list[ContextItem]] = []
        self.log: list[Transition] = []
        self.attention = AttentionState(context_budget=context_budget)
        self._n = 0
        self._last_topic: str | None = None

    def _id(self, prefix: str) -> str:
        self._n += 1
        return f"{prefix}-{self.seed}-{self._n}"

    def _transition(self, kind: str, target: str, source: str, dest: str, trigger: str, signals: tuple[str, ...], reason: str, evidence: tuple[str, ...]) -> None:
        self.log.append(Transition(self.tick, kind, target, source, dest, trigger, signals, reason, evidence))

    def add_point(self, content: str, source: str = "stream") -> MemoryPoint:
        self.tick += 1
        pid = self._id("pt")
        point = MemoryPoint(pid, self.tick, source, content, f"ev-{pid}")
        self.points[pid] = point
        self._transition("point.create", pid, "", PointStatus.CANDIDATE.value, "observation", ("observation",), "candidate recorded", (point.evidence_ref,))
        return point

    def promote(self, point_id: str, reason: str, **episode) -> Event:
        if not reason:
            raise ValueError("promotion requires an explicit reason")
        point = self.points[point_id]
        self.tick += 1
        eid = self._id("ev")
        episode_id = self._id("ep") if any(episode.get(k) for k in ("action", "feedback", "outcome")) else None
        event = Event(
            eid, self.tick, point.source, point.content, point.evidence_ref,
            action=episode.get("action"), feedback=episode.get("feedback"), outcome=episode.get("outcome"),
            context=episode.get("context"), goal=episode.get("goal"), state_change=episode.get("state_change"),
            episode_id=episode_id,
        )
        self.events[eid] = event
        self.states[eid] = MemoryState(eid, lifecycle_state=Lifecycle.FORMING, recency=1.0, contextual_fit=0.2)
        point.candidate_status = PointStatus.PROMOTED
        point.promotion_reason = reason
        self._move(eid, Lifecycle.LABILE, "promote", (reason,), reason, (point.evidence_ref,))
        return event

    def open_thread(self, event_id: str, topic: str, goal: str | None = None) -> Thread:
        self.tick += 1
        tid = self._id("th")
        thread = Thread(tid, self.tick, [event_id], topic, goal)
        self.threads[tid] = thread
        self.events[event_id].thread_id = tid
        self.states[tid] = MemoryState(tid, lifecycle_state=Lifecycle.LABILE)
        self._transition("thread.create", tid, "", "active", "first-event", (topic,), "coherent cluster", (self.events[event_id].evidence_ref,))
        return thread

    def extend(self, thread_id: str, event_id: str, signal: str) -> None:
        self.tick += 1
        thread = self.threads[thread_id]
        prev = thread.member_event_ids[-1]
        thread.member_event_ids.append(event_id)
        self.events[event_id].thread_id = thread_id
        rel = self._rel(prev, event_id, "temporal.before", signal)
        self._transition("thread.extend", thread_id, "active", "active", "continuity", (signal,), "extend thread", (rel.evidence_ref,))

    def split(self, thread_id: str, event_id: str, new_topic: str) -> Thread:
        self.tick += 1
        parent = self.threads[thread_id]
        if event_id in parent.member_event_ids:
            parent.member_event_ids.remove(event_id)
        child = Thread(self._id("th"), self.tick, [event_id], new_topic, parent_thread_id=thread_id)
        self.threads[child.thread_id] = child
        self.events[event_id].thread_id = child.thread_id
        self.states[child.thread_id] = MemoryState(child.thread_id, lifecycle_state=Lifecycle.LABILE)
        self._rel(thread_id, child.thread_id, "contextual.changed_context", new_topic)
        self._transition("thread.split", child.thread_id, thread_id, "active", "divergent-goal", (new_topic,), "independent context", (self.events[event_id].evidence_ref,))
        return child

    def merge(self, left_id: str, right_id: str, signal: str) -> Thread:
        self.tick += 1
        left, right = self.threads[left_id], self.threads[right_id]
        for eid in right.member_event_ids:
            if eid not in left.member_event_ids:
                left.member_event_ids.append(eid)
                self.events[eid].thread_id = left_id
        right.status = "merged"
        rel = self._rel(left_id, right_id, "referential.same_thread", signal)
        self._transition("thread.merge", left_id, "separate", "merged", "continuity-evidence", (signal,), "graph merge, events kept", (rel.evidence_ref,))
        return left

    def contradict(self, left_event: str, right_event: str, evidence: str) -> Relation:
        self.tick += 1
        rel = self._rel(left_event, right_event, "evidential.contradicts", evidence)
        for eid in (left_event, right_event):
            state = self.states[eid]
            state.contradiction_history.append(rel.relation_id)
            self._move(eid, Lifecycle.RECONSOLIDATING, "contradiction", (evidence,), "enter reconsolidation; evidence kept", (rel.evidence_ref, self.events[eid].evidence_ref))
        self._transition("relation.contradict", rel.relation_id, "both-present", "both-present", "contradiction", (evidence,), "neither side overwritten", (rel.evidence_ref,))
        return rel

    def begin_reconsolidation(self, event_id: str, evidence: str) -> None:
        self.tick += 1
        self._move(event_id, Lifecycle.RECONSOLIDATING, "retrieval-followup", (evidence,), "reactivated opens reconsolidation", (evidence,))

    def resolve_reconsolidation(self, event_id: str, decision: str, evidence: str) -> None:
        mapping = {"confirm": Lifecycle.STABLE, "revise": Lifecycle.UPDATED, "weaken": Lifecycle.WEAKENED, "unresolved": Lifecycle.WEAKENED}
        if decision not in mapping:
            raise ValueError("decision must be confirm, revise, or weaken")
        self.tick += 1
        self._move(event_id, mapping[decision], "reconsolidation-decision", (decision,), evidence, (evidence,))

    def consolidate(self, event_id: str, evidence: str = "repeated-reinforcement") -> None:
        self.tick += 1
        state = self.states[event_id]
        state.reinforcement_history.append(evidence)
        if state.lifecycle_state == Lifecycle.LABILE and len(state.reinforcement_history) >= 1:
            self._move(event_id, Lifecycle.STABLE, "consolidation", (evidence,), "labile to stable", (evidence,))

    def decay(self, target_id: str) -> None:
        self.tick += 1
        state = self.states[target_id]
        state.accessibility = max(0.0, round(state.accessibility - 0.5, 4))
        state.recency = max(0.0, round(state.recency - 0.25, 4))
        if state.lifecycle_state == Lifecycle.STABLE and state.accessibility <= 0.5:
            self._move(target_id, Lifecycle.DORMANT, "time", ("low-accessibility",), "stable to dormant", ())
        elif state.lifecycle_state == Lifecycle.DORMANT and state.accessibility == 0.0:
            self._move(target_id, Lifecycle.INACCESSIBLE, "time", ("zero-accessibility",), "dormant to inaccessible", ())

    def _move(self, target: str, dest: Lifecycle, trigger: str, signals: tuple[str, ...], reason: str, evidence: tuple[str, ...]) -> None:
        state = self.states[target]
        source = state.lifecycle_state.value
        state.lifecycle_state = dest
        self._transition("lifecycle", target, source, dest.value, trigger, signals, reason, evidence)

    def _rel(self, source: str, target: str, kind: str, evidence: str) -> Relation:
        rid = self._id("rel")
        rel = Relation(rid, source, target, kind, self.tick, evidence)
        self.relations[rid] = rel
        return rel

    def observe(self, signals: Signals) -> AttentionState:
        """Automatic attention. Callers cannot write mode directly."""
        self.tick += 1
        detected = self._detect(signals)
        mode, anchor, reason = self._decide(detected, signals)
        return_to = signals.thread_reference or self._thread_for_topic(signals.topic)
        returning = bool(return_to) and return_to in self.attention.historical_attention_profile and return_to != self.attention.current_anchor
        anchor = return_to if returning else anchor
        if self.attention.current_anchor:
            self.attention.historical_attention_profile[self.attention.current_anchor] = AttentionProfile(
                dict(self.attention.active_thread_distribution), self.attention.current_anchor, self.attention.mode.value
            )
        if returning:
            saved = self.attention.historical_attention_profile[anchor]
            self.attention.active_thread_distribution = dict(saved.distribution)
            self.attention.mode = AttentionMode(saved.mode)
            self.attention.current_anchor = saved.anchor
            self.attention.transition_reason = "topic-return-restore"
        else:
            self.attention.mode = mode
            self.attention.current_anchor = anchor
            self.attention.active_thread_distribution = self._distribution(anchor, mode)
            self.attention.transition_reason = reason
        self.attention.detection_signals = tuple(detected)
        self.attention.timestamp = self.tick
        self._last_topic = signals.topic or self._last_topic
        self._transition("attention.update", self.attention.current_anchor or "*", "", self.attention.mode.value, "signals", tuple(detected), self.attention.transition_reason, ())
        return self.attention

    def _detect(self, signals: Signals) -> list[str]:
        found = []
        if signals.topic and signals.topic == self._last_topic:
            found.append("topic-continuity")
        if signals.topic_continuity:
            found.append("topic-continuity")
        if signals.topic_switch or (signals.topic and self._last_topic and signals.topic != self._last_topic):
            found.append("topic-switch")
        if signals.thread_reference:
            found.append("thread-reference")
        if signals.unresolved_goal or signals.goal_continuity:
            found.append("unresolved-goal")
        if signals.goal_continuity:
            found.append("goal-continuity")
        if signals.divergence:
            found.append("divergence")
        found.append(f"active-threads:{sum(1 for t in self.threads.values() if t.status == 'active')}")
        return found

    def _decide(self, detected: list[str], signals: Signals) -> tuple[AttentionMode, str | None, str]:
        anchor = signals.thread_reference or self._thread_for_topic(signals.topic) or self.attention.current_anchor
        active = sum(1 for t in self.threads.values() if t.status == "active")
        if self.policy == "none":
            return AttentionMode.NONE, None, "no-attention-control"
        if self.policy == "focus":
            return AttentionMode.FOCUS, anchor, "focus-only"
        if self.policy == "divergent":
            return AttentionMode.DIVERGENT, None, "divergent-only"
        if "divergence" in detected and ("topic-continuity" in detected or signals.unresolved_goal):
            return AttentionMode.COMBINED, anchor, "continuity-plus-divergence"
        if "divergence" in detected or (active >= 3 and "topic-continuity" not in detected and "thread-reference" not in detected):
            return AttentionMode.DIVERGENT, None, "divergence-signal"
        if anchor and ("topic-continuity" in detected or "thread-reference" in detected or "unresolved-goal" in detected):
            return AttentionMode.FOCUS, anchor, "continuity-signal"
        return AttentionMode.UNFOCUSED, anchor, "no-dominant-signal"

    def _thread_for_topic(self, topic: str | None) -> str | None:
        if not topic:
            return None
        for thread in self.threads.values():
            if thread.topic == topic and thread.status == "active":
                return thread.thread_id
        return None

    def _distribution(self, anchor: str | None, mode: AttentionMode) -> dict[str, float]:
        active = [t.thread_id for t in self.threads.values() if t.status == "active"]
        if not active:
            return {}
        if mode == AttentionMode.FOCUS and anchor in active:
            rest = [t for t in active if t != anchor]
            share = 0.2 / len(rest) if rest else 0.0
            return {t: (0.8 if t == anchor else share) for t in active}
        if mode == AttentionMode.DIVERGENT:
            share = 1.0 / len(active)
            return {t: share for t in active}
        if mode == AttentionMode.COMBINED and anchor in active:
            rest = [t for t in active if t != anchor]
            share = 0.5 / len(rest) if rest else 0.0
            return {t: (0.5 if t == anchor else share) for t in active}
        share = 1.0 / len(active)
        return {t: share for t in active}

    def retrieve(self, query: str) -> RetrievalEvent:
        self.tick += 1
        candidates = [eid for eid, st in self.states.items() if eid in self.events and st.accessibility > 0 and st.lifecycle_state != Lifecycle.INACCESSIBLE]
        selected = self._allocate_with_attention(candidates) if self.policy != "none" else self._allocate_baseline(candidates)
        for eid in selected:
            state = self.states[eid]
            state.retrieval_history.append(query)
            state.recency = 1.0
            if state.lifecycle_state in (Lifecycle.DORMANT, Lifecycle.STABLE):
                self._move(eid, Lifecycle.REACTIVATED, "retrieval", (query,), "retrieval reactivates", (self.events[eid].evidence_ref,))
                state.accessibility = 1.0
        rec = RetrievalEvent(self._id("ret"), self.tick, query, candidates, selected, self.attention.mode.value, self.attention.current_anchor)
        self.retrievals.append(rec)
        self._transition("retrieval.log", rec.retrieval_id, "", ",".join(selected), "retrieve", (query,), "allocation recorded", tuple(selected))
        return rec

    def assemble(self, query: str) -> list[ContextItem]:
        rec = self.retrieve(query)
        items = []
        for eid in rec.selected_refs:
            event = self.events[eid]
            weight = self.attention.active_thread_distribution.get(event.thread_id or "", 0.0)
            items.append(ContextItem(
                source_ref=eid,
                event_id=eid,
                thread_id=event.thread_id,
                content=event.observation,
                relevance=self.states[eid].contextual_fit,
                attention_weight=weight,
                provenance={"event_id": eid, "evidence_ref": event.evidence_ref, "thread_id": event.thread_id or ""},
            ))
        self.contexts.append(items)
        return items

    def _allocate_baseline(self, candidates: list[str]) -> list[str]:
        ranked = sorted(candidates, key=lambda eid: self.states[eid].recency, reverse=True)
        return ranked[: self.attention.context_budget]

    def _allocate_with_attention(self, candidates: list[str]) -> list[str]:
        budget = self.attention.context_budget
        scored = []
        for eid in candidates:
            thread_id = self.events[eid].thread_id or ""
            weight = self.attention.active_thread_distribution.get(thread_id, 0.0)
            state = self.states[eid]
            score = weight + 0.01 * state.recency + 0.01 * state.contextual_fit
            scored.append((score, eid))
        scored.sort(key=lambda row: (-row[0], row[1]))
        return [eid for _, eid in scored[:budget]]

    def set_attention(self, mode: AttentionMode, focus_thread: str | None = None) -> None:
        """Debug-only. Production path is observe(Signals) -> AttentionState."""
        self.tick += 1
        self.attention.mode = mode
        self.attention.current_anchor = focus_thread
        self.attention.transition_reason = "debug-set-attention"
        self._transition("attention.debug", focus_thread or "*", "", mode.value, "debug", (), "not a production path", ())

    def snapshot(self) -> dict:
        return {
            "seed": self.seed,
            "policy": self.policy,
            "events": {k: asdict(v) for k, v in self.events.items()},
            "threads": {k: asdict(v) for k, v in self.threads.items()},
            "states": {k: {**asdict(v), "lifecycle_state": v.lifecycle_state.value} for k, v in self.states.items()},
            "attention": {
                "distribution": self.attention.active_thread_distribution,
                "anchor": self.attention.current_anchor,
                "mode": self.attention.mode.value,
                "budget": self.attention.context_budget,
                "reason": self.attention.transition_reason,
                "signals": self.attention.detection_signals,
                "history": {k: asdict(v) for k, v in self.attention.historical_attention_profile.items()},
            },
            "contexts": [[asdict(i) for i in ctx] for ctx in self.contexts],
            "trace": [asdict(t) for t in self.log],
        }
