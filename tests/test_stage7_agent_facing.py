"""Stage 7 heterogeneous agent-facing wrappers over the Stage 6 boundary."""

from memory_infra.clients import EnvelopeCaller, MethodCaller
from memory_infra.store import FileDurableStore, InMemoryDurableStore, MemoryService, SnapshotError, _restart_capability


def _service(store):
    return MemoryService(store=store, seed=7, context_budget=4, policy="none")


def _exercise(service: MemoryService) -> None:
    method = MethodCaller(service, "method-agent")
    envelope = EnvelopeCaller(service, "envelope-agent")
    observed = method.observe("alpha fact", note="method-private")
    envelope.submit(
        {
            "op": "observe",
            "client_meta": {"shape": "envelope", "local_only": True},
            "payload": {"content": "beta fact", "note": "envelope-private"},
        }
    )
    method_ctx = method.read_context()["result"]
    envelope_ctx = envelope.submit({"op": "read_caller_context", "payload": {}})["result"]
    assert method_ctx["notes"] == ("method-private",)
    assert envelope_ctx["notes"] == ("envelope-private",)
    assert method_ctx["attributions"][0]["point_id"] == observed["point_id"]
    assert all(item["content"] != "beta fact" for item in method_ctx["attributions"])
    assert all(item["content"] != "alpha fact" for item in envelope_ctx["attributions"])
    assert method.local_log[0] == "observe:alpha fact"
    assert envelope.sent[0]["client_meta"]["shape"] == "envelope"
    event = method.signal("promote", point_id=observed["point_id"], reason="useful")["result"]["result"]["event_id"]
    shared = envelope.submit({"op": "read_event", "payload": {"event_id": event}})["result"]
    assert shared["observation"] == "alpha fact"
    assert method.read_lifecycle(event)["result"]["lifecycle_state"]
    with __import__("pytest").raises(SnapshotError, match="caller cannot impersonate another caller"):
        envelope.submit({"op": "read_caller_context", "payload": {"caller_id": "method-agent"}})
    with __import__("pytest").raises(SnapshotError, match="caller cannot address another caller scope"):
        method.signal("promote", point_id=observed["point_id"], reason="useful", target_caller_id="envelope-agent")
    with __import__("pytest").raises(SnapshotError, match="caller cannot own mechanism fields"):
        envelope.submit(
            {
                "op": "signal",
                "payload": {
                    "name": "promote",
                    "point_id": observed["point_id"],
                    "reason": "useful",
                    "assign_ids": True,
                },
            }
        )


def test_heterogeneous_clients_share_mechanism_not_context(tmp_path):
    _exercise(_service(InMemoryDurableStore()))
    _exercise(_service(FileDurableStore(tmp_path / "snap.json")))


def test_save_load_keeps_mechanism_and_drops_caller_context(tmp_path):
    service = _service(FileDurableStore(tmp_path / "snap.json"))
    method = MethodCaller(service, "method-agent")
    observed = method.observe("kept fact", note="not-durable")
    method.signal("promote", point_id=observed["point_id"], reason="useful")
    method.save()
    reloaded = MemoryService(
        store=FileDurableStore(tmp_path / "snap.json", seal_key=_restart_capability(service.store)),
        seed=7,
        context_budget=4,
        policy="none",
    )
    restored = MethodCaller(reloaded, "method-agent")
    restored.load()
    assert restored.read_context()["result"]["notes"] == ()
    assert restored.read_context()["result"]["attributions"] == ()
    assert len(reloaded.adapter._graph.points) == 1
    assert next(iter(reloaded.adapter._graph.events.values())).observation == "kept fact"
