"""Stage 2 adapter ownership tests. Does not retune locked experiments."""

import pytest

from memory_infra.adapter import ALLOWED_SIGNALS, BoundaryError, DurableStorePort, MemoryAdapter


def test_caller_cannot_set_mechanism_owned_fields() -> None:
    adapter = MemoryAdapter(seed=7)
    point_id = adapter.submit_observation("rule", source="caller")
    with pytest.raises(BoundaryError):
        adapter.submit_signal("promote", point_id=point_id, reason="task-relevance", lifecycle_state="STABLE")
    with pytest.raises(BoundaryError):
        adapter.submit_signal("set_lifecycle", target_id="ev-1", lifecycle_state="STABLE")
    assert "set_lifecycle" not in ALLOWED_SIGNALS


def test_observation_and_signal_leave_lifecycle_mechanism_owned() -> None:
    adapter = MemoryAdapter(seed=7, context_budget=4, policy="none")
    point_id = adapter.submit_observation("rule")
    promoted = adapter.submit_signal("promote", point_id=point_id, reason="task-relevance")
    event_id = promoted["result"]["event_id"]
    view = adapter.read_lifecycle(event_id)
    assert view["lifecycle_state"] == "LABILE"
    with pytest.raises(TypeError):
        view["lifecycle_state"] = "STABLE"
    assert adapter.read_lifecycle(event_id)["lifecycle_state"] == "LABILE"
    event = adapter.read_event(event_id)
    assert event["observation"] == "rule"
    assert event["evidence_ref"]


def test_relation_provenance_and_trace_are_read_only() -> None:
    adapter = MemoryAdapter(seed=7)
    root = adapter.submit_signal(
        "promote",
        point_id=adapter.submit_observation("start"),
        reason="task-relevance",
    )["result"]["event_id"]
    thread_id = adapter.submit_signal("open_thread", event_id=root, topic="alpha")["result"]["thread_id"]
    extra = adapter.submit_signal(
        "promote",
        point_id=adapter.submit_observation("continue"),
        reason="repeated-reference",
    )["result"]["event_id"]
    adapter.submit_signal("extend", thread_id=thread_id, event_id=extra, signal="same-topic")
    branch = adapter.submit_signal(
        "promote",
        point_id=adapter.submit_observation("branch"),
        reason="task-relevance",
    )["result"]["event_id"]
    child = adapter.submit_signal("split", thread_id=thread_id, event_id=branch, new_topic="new-context")
    relations = adapter.read_relations()
    split = [row for row in relations if row["relation_type"] == "contextual.changed_context"]
    assert len(split) == 1
    assert split[0]["evidence_ref"] == "new-context"
    assert split[0]["target_id"] == child["result"]["thread_id"]
    with pytest.raises(TypeError):
        relations[0]["evidence_ref"] = "rewritten"
    trace = adapter.inspect_trace()
    assert trace[-1]["trigger"]
    assert trace[-1]["evidence_refs"]
    with pytest.raises(TypeError):
        trace[-1]["target_state"] = "DELETED"


def test_same_signals_replay_same_trace_digest() -> None:
    def run() -> str:
        adapter = MemoryAdapter(seed=11, context_budget=4, policy="none")
        event_id = adapter.submit_signal(
            "promote",
            point_id=adapter.submit_observation("same"),
            reason="task-relevance",
        )["result"]["event_id"]
        adapter.submit_signal("consolidate", event_id=event_id, evidence="repeat")
        adapter.retrieve("same")
        return adapter.trace_digest()

    assert run() == run()


def test_storage_port_is_not_implemented() -> None:
    port = DurableStorePort()
    with pytest.raises(NotImplementedError):
        port.load_snapshot()
    with pytest.raises(NotImplementedError):
        port.save_snapshot({})
