"""Black-box Stage 8 Skill/API boundary. Imports only the public seam."""

import pytest

from memory_infra.skill import SUPPORTED_OPS, SkillApi
from memory_infra.store import FileDurableStore, InMemoryDurableStore, MemoryService, SnapshotError, _restart_capability


def _api(store):
    service = MemoryService(store=store, seed=7, context_budget=4, policy="none")
    return service, SkillApi(service)


def _exercise(api: SkillApi) -> None:
    left = api.open_caller("skill-left")
    right = api.open_caller("skill-right")
    observed = left.invoke("observe", {"content": "alpha fact", "note": "left-private"})
    right.invoke("observe", {"content": "beta fact", "note": "right-private"})
    left_ctx = left.invoke("read_caller_context")["result"]
    right_ctx = right.invoke("read_caller_context")["result"]
    assert left_ctx["notes"] == ("left-private",)
    assert right_ctx["notes"] == ("right-private",)
    assert left_ctx["attributions"][0]["point_id"] == observed["point_id"]
    assert all(item["content"] != "beta fact" for item in left_ctx["attributions"])
    assert all(item["content"] != "alpha fact" for item in right_ctx["attributions"])
    event = left.invoke(
        "signal",
        {"name": "promote", "point_id": observed["point_id"], "reason": "useful"},
    )["result"]["result"]["event_id"]
    shared = right.invoke("read_event", {"event_id": event})["result"]
    assert shared["observation"] == "alpha fact"
    assert left.invoke("read_lifecycle", {"target_id": event})["result"]["lifecycle_state"]
    assert right.invoke("read_relations")["result"] is not None
    assert "steps" in left.invoke("inspect_trace")["result"] or left.invoke("inspect_trace")["result"] is not None
    with pytest.raises(SnapshotError, match="caller cannot impersonate another caller"):
        left.invoke("read_caller_context", {"caller_id": "skill-right"})
    with pytest.raises(SnapshotError, match="caller cannot address another caller scope"):
        right.invoke(
            "signal",
            {
                "name": "promote",
                "point_id": observed["point_id"],
                "reason": "useful",
                "target_caller_id": "skill-left",
            },
        )
    with pytest.raises(SnapshotError, match="caller cannot own mechanism fields"):
        left.invoke(
            "signal",
            {
                "name": "promote",
                "point_id": observed["point_id"],
                "reason": "useful",
                "assign_ids": True,
            },
        )
    with pytest.raises(SnapshotError, match="unsupported skill operation"):
        api.invoke("skill-left", "assign_ids", {})
    assert "assign_ids" not in SUPPORTED_OPS
    assert not hasattr(SkillApi, "promote")
    assert not hasattr(api, "points")


def test_skill_api_shares_mechanism_not_context(tmp_path):
    _, memory_api = _api(InMemoryDurableStore())
    _exercise(memory_api)
    _, file_api = _api(FileDurableStore(tmp_path / "snap.json"))
    _exercise(file_api)


def test_skill_api_save_load_keeps_mechanism_only(tmp_path):
    service, api = _api(FileDurableStore(tmp_path / "snap.json"))
    caller = api.open_caller("skill-left")
    observed = caller.invoke("observe", {"content": "kept fact", "note": "not-durable"})
    caller.invoke("signal", {"name": "promote", "point_id": observed["point_id"], "reason": "useful"})
    caller.invoke("save")
    reloaded = MemoryService(
        store=FileDurableStore(tmp_path / "snap.json", seal_key=_restart_capability(service.store)),
        seed=7,
        context_budget=4,
        policy="none",
    )
    restored = SkillApi(reloaded).open_caller("skill-left")
    restored.invoke("load")
    context = restored.invoke("read_caller_context")["result"]
    assert context["notes"] == ()
    assert context["attributions"] == ()
    events = restored.invoke("inspect_trace")
    assert events["result"] is not None
    shared = SkillApi(reloaded).open_caller("skill-right").invoke("read_relations")["result"]
    assert shared is not None
    point = restored.invoke("retrieve", {"query": "kept fact"})
    assert point["result"]
