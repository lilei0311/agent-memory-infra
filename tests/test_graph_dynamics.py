import pytest

from memory_infra.graph import AttentionMode, GraphMemory, Lifecycle, PointStatus


def _world(seed: int = 1) -> tuple[GraphMemory, str, str, str, str]:
    g = GraphMemory(seed=seed, context_budget=4)
    tea = g.promote(g.add_point("prefers tea").point_id, "explicit-feedback")
    drinks = g.open_thread(tea.event_id, "drinks")
    tea2 = g.promote(g.add_point("prefers tea again").point_id, "repeated-reference")
    g.extend(drinks.thread_id, tea2.event_id, "same-topic")
    coffee = g.promote(g.add_point("said coffee").point_id, "contradiction-signal")
    other = g.open_thread(coffee.event_id, "other-drink")
    return g, drinks.thread_id, other.thread_id, tea.event_id, coffee.event_id


def test_identity_and_invariants() -> None:
    g, _, _, tea, coffee = _world()
    assert tea != coffee
    assert g.events[tea].evidence_ref.startswith("ev-")
    with pytest.raises(ValueError):
        g.promote(next(iter(g.points)), "")


def test_promotion_records_reason() -> None:
    g = GraphMemory(seed=1)
    point = g.add_point("note")
    assert point.candidate_status == PointStatus.CANDIDATE
    event = g.promote(point.point_id, "task-relevance")
    assert g.points[point.point_id].promotion_reason == "task-relevance"
    assert g.states[event.event_id].lifecycle == Lifecycle.LABILE


def test_repeated_events_stay_separate_in_a_thread() -> None:
    g, thread_id, _, tea, _ = _world()
    assert len(g.threads[thread_id].member_event_ids) == 2
    assert tea in g.events


def test_contradiction_keeps_both() -> None:
    g, _, _, tea, coffee = _world()
    g.contradict(tea, coffee, "both-observed")
    assert tea in g.events and coffee in g.events
    assert any(r.relation_type == "evidential.contradicts" for r in g.relations.values())


def test_retrieval_reactivates_dormant() -> None:
    g, _, _, tea, _ = _world()
    g.decay(tea)
    assert g.states[tea].lifecycle == Lifecycle.DORMANT
    g.retrieve("drinks")
    assert g.states[tea].lifecycle == Lifecycle.REACTIVATED


def test_focus_increases_target_share() -> None:
    g, drinks, other, _, _ = _world()
    g.set_attention(AttentionMode.FOCUS, drinks)
    ctx = g.assemble("drinks", AttentionMode.FOCUS)
    focused = sum(1 for i in ctx if i["thread_id"] == drinks)
    other_n = sum(1 for i in ctx if i["thread_id"] == other)
    assert focused > other_n


def test_topic_return_restores_thread() -> None:
    g, drinks, _, _, _ = _world()
    g.states[drinks].lifecycle = Lifecycle.DORMANT
    g.threads[drinks].status = "archived"
    g.reopen(drinks, "topic-return")
    assert g.threads[drinks].status == "active"
    assert g.states[drinks].lifecycle == Lifecycle.REACTIVATED


def test_divergent_keeps_multiple_threads() -> None:
    g, drinks, other, _, _ = _world()
    ctx = g.assemble("both", AttentionMode.DIVERGENT)
    threads = {i["thread_id"] for i in ctx}
    assert drinks in threads and other in threads


def test_replay_is_deterministic() -> None:
    a, *_ = _world(7)
    b, *_ = _world(7)
    assert a.replay_signature() == b.replay_signature()
