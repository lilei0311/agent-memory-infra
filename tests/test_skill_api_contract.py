"""Pin the public Skill API contract in docs/SKILL_API.md to current code."""

import pytest

from memory_infra.adapter import BoundaryError
from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.skill import SUPPORTED_OPS, SkillApi, SnapshotError

DOCUMENTED_OPS = (
    "observe",
    "signal",
    "retrieve",
    "read_lifecycle",
    "read_event",
    "read_relations",
    "read_graph",
    "inspect_trace",
    "read_caller_context",
    "save",
    "load",
)


def test_supported_ops_match_contract():
    assert SUPPORTED_OPS == DOCUMENTED_OPS
    assert "render_explorer" not in SUPPORTED_OPS


def test_unknown_op_and_read_graph_are_not_writes():
    api = SkillApi.open_memory()
    before = api.invoke("agent-a", "inspect_trace")["result"]
    try:
        api.invoke("agent-a", "not-an-op")
    except SnapshotError as exc:
        assert str(exc) == "unsupported skill operation"
    else:
        raise AssertionError("unknown op must fail")
    graph = api.invoke("agent-a", "read_graph")
    assert graph["ok"] is True and graph["op"] == "read_graph"
    assert graph["result"]["read_only"] is True
    assert graph["result"]["owner"] == "mechanism"
    after = api.invoke("agent-a", "inspect_trace")["result"]
    assert after == before
    try:
        api.invoke("agent-a", "read_graph", {"nodes": []})
    except SnapshotError as exc:
        assert "caller cannot own mechanism fields" in str(exc)
    else:
        raise AssertionError("read_graph write payload must fail")


def test_missing_feedback_is_not_guessed():
    api = SkillApi.open_memory()
    observed = api.invoke("agent-a", "observe", {"content": "no feedback supplied"})
    assert "user_feedback" not in observed
    assert "task_success" not in observed
    assert observed["point_id"]


def test_entrypoint_requires_discovery_before_invoke():
    handle = SkillEntrypoint().open("agent-a")
    try:
        handle.invoke("observe", {"content": "too early"})
    except RuntimeError as exc:
        assert "discovery" in str(exc)
    else:
        raise AssertionError("invoke before discovery must fail")
    started = handle.start(artifacts={})
    assert started["memory_operations_enabled"] is False
    assert started["mechanism_memory_created"] is False


@pytest.mark.parametrize(
    ("op", "payload"),
    [
        ("observe", {}),
        ("signal", {}),
        ("retrieve", {}),
        ("read_lifecycle", {}),
        ("read_event", {}),
    ],
)
def test_missing_required_operation_fields_raise_key_error(op, payload):
    api = SkillApi.open_memory()
    with pytest.raises(KeyError):
        api.invoke("agent-a", op, payload)


def test_empty_observation_is_boundary_error():
    api = SkillApi.open_memory()
    with pytest.raises(BoundaryError, match="observation content is required"):
        api.invoke("agent-a", "observe", {"content": ""})


def test_invalid_signal_and_mechanism_owned_signal_field():
    api = SkillApi.open_memory()
    observed = api.invoke("agent-a", "observe", {"content": "fact"})
    with pytest.raises(BoundaryError, match="unsupported signal: not-a-signal"):
        api.invoke("agent-a", "signal", {"name": "not-a-signal"})
    with pytest.raises(BoundaryError, match="caller cannot set mechanism-owned fields"):
        api.invoke(
            "agent-a",
            "signal",
            {
                "name": "promote",
                "point_id": observed["point_id"],
                "reason": "explicit",
                "lifecycle_state": "stable",
            },
        )


def test_caller_scope_ownership_and_impersonation_are_rejected():
    api = SkillApi.open_memory()
    with pytest.raises(SnapshotError, match="caller cannot address another caller scope"):
        api.invoke("agent-a", "read_caller_context", {"target_caller_id": "agent-b"})
    with pytest.raises(SnapshotError, match="caller cannot own mechanism fields"):
        api.invoke("agent-a", "observe", {"content": "fact", "assign_ids": True})
    with pytest.raises(SnapshotError, match="caller cannot impersonate another caller"):
        api.invoke("agent-a", "observe", {"content": "fact", "caller_id": "agent-b"})


def test_empty_caller_id_errors_match_contract():
    with pytest.raises(ValueError, match="caller_id is required"):
        SkillEntrypoint().open("")
    api = SkillApi.open_memory()
    with pytest.raises(SnapshotError, match="caller_id must be a non-empty string"):
        api.invoke("  ", "inspect_trace")


def test_load_without_snapshot_is_snapshot_error():
    api = SkillApi.open_memory()
    with pytest.raises(SnapshotError, match="no snapshot to load"):
        api.invoke("agent-a", "load")


@pytest.mark.parametrize(
    ("name", "payload"),
    [
        ("promote", {"reason": "explicit"}),
        ("open_thread", {"topic": "topic"}),
        ("extend", {"thread_id": "thread"}),
        ("split", {"thread_id": "thread"}),
        ("merge", {"left_id": "left"}),
        ("reopen", {}),
        ("link_causal", {"source_id": "left"}),
        ("contradict", {"left_event": "left"}),
        ("begin_reconsolidation", {}),
        ("resolve_reconsolidation", {"event_id": "event"}),
        ("consolidate", {}),
        ("decay", {}),
        ("retrieve", {}),
    ],
)
def test_documented_signal_required_fields_are_not_optional(name, payload):
    api = SkillApi.open_memory()
    with pytest.raises(TypeError):
        api.invoke("agent-a", "signal", {"name": name, **payload})


def test_public_operation_envelopes_match_contract():
    api = SkillApi.open_memory()
    observed = api.invoke(
        "agent-a",
        "observe",
        {"content": "fact", "source": "caller", "note": "seen"},
    )
    assert observed["ok"] is True and observed["op"] == "observe"
    assert observed["caller_id"] == "agent-a" and observed["point_id"]
    assert "result" not in observed

    promoted = api.invoke(
        "agent-a",
        "signal",
        {"name": "promote", "point_id": observed["point_id"], "reason": "explicit"},
    )
    assert promoted["ok"] is True and promoted["op"] == "signal"
    assert promoted["caller_id"] == "agent-a"
    assert promoted["result"]["signal"] == "promote"
    assert set(promoted["result"]["result"]) >= {"event_id", "evidence_ref"}
    event_id = promoted["result"]["result"]["event_id"]

    opened = api.invoke(
        "agent-a",
        "signal",
        {"name": "open_thread", "event_id": event_id, "topic": "topic"},
    )
    assert opened["result"]["signal"] == "open_thread"
    assert set(opened["result"]["result"]) >= {"thread_id", "status"}

    retrieved = api.invoke("agent-a", "retrieve", {"query": "fact"})
    assert retrieved["ok"] is True and retrieved["op"] == "retrieve"
    assert set(retrieved["result"]) >= {"retrieval_id", "query", "selected", "timestamp"}

    life = api.invoke("agent-a", "read_lifecycle", {"target_id": event_id})
    assert life["op"] == "read_lifecycle"
    assert set(life["result"]) >= {
        "target_id",
        "lifecycle_state",
        "accessibility",
        "recency",
        "retrieval_history",
        "contradiction_history",
    }

    event = api.invoke("agent-a", "read_event", {"event_id": event_id})
    assert event["result"]["event_id"] == event_id
    assert set(event["result"]) >= {
        "event_id",
        "timestamp",
        "source",
        "observation",
        "evidence_ref",
        "thread_id",
    }

    relations = api.invoke("agent-a", "read_relations")
    assert relations["op"] == "read_relations" and isinstance(relations["result"], tuple)
    graph = api.invoke("agent-a", "read_graph")
    assert graph["result"]["read_only"] is True
    assert graph["result"]["owner"] == "mechanism"
    assert graph["result"]["ordering"] == "kind,id"
    assert set(graph["result"]) >= {"node_kinds", "edge_kinds", "nodes", "edges"}
    trace = api.invoke("agent-a", "inspect_trace")
    assert isinstance(trace["result"], tuple) and trace["result"]
    context = api.invoke("agent-a", "read_caller_context")
    assert context["result"]["caller_id"] == "agent-a"
    assert context["result"]["notes"] and context["result"]["attributions"]

    saved = api.invoke("agent-a", "save")
    assert saved["ok"] is True and saved["op"] == "save" and saved["integrity"]
    assert "result" not in saved
    loaded = api.invoke("agent-a", "load")
    assert loaded["op"] == "load" and loaded["integrity"] == saved["integrity"]
    assert "result" not in loaded
