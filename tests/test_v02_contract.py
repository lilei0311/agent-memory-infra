"""Contract tests for the frozen V0.2 dynamics boundary.

These tests lock already-implemented invariants. They do not retune
Phase G/H configuration or change mechanism transitions.
"""

from memory_infra.graph import GraphMemory, Lifecycle, PointStatus


def test_event_identity_is_immutable_and_repeated_occurrences_stay_distinct() -> None:
    graph = GraphMemory(seed=7)
    first = graph.promote(graph.add_point("same observation").point_id, "task-relevance")
    second = graph.promote(graph.add_point("same observation").point_id, "repeated-reference")
    assert first.event_id != second.event_id
    assert first.evidence_ref != second.evidence_ref
    snapshot = (first.observation, first.evidence_ref, first.timestamp)
    graph.decay(first.event_id)
    assert (first.observation, first.evidence_ref, first.timestamp) == snapshot
    assert first.event_id in graph.events


def test_thread_lifecycle_statuses_and_member_preservation() -> None:
    graph = GraphMemory(seed=7)
    root = graph.promote(graph.add_point("start").point_id, "task-relevance")
    thread = graph.open_thread(root.event_id, "alpha")
    assert thread.status == "active"
    extra = graph.promote(graph.add_point("continue").point_id, "repeated-reference")
    graph.extend(thread.thread_id, extra.event_id, "same-topic")
    assert thread.member_event_ids == [root.event_id, extra.event_id]
    other = graph.promote(graph.add_point("other").point_id, "task-relevance")
    right = graph.open_thread(other.event_id, "gamma")
    before = list(right.member_event_ids)
    graph.merge(thread.thread_id, right.thread_id, "same-goal")
    assert right.status == "merged"
    assert before[0] in thread.member_event_ids
    assert other.event_id in graph.events
    graph.reopen(right.thread_id, "later-reference")
    assert right.status == "active"
    assert right.member_event_ids == before


def test_forgetting_is_non_destructive() -> None:
    graph = GraphMemory(seed=7)
    event = graph.promote(graph.add_point("sleep").point_id, "task-relevance")
    graph.consolidate(event.event_id, "repeat")
    graph.decay(event.event_id)
    graph.decay(event.event_id)
    assert graph.states[event.event_id].lifecycle_state == Lifecycle.INACCESSIBLE
    assert event.event_id in graph.events
    assert graph.events[event.event_id].evidence_ref == event.evidence_ref


def test_contradiction_keeps_both_evidence_paths() -> None:
    graph = GraphMemory(seed=7)
    left = graph.promote(graph.add_point("left").point_id, "task-relevance")
    right = graph.promote(graph.add_point("right").point_id, "contradiction-signal")
    graph.consolidate(left.event_id, "repeat")
    graph.consolidate(right.event_id, "repeat")
    relation = graph.contradict(left.event_id, right.event_id, "both-observed")
    assert relation.relation_type == "evidential.contradicts"
    assert relation.evidence_ref == "both-observed"
    assert left.event_id in graph.events and right.event_id in graph.events
    assert graph.events[left.event_id].evidence_ref != graph.events[right.event_id].evidence_ref


def test_relation_writers_require_provenance() -> None:
    graph = GraphMemory(seed=7)
    event = graph.promote(graph.add_point("cause").point_id, "task-relevance")
    other = graph.promote(graph.add_point("effect").point_id, "task-relevance")
    causal = graph.link_causal(other.event_id, event.event_id, "causal.caused_by", "observed-order")
    assert causal.evidence_ref == "observed-order"
    assert causal.inferred is False
    try:
        graph.link_causal(other.event_id, event.event_id, "causal.caused_by", "")
    except ValueError:
        pass
    else:
        raise AssertionError("causal relation must require evidence")


def test_point_promotion_is_explicit_and_discard_is_not_implemented() -> None:
    graph = GraphMemory(seed=7)
    point = graph.add_point("note")
    assert point.candidate_status == PointStatus.CANDIDATE
    assert not hasattr(graph, "discard")
    event = graph.promote(point.point_id, "task-relevance")
    assert graph.points[point.point_id].candidate_status == PointStatus.PROMOTED
    assert graph.states[event.event_id].lifecycle_state == Lifecycle.LABILE


def test_trace_records_trigger_and_evidence_refs() -> None:
    graph = GraphMemory(seed=7)
    event = graph.promote(graph.add_point("rule").point_id, "task-relevance")
    graph.consolidate(event.event_id, "repeat")
    row = graph.snapshot()["trace"][-1]
    assert row["trigger"] == "consolidation"
    assert row["source_state"] == "LABILE"
    assert row["target_state"] == "STABLE"
    assert "repeat" in row["evidence_refs"]
