"""Contract tests for the Stage 3 persistence seam."""

import copy

import pytest

from memory_infra.adapter import BoundaryError, DurableStorePort
from memory_infra.store import (
    InMemoryDurableStore,
    MemoryService,
    SnapshotError,
    export_snapshot,
    restore_graph,
)


def _populated():
    service = MemoryService(seed=7, context_budget=4, policy="none")
    point_id = service.adapter.submit_observation("ship the boundary", "caller")
    service.adapter.submit_signal("promote", point_id=point_id, reason="useful")
    event_id = service.adapter.read_relations() and service.adapter._graph.events
    event_id = next(iter(service.adapter._graph.events))
    service.adapter.submit_signal("open_thread", event_id=event_id, topic="boundary")
    service.adapter.submit_signal("decay", target_id=event_id)
    service.adapter.retrieve("boundary")
    return service


def test_round_trip_preserves_state_and_trace():
    service = _populated()
    before_trace = service.adapter.trace_digest()
    before_relations = service.adapter.read_relations()
    before_event = next(iter(service.adapter._graph.events))
    service.save()
    other = MemoryService(store=service.store, seed=1, context_budget=1, policy="automatic")
    other.load()
    assert other.adapter.trace_digest() == before_trace
    assert other.adapter.read_relations() == before_relations
    assert other.adapter.read_event(before_event)["evidence_ref"] == service.adapter.read_event(before_event)["evidence_ref"]
    assert other.adapter.read_lifecycle(before_event)["lifecycle_state"] == service.adapter.read_lifecycle(before_event)["lifecycle_state"]
    assert other.adapter._graph.tick == service.adapter._graph.tick
    assert other.adapter._graph._n == service.adapter._graph._n


def test_malformed_and_incompatible_snapshots_rejected():
    service = _populated()
    snapshot = export_snapshot(service.adapter._graph)
    store = InMemoryDurableStore()
    broken = copy.deepcopy(snapshot)
    broken["version"] = 99
    with pytest.raises(SnapshotError):
        store.save_snapshot(broken)
    missing = copy.deepcopy(snapshot)
    del missing["trace"]
    with pytest.raises(SnapshotError):
        store.save_snapshot(missing)
    rewritten = copy.deepcopy(snapshot)
    rewritten["integrity"] = "0" * 64
    with pytest.raises(SnapshotError):
        restore_graph(rewritten)


def test_caller_cannot_manufacture_ownership_through_persistence():
    service = _populated()
    snapshot = export_snapshot(service.adapter._graph)
    snapshot["caller_lifecycle"] = "STABLE"
    store = InMemoryDurableStore()
    with pytest.raises(SnapshotError):
        store.save_snapshot(snapshot)
    mutated = copy.deepcopy(export_snapshot(service.adapter._graph))
    event_id = next(iter(mutated["events"]))
    mutated["states"][event_id]["lifecycle_state"] = "STABLE"
    with pytest.raises(SnapshotError):
        store.save_snapshot(mutated)
    with pytest.raises(SnapshotError):
        service.request("save", {"rewrite_lifecycle": True})


def test_existing_adapter_mutation_protection_remains():
    service = _populated()
    with pytest.raises(BoundaryError):
        service.adapter.submit_signal("decay", target_id="evt-7-1", lifecycle_state="STABLE")
    port = DurableStorePort()
    with pytest.raises(NotImplementedError):
        port.load_snapshot()


def test_service_request_boundary_round_trip():
    service = MemoryService()
    observed = service.request("observe", {"content": "persist me"})
    service.request("signal", {"name": "promote", "point_id": observed["point_id"], "reason": "keep"})
    service.request("save")
    reloaded = MemoryService(store=service.store)
    loaded = reloaded.request("load")
    assert loaded["integrity"]
    assert reloaded.adapter.inspect_trace() == service.adapter.inspect_trace()
