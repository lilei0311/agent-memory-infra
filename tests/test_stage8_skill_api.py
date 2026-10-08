"""Black-box Stage 8 Skill/API boundary. Imports only the public seam."""

import pytest

from memory_infra.skill import SUPPORTED_OPS, SkillApi, SnapshotError


def _assert_trace(response, event_id: str) -> None:
    assert response["ok"] is True
    assert response["op"] == "inspect_trace"
    steps = response["result"]
    assert isinstance(steps, tuple) and steps
    matched = [row for row in steps if row["target_id"] == event_id]
    assert matched
    row = matched[0]
    assert row["kind"]
    assert row["reason"]
    assert isinstance(row["evidence_refs"], tuple) and row["evidence_refs"]
    assert "note" not in row
    assert "caller_id" not in row


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
    relations = right.invoke("read_relations")
    assert relations["ok"] is True
    assert relations["op"] == "read_relations"
    assert isinstance(relations["result"], tuple)
    _assert_trace(left.invoke("inspect_trace"), event)
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
    _exercise(SkillApi.open_memory())
    _exercise(SkillApi.open_file(tmp_path / "snap.json"))


def test_skill_api_save_load_keeps_mechanism_only(tmp_path):
    for api in (SkillApi.open_memory(), SkillApi.open_file(tmp_path / "file.json")):
        caller = api.open_caller("skill-left")
        observed = caller.invoke("observe", {"content": "kept fact", "note": "not-durable"})
        event = caller.invoke(
            "signal",
            {"name": "promote", "point_id": observed["point_id"], "reason": "useful"},
        )["result"]["result"]["event_id"]
        saved = caller.invoke("save")
        assert saved["ok"] is True
        assert saved["op"] == "save"
        assert isinstance(saved["integrity"], str) and saved["integrity"]
        restored_api = api.reopen()
        restored = restored_api.open_caller("skill-left")
        loaded = restored.invoke("load")
        assert loaded["ok"] is True
        assert loaded["op"] == "load"
        assert loaded["integrity"] == saved["integrity"]
        context = restored.invoke("read_caller_context")["result"]
        assert context["notes"] == ()
        assert context["attributions"] == ()
        _assert_trace(restored.invoke("inspect_trace"), event)
        shared = restored_api.open_caller("skill-right").invoke("read_event", {"event_id": event})
        assert shared["result"]["observation"] == "kept fact"
        point = restored.invoke("retrieve", {"query": "kept fact"})
        assert point["ok"] is True
        assert point["result"]
