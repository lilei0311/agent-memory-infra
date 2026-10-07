import pytest

from memory_infra.graph import AttentionMode, GraphMemory, Lifecycle, PointStatus, Signals


def _world(seed: int = 1) -> tuple[GraphMemory, str, str, str, str]:
    g = GraphMemory(seed=seed, context_budget=4, policy="automatic")
    tea = g.promote(g.add_point("prefers tea").point_id, "explicit-feedback", action="ask", feedback="yes", outcome="noted", goal="drinks")
    drinks = g.open_thread(tea.event_id, "drinks", goal="settle-drink")
    tea2 = g.promote(g.add_point("prefers tea again").point_id, "repeated-reference")
    g.extend(drinks.thread_id, tea2.event_id, "same-topic")
    coffee = g.promote(g.add_point("said coffee").point_id, "contradiction-signal")
    other = g.open_thread(coffee.event_id, "other-drink")
    return g, drinks.thread_id, other.thread_id, tea.event_id, coffee.event_id


def test_identity_and_invariants() -> None:
    g, _, _, tea, coffee = _world()
    assert tea != coffee
    assert g.events[tea].evidence_ref.startswith("ev-")
    assert g.events[tea].episode_id
    with pytest.raises(ValueError):
        g.promote(next(iter(g.points)), "")


def test_promotion_records_reason() -> None:
    g = GraphMemory(seed=1)
    point = g.add_point("note")
    assert point.candidate_status == PointStatus.CANDIDATE
    event = g.promote(point.point_id, "task-relevance")
    assert g.points[point.point_id].promotion_reason == "task-relevance"
    assert g.states[event.event_id].lifecycle_state == Lifecycle.LABILE


def test_repeated_events_stay_separate_in_a_thread() -> None:
    g, thread_id, _, tea, _ = _world()
    assert len(g.threads[thread_id].member_event_ids) == 2
    assert tea in g.events


def test_contradiction_keeps_both_and_reconsolidates() -> None:
    g, _, _, tea, coffee = _world()
    g.consolidate(tea, "repeat")
    g.contradict(tea, coffee, "both-observed")
    assert tea in g.events and coffee in g.events
    assert g.states[tea].lifecycle_state == Lifecycle.RECONSOLIDATING
    assert g.states[coffee].lifecycle_state == Lifecycle.RECONSOLIDATING
    assert g.events[tea].evidence_ref != g.events[coffee].evidence_ref
    assert any(r.relation_type == "evidential.contradicts" for r in g.relations.values())


def test_retrieval_reactivates_dormant() -> None:
    g, _, _, tea, _ = _world()
    g.consolidate(tea, "repeat")
    g.decay(tea)
    assert g.states[tea].lifecycle_state == Lifecycle.DORMANT
    g.retrieve("drinks")
    assert g.states[tea].lifecycle_state == Lifecycle.REACTIVATED


def test_focus_increases_target_share() -> None:
    g, drinks, other, _, _ = _world()
    g.observe(Signals(topic="drinks", topic_continuity=True, thread_reference=drinks))
    ctx = g.assemble("drinks")
    focused = sum(1 for i in ctx if i.thread_id == drinks)
    other_n = sum(1 for i in ctx if i.thread_id == other)
    assert g.attention.mode == AttentionMode.FOCUS
    assert focused > other_n


def test_topic_return_restores_prior_profile() -> None:
    g = GraphMemory(seed=2, context_budget=4, policy="automatic")
    e1 = g.promote(g.add_point("t1").point_id, "task-relevance")
    t1 = g.open_thread(e1.event_id, "T1")
    e2 = g.promote(g.add_point("t2").point_id, "task-relevance")
    t2 = g.open_thread(e2.event_id, "T2")
    e3 = g.promote(g.add_point("t3").point_id, "task-relevance")
    t3 = g.open_thread(e3.event_id, "T3")
    g.observe(Signals(topic="T1", topic_continuity=True, thread_reference=t1.thread_id))
    saved = dict(g.attention.active_thread_distribution)
    assert g.attention.current_anchor == t1.thread_id
    g.observe(Signals(topic="T2", topic_switch=True, thread_reference=t2.thread_id))
    g.observe(Signals(topic="T3", topic_switch=True, thread_reference=t3.thread_id))
    g.observe(Signals(topic="T1", topic_switch=True, thread_reference=t1.thread_id))
    assert g.attention.transition_reason == "topic-return-restore"
    assert g.attention.current_anchor == t1.thread_id
    assert g.attention.active_thread_distribution == saved


def test_divergent_keeps_multiple_threads() -> None:
    g, drinks, other, _, _ = _world()
    g.observe(Signals(divergence=True))
    ctx = g.assemble("both")
    threads = {i.thread_id for i in ctx}
    assert drinks in threads and other in threads
    assert g.attention.mode == AttentionMode.DIVERGENT


def test_lifecycle_path_is_recorded() -> None:
    g = GraphMemory(seed=1)
    event = g.promote(g.add_point("rule").point_id, "task-relevance")
    g.consolidate(event.event_id, "repeat")
    g.retrieve("rule")
    assert g.states[event.event_id].lifecycle_state == Lifecycle.REACTIVATED
    g.contradict(event.event_id, event.event_id, "self-check")
    g.resolve_reconsolidation(event.event_id, "revise", "new-outcome")
    kinds = [(t.source_state, t.target_state) for t in g.log if t.kind == "lifecycle"]
    assert ("LABILE", "STABLE") in kinds
    assert ("STABLE", "REACTIVATED") in kinds
    assert ("RECONSOLIDATING", "UPDATED") in kinds


def test_context_item_has_provenance() -> None:
    g, drinks, _, tea, _ = _world()
    g.observe(Signals(topic="drinks", thread_reference=drinks, topic_continuity=True))
    ctx = g.assemble("drinks")
    assert ctx
    assert ctx[0].provenance["event_id"] == ctx[0].source_ref
    assert ctx[0].provenance["evidence_ref"]


def test_replay_matches_graph_state_attention_context_and_trace() -> None:
    a, *_ = _world(7)
    b, *_ = _world(7)
    a.observe(Signals(topic="drinks", topic_continuity=True))
    b.observe(Signals(topic="drinks", topic_continuity=True))
    a.assemble("drinks")
    b.assemble("drinks")
    assert a.snapshot() == b.snapshot()


def test_memory_state_dimensions_stay_separate() -> None:
    g, _, _, tea, _ = _world()
    state = g.states[tea]
    state.reinforcement_history.append("r")
    state.contradiction_history.append("c")
    state.retrieval_history.append("q")
    state.usefulness_history.append("u")
    assert {"accessibility", "confidence", "contextual_fit", "recency", "reinforcement_history", "contradiction_history", "retrieval_history", "usefulness_history", "lifecycle_state"} <= set(state.__dict__)
