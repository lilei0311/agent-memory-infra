"""Contract tests for the Stage 3 persistence seam."""

import copy
import hashlib
import json

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


def _recompute_public_checksum(snapshot):
    body = {key: snapshot[key] for key in snapshot if key not in {"integrity", "authenticity"}}
    snapshot["integrity"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return snapshot


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


def test_recomputed_checksum_cannot_authorize_rewritten_snapshot():
    service = _populated()
    other = service.adapter.submit_observation("second fact", "caller")
    service.adapter.submit_signal("promote", point_id=other, reason="useful")
    left, right = list(service.adapter._graph.events)
    service.adapter.submit_signal("contradict", left_event=left, right_event=right, evidence="obs")
    store = InMemoryDurableStore()
    graph = service.adapter._graph
    event_id = next(iter(graph.events))
    thread_id = next(iter(graph.threads))
    relation_id = next(iter(graph.relations))

    lifecycle = copy.deepcopy(export_snapshot(graph))
    lifecycle["states"][event_id]["lifecycle_state"] = "STABLE"
    with pytest.raises(SnapshotError):
        store.save_snapshot(_recompute_public_checksum(lifecycle))

    thread = copy.deepcopy(export_snapshot(graph))
    thread["threads"][thread_id]["status"] = "merged"
    thread["threads"][thread_id]["member_event_ids"] = []
    with pytest.raises(SnapshotError):
        store.save_snapshot(_recompute_public_checksum(thread))

    relation = copy.deepcopy(export_snapshot(graph))
    relation["relations"][relation_id]["target_id"] = event_id
    relation["relations"][relation_id]["evidence_ref"] = "caller-forged"
    with pytest.raises(SnapshotError):
        store.save_snapshot(_recompute_public_checksum(relation))

    counters = copy.deepcopy(export_snapshot(graph))
    counters["counters"]["n"] = counters["counters"]["n"] + 9
    counters["trace"][0]["reason"] = "caller-forged"
    with pytest.raises(SnapshotError):
        store.save_snapshot(_recompute_public_checksum(counters))

    with pytest.raises(SnapshotError):
        restore_graph(_recompute_public_checksum(copy.deepcopy(lifecycle)))


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


def test_instance_seal_is_not_a_source_constant():
    source = open("src/memory_infra/store.py", encoding="utf-8").read()
    assert "_MECHANISM_SEAL_KEY" not in source
    assert "6d656d6f72792d696e667261" not in source
    left = _populated()
    right = _populated()
    assert left._seal_key != right._seal_key
    snapshot = export_snapshot(left.adapter._graph)
    forged = _recompute_public_checksum(copy.deepcopy(snapshot))
    forged["authenticity"] = "0" * 64
    with pytest.raises(SnapshotError):
        left.store.save_snapshot(forged)
    with pytest.raises(SnapshotError):
        restore_graph(forged, left._seal_key)
