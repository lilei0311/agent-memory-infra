"""Stage 6 caller attribution and isolation. Does not change V0.2 transitions."""

import pytest

from memory_infra.store import (
    CallerSession,
    FileDurableStore,
    InMemoryDurableStore,
    MemoryService,
    SnapshotError,
    _restart_capability,
)


def _service(store):
    return MemoryService(store=store, seed=7, context_budget=4, policy="none")


def _assert_isolated(service: MemoryService) -> None:
    agent_a = CallerSession(service, "agent-a")
    agent_b = CallerSession(service, "agent-b")
    observed = agent_a.request(
        "observe",
        {"content": "alpha fact", "note": "a-private"},
    )
    agent_b.request("observe", {"content": "beta fact", "note": "b-private"})
    context_a = agent_a.request("read_caller_context")["result"]
    context_b = agent_b.request("read_caller_context")["result"]
    assert context_a["notes"] == ("a-private",)
    assert context_b["notes"] == ("b-private",)
    assert context_a["attributions"][0]["point_id"] == observed["point_id"]
    assert all(item["content"] != "beta fact" for item in context_a["attributions"])
    assert all(item["content"] != "alpha fact" for item in context_b["attributions"])
    event = agent_a.request(
        "signal",
        {"name": "promote", "point_id": observed["point_id"], "reason": "useful"},
    )["result"]["result"]["event_id"]
    assert agent_b.request("read_event", {"event_id": event})["result"]["observation"] == "alpha fact"
    with pytest.raises(SnapshotError, match="caller cannot impersonate another caller"):
        agent_b.request("read_caller_context", {"caller_id": "agent-a"})
    with pytest.raises(SnapshotError, match="caller cannot address another caller scope"):
        agent_b.request("read_caller_context", {"target_caller_id": "agent-a"})
    with pytest.raises(SnapshotError, match="caller cannot own mechanism fields"):
        agent_a.request(
            "signal",
            {
                "name": "promote",
                "point_id": observed["point_id"],
                "reason": "useful",
                "assign_ids": True,
            },
        )


def test_caller_contexts_are_isolated_on_both_stores(tmp_path):
    _assert_isolated(_service(InMemoryDurableStore()))
    _assert_isolated(_service(FileDurableStore(tmp_path / "snap.json")))


def test_caller_notes_are_not_mechanism_snapshot_state(tmp_path):
    service = _service(FileDurableStore(tmp_path / "snap.json"))
    session = CallerSession(service, "agent-a")
    session.request("observe", {"content": "kept fact", "note": "not-durable"})
    service.request("save")
    reloaded = MemoryService(
        store=FileDurableStore(tmp_path / "snap.json", seal_key=_restart_capability(service.store)),
        seed=7,
        context_budget=4,
        policy="none",
    )
    reloaded.request("load")
    restored = CallerSession(reloaded, "agent-a").request("read_caller_context")["result"]
    assert restored["notes"] == ()
    assert restored["attributions"] == ()
    assert len(reloaded.adapter._graph.points) == 1
