"""Stage 5 integration matrix. Does not change V0.2 transitions."""

from memory_infra.adapter import BoundaryError
from memory_infra.store import (
    FileDurableStore,
    InMemoryDurableStore,
    MemoryService,
    SnapshotError,
    _restart_capability,
)


def _service(store):
    return MemoryService(store=store, seed=7, context_budget=4, policy="none")


def _run(service: MemoryService) -> dict:
    observed = service.request("observe", {"content": "alpha fact", "source": "caller"})
    promoted = service.request(
        "signal",
        {"name": "promote", "point_id": observed["point_id"], "reason": "useful"},
    )
    event_id = promoted["result"]["result"]["event_id"]
    opened = service.request("signal", {"name": "open_thread", "event_id": event_id, "topic": "boundary"})
    service.request("signal", {"name": "decay", "target_id": event_id})
    service.request("retrieve", {"query": "alpha"})
    return {
        "event_id": event_id,
        "thread_id": opened["result"]["result"]["thread_id"],
        "lifecycle": service.request("read_lifecycle", {"target_id": event_id})["result"],
        "event": service.request("read_event", {"event_id": event_id})["result"],
        "relations": service.request("read_relations")["result"],
        "trace": service.request("inspect_trace")["result"],
    }


def test_in_memory_and_file_satisfy_same_request_contract(tmp_path):
    memory = _run(_service(InMemoryDurableStore()))
    file_service = _service(FileDurableStore(tmp_path / "snap.json"))
    filed = _run(file_service)
    assert filed["event_id"] == memory["event_id"]
    assert filed["thread_id"] == memory["thread_id"]
    assert filed["lifecycle"]["lifecycle_state"] == memory["lifecycle"]["lifecycle_state"]
    assert filed["event"]["event_id"] == memory["event"]["event_id"]
    assert filed["event"]["evidence_ref"] == memory["event"]["evidence_ref"]
    assert [row["relation_type"] for row in filed["relations"]] == [
        row["relation_type"] for row in memory["relations"]
    ]
    assert [row["kind"] for row in filed["trace"]] == [row["kind"] for row in memory["trace"]]
    file_service.request("save")
    restarted = MemoryService(
        store=FileDurableStore(tmp_path / "snap.json", seal_key=_restart_capability(file_service.store)),
        seed=7,
        context_budget=4,
        policy="none",
    )
    restarted.request("load")
    restored = restarted.request("read_event", {"event_id": filed["event_id"]})["result"]
    assert restored["event_id"] == filed["event_id"]
    assert restored["evidence_ref"] == filed["event"]["evidence_ref"]
    assert restarted.request("read_lifecycle", {"target_id": filed["event_id"]})["result"][
        "lifecycle_state"
    ] == filed["lifecycle"]["lifecycle_state"]
    assert restarted.request("inspect_trace")["result"][-1]["target_id"] == filed["trace"][-1]["target_id"]


def test_separate_service_instances_do_not_share_mechanism_state(tmp_path):
    left = _service(InMemoryDurableStore())
    right = _service(FileDurableStore(tmp_path / "other.json"))
    left_view = _run(left)
    assert right.request("read_relations")["result"] == ()
    with __import__("pytest").raises(KeyError):
        right.adapter._graph.events[left_view["event_id"]]
    right.request("observe", {"content": "other fact", "source": "caller"})
    assert left.request("read_event", {"event_id": left_view["event_id"]})["result"]["observation"] == "alpha fact"
    assert len(left.adapter._graph.points) == 1
    assert len(right.adapter._graph.points) == 1
    assert next(iter(right.adapter._graph.points.values())).content == "other fact"


def test_service_request_cannot_set_mechanism_owned_fields(tmp_path):
    """Each forbidden field is rejected on an otherwise valid promote request.

    A missing point_id must not be the reason the assertion passes.
    """
    import pytest

    service_owned = (
        "assign_ids",
        "rewrite_lifecycle",
        "rewrite_threads",
        "rewrite_relations",
        "caller_lifecycle",
        "overwrite",
        "delete",
    )
    signal_owned = (
        "lifecycle_state",
        "candidate_status",
        "status",
        "member_event_ids",
        "accessibility",
        "evidence_ref",
        "relation_id",
        "trace",
    )
    stores = (InMemoryDurableStore(), FileDurableStore(tmp_path / "snap.json"))
    for store in stores:
        service = _service(store)
        observed = service.request("observe", {"content": "owned-field probe", "source": "caller"})
        point_id = observed["point_id"]
        accepted = service.request(
            "signal",
            {"name": "promote", "point_id": point_id, "reason": "useful"},
        )
        assert accepted["ok"] is True
        for field in service_owned:
            with pytest.raises(SnapshotError, match="caller cannot own mechanism fields") as caught:
                service.request(
                    "signal",
                    {
                        "name": "promote",
                        "point_id": point_id,
                        "reason": "useful",
                        field: "caller",
                    },
                )
            assert field in str(caught.value)
        for field in signal_owned:
            with pytest.raises(BoundaryError, match="caller cannot set mechanism-owned fields") as caught:
                service.request(
                    "signal",
                    {
                        "name": "promote",
                        "point_id": point_id,
                        "reason": "useful",
                        field: "caller",
                    },
                )
            assert field in str(caught.value)
