"""Reusable Stage 9 Skill/API conformance suite.

Future callers pass a zero-argument factory that returns the public surface
(open_caller, invoke, reopen). This module does not import store internals.
"""

from __future__ import annotations

from typing import Callable, Mapping, Protocol

import pytest

from memory_infra.skill import SUPPORTED_OPS, SnapshotError


class SkillSurface(Protocol):
    def open_caller(self, caller_id: str): ...

    def invoke(self, caller_id: str, op: str, payload: Mapping | None = None) -> Mapping: ...

    def reopen(self) -> "SkillSurface": ...


def assert_trace(response: Mapping, event_id: str) -> None:
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


def assert_conformance(open_api: Callable[[], SkillSurface]) -> None:
    api = open_api()
    left = api.open_caller("conf-left")
    right = api.open_caller("conf-right")

    observed = left.invoke(
        "observe",
        {"content": "conformance fact", "note": "left-only", "point_id": "caller-picked"},
    )
    assert observed["ok"] is True
    assert observed["op"] == "observe"
    assert observed["point_id"] != "caller-picked"
    assert observed["point_id"]
    right.invoke("observe", {"content": "other fact", "note": "right-only"})

    left_ctx = left.invoke("read_caller_context")
    right_ctx = right.invoke("read_caller_context")
    assert left_ctx["ok"] is True and left_ctx["op"] == "read_caller_context"
    assert left_ctx["result"]["notes"] == ("left-only",)
    assert right_ctx["result"]["notes"] == ("right-only",)
    assert all(item["content"] != "other fact" for item in left_ctx["result"]["attributions"])
    assert all(item["content"] != "conformance fact" for item in right_ctx["result"]["attributions"])

    signaled = left.invoke(
        "signal",
        {"name": "promote", "point_id": observed["point_id"], "reason": "useful"},
    )
    assert signaled["ok"] is True and signaled["op"] == "signal"
    event_id = signaled["result"]["result"]["event_id"]
    assert event_id and event_id != observed["point_id"]

    shared = right.invoke("read_event", {"event_id": event_id})
    assert shared["ok"] is True and shared["op"] == "read_event"
    assert shared["result"]["observation"] == "conformance fact"
    lifecycle = left.invoke("read_lifecycle", {"target_id": event_id})
    assert lifecycle["ok"] is True and lifecycle["result"]["lifecycle_state"]
    relations = right.invoke("read_relations")
    assert relations["ok"] is True and relations["op"] == "read_relations"
    assert isinstance(relations["result"], tuple)
    assert_trace(left.invoke("inspect_trace"), event_id)

    ranked = right.invoke("retrieve", {"query": "conformance fact"})
    assert ranked["ok"] is True and ranked["op"] == "retrieve"
    assert ranked["result"]

    with pytest.raises(SnapshotError, match="caller cannot impersonate another caller"):
        left.invoke("read_caller_context", {"caller_id": "conf-right"})
    with pytest.raises(SnapshotError, match="caller cannot address another caller scope"):
        right.invoke(
            "signal",
            {
                "name": "promote",
                "point_id": observed["point_id"],
                "reason": "useful",
                "target_caller_id": "conf-left",
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
        api.invoke("conf-left", "assign_ids", {})
    assert "assign_ids" not in SUPPORTED_OPS

    saved = left.invoke("save")
    assert saved["ok"] is True and saved["op"] == "save"
    assert isinstance(saved["integrity"], str) and saved["integrity"]
    restored = api.reopen().open_caller("conf-left")
    loaded = restored.invoke("load")
    assert loaded["ok"] is True and loaded["op"] == "load"
    assert loaded["integrity"] == saved["integrity"]
    context = restored.invoke("read_caller_context")["result"]
    assert context["notes"] == ()
    assert context["attributions"] == ()
    assert_trace(restored.invoke("inspect_trace"), event_id)
    again = api.reopen().open_caller("conf-right")
    again.invoke("load")
    shared_after = again.invoke("read_event", {"event_id": event_id})
    assert shared_after["result"]["observation"] == "conformance fact"
    assert "left-only" not in str(shared_after["result"])
