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
        assert str(exc) == "caller cannot own mechanism fields: ['nodes']"
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
    with pytest.raises(BoundaryError) as signal_owned:
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
    assert str(signal_owned.value) == "caller cannot set mechanism-owned fields: ['lifecycle_state']"
    assert not isinstance(signal_owned.value, SnapshotError)


def test_caller_scope_ownership_and_impersonation_are_rejected():
    api = SkillApi.open_memory()
    with pytest.raises(SnapshotError) as scope:
        api.invoke("agent-a", "read_caller_context", {"target_caller_id": "agent-b"})
    assert str(scope.value) == "caller cannot address another caller scope: ['target_caller_id']"
    with pytest.raises(SnapshotError) as owned:
        api.invoke("agent-a", "observe", {"content": "fact", "assign_ids": True})
    assert str(owned.value) == "caller cannot own mechanism fields: ['assign_ids']"
    with pytest.raises(SnapshotError) as impersonated:
        api.invoke("agent-a", "observe", {"content": "fact", "caller_id": "agent-b"})
    assert str(impersonated.value) == "caller cannot impersonate another caller"


def test_empty_caller_id_errors_match_contract():
    with pytest.raises(ValueError) as empty:
        SkillEntrypoint().open("")
    assert str(empty.value) == "caller_id is required"
    api = SkillApi.open_memory()
    with pytest.raises(SnapshotError) as blank:
        api.invoke("  ", "inspect_trace")
    assert str(blank.value) == "caller_id must be a non-empty string"


def test_entrypoint_backend_errors_match_contract():
    with pytest.raises(ValueError) as backend:
        SkillEntrypoint(backend="sqlite")
    assert str(backend.value) == "backend must be memory or file"
    with pytest.raises(ValueError) as missing:
        SkillEntrypoint(backend="file")
    assert str(missing.value) == "file backend requires a path"


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


def test_scope_and_ownership_errors_include_sorted_fields():
    api = SkillApi.open_memory()
    with pytest.raises(SnapshotError) as scope:
        api.invoke("agent-a", "read_caller_context", {"target_caller_id": "agent-b"})
    assert str(scope.value) == "caller cannot address another caller scope: ['target_caller_id']"
    with pytest.raises(SnapshotError) as owned:
        api.invoke("agent-a", "observe", {"content": "fact", "assign_ids": True})
    assert str(owned.value) == "caller cannot own mechanism fields: ['assign_ids']"
    with pytest.raises(SnapshotError) as graph:
        api.invoke("agent-a", "read_graph", {"nodes": []})
    assert str(graph.value) == "caller cannot own mechanism fields: ['nodes']"


def test_unknown_target_event_and_empty_note_match_contract():
    api = SkillApi.open_memory()
    with pytest.raises(BoundaryError, match="unknown target: missing"):
        api.invoke("agent-a", "read_lifecycle", {"target_id": "missing"})
    with pytest.raises(BoundaryError, match="unknown event: missing"):
        api.invoke("agent-a", "read_event", {"event_id": "missing"})
    with pytest.raises(SnapshotError, match="caller note must be a non-empty string"):
        api.invoke("agent-a", "observe", {"content": "fact", "note": ""})


def test_enable_memory_requires_discovery():
    handle = SkillEntrypoint().open("agent-a")
    with pytest.raises(RuntimeError, match="discovery must complete before memory operations"):
        handle.enable_memory()


def test_decay_signal_result_keys_match_contract():
    api = SkillApi.open_memory()
    observed = api.invoke("agent-a", "observe", {"content": "fact"})
    promoted = api.invoke(
        "agent-a",
        "signal",
        {"name": "promote", "point_id": observed["point_id"], "reason": "explicit"},
    )
    event_id = promoted["result"]["result"]["event_id"]
    decayed = api.invoke("agent-a", "signal", {"name": "decay", "target_id": event_id})
    assert decayed["result"]["signal"] == "decay"
    assert set(decayed["result"]["result"]) == {"target_id", "lifecycle_state"}
    assert decayed["result"]["result"]["target_id"] == event_id
    context = api.invoke("agent-a", "read_caller_context")
    assert isinstance(context["result"]["notes"], tuple)
    assert isinstance(context["result"]["attributions"], tuple)


def test_rejected_keys_are_sorted_and_signal_ownership_is_distinct():
    api = SkillApi.open_memory()
    with pytest.raises(SnapshotError) as scope:
        api.invoke(
            "agent-a",
            "read_caller_context",
            {"impersonate": "agent-b", "target_caller_id": "agent-c", "all_caller_contexts": True},
        )
    assert str(scope.value) == (
        "caller cannot address another caller scope: "
        "['all_caller_contexts', 'impersonate', 'target_caller_id']"
    )
    with pytest.raises(SnapshotError) as owned:
        api.invoke(
            "agent-a",
            "observe",
            {"rewrite_threads": True, "content": "fact", "assign_ids": True, "delete": True},
        )
    assert str(owned.value) == (
        "caller cannot own mechanism fields: ['assign_ids', 'delete', 'rewrite_threads']"
    )
    with pytest.raises(SnapshotError) as graph:
        api.invoke("agent-a", "read_graph", {"graph": {}, "edges": [], "nodes": []})
    assert str(graph.value) == "caller cannot own mechanism fields: ['edges', 'graph', 'nodes']"
    with pytest.raises(SnapshotError) as mixed:
        api.invoke("agent-a", "read_graph", {"nodes": [], "assign_ids": True, "edges": []})
    assert str(mixed.value) == "caller cannot own mechanism fields: ['assign_ids']"
    with pytest.raises(SnapshotError) as signal_snapshot:
        api.invoke("agent-a", "signal", {"name": "decay", "target_id": "missing", "overwrite": True, "delete": True})
    assert str(signal_snapshot.value) == "caller cannot own mechanism fields: ['delete', 'overwrite']"
    with pytest.raises(BoundaryError) as signal_boundary:
        api.invoke(
            "agent-a",
            "signal",
            {"name": "decay", "target_id": "missing", "candidate_status": "active", "lifecycle_state": "stable"},
        )
    assert type(signal_boundary.value) is BoundaryError
    assert str(signal_boundary.value) == (
        "caller cannot set mechanism-owned fields: ['candidate_status', 'lifecycle_state']"
    )

def test_rejection_order_and_read_graph_write_keys_match_contract():
    api = SkillApi.open_memory()
    with pytest.raises(SnapshotError) as impersonated:
        api.invoke(
            "agent-a",
            "observe",
            {"content": "fact", "caller_id": "agent-b", "assign_ids": True, "target_caller_id": "agent-c"},
        )
    assert str(impersonated.value) == "caller cannot impersonate another caller"
    with pytest.raises(SnapshotError) as scope_before_graph:
        api.invoke(
            "agent-a",
            "read_graph",
            {"nodes": [], "impersonate": "agent-b", "graph": {}, "caller_contexts": True},
        )
    assert str(scope_before_graph.value) == (
        "caller cannot address another caller scope: ['caller_contexts', 'impersonate']"
    )
    with pytest.raises(SnapshotError) as graph_ids:
        api.invoke(
            "agent-a",
            "read_graph",
            {"thread_id": "t", "point_id": "p", "event_id": "e", "relation_id": "r"},
        )
    assert str(graph_ids.value) == (
        "caller cannot own mechanism fields: ['event_id', 'point_id', 'relation_id', 'thread_id']"
    )
    with pytest.raises(BoundaryError) as signal_relation:
        api.invoke("agent-a", "signal", {"name": "decay", "target_id": "missing", "relation_id": "r"})
    assert type(signal_relation.value) is BoundaryError
    assert str(signal_relation.value) == "caller cannot set mechanism-owned fields: ['relation_id']"


def test_exact_read_shapes_note_scope_and_import_rejection():
    api = SkillApi.open_memory()
    same = api.invoke("agent-a", "observe", {"content": "fact", "caller_id": "agent-a"})
    assert same["caller_id"] == "agent-a" and same["point_id"]
    omitted = api.invoke("agent-a", "observe", {"content": "other"})
    graph = api.invoke("agent-a", "read_graph")
    sources = {node["id"]: node["source"] for node in graph["result"]["nodes"] if node["kind"] == "point"}
    assert sources[omitted["point_id"]] == "agent-a"
    assert graph["result"]["node_kinds"] == ("event", "point", "state", "thread")
    assert graph["result"]["edge_kinds"] == (
        "contextual.changed_context",
        "causal.caused",
        "causal.caused_by",
        "causal.enabled",
        "causal.prevented",
        "evidential.contradicts",
        "referential.revisits",
        "referential.same_thread",
        "temporal.before",
    )
    assert isinstance(graph["result"]["nodes"], tuple) and isinstance(graph["result"]["edges"], tuple)
    noted = api.invoke("agent-a", "retrieve", {"query": "fact", "note": "asked"})
    assert set(noted["result"]) == {"retrieval_id", "query", "selected", "timestamp"}
    assert isinstance(noted["result"]["selected"], tuple)
    context = api.invoke("agent-a", "read_caller_context")
    assert context["result"]["notes"] == ("asked",)
    left = api.invoke("agent-a", "signal", {"name": "promote", "point_id": same["point_id"], "reason": "left"})
    right = api.invoke("agent-a", "signal", {"name": "promote", "point_id": omitted["point_id"], "reason": "right"})
    api.invoke(
        "agent-a",
        "signal",
        {
            "name": "contradict",
            "left_event": left["result"]["result"]["event_id"],
            "right_event": right["result"]["result"]["event_id"],
            "evidence": "conflict",
        },
    )
    life = api.invoke("agent-a", "read_lifecycle", {"target_id": left["result"]["result"]["event_id"]})
    assert set(life["result"]) == {
        "target_id",
        "lifecycle_state",
        "accessibility",
        "recency",
        "retrieval_history",
        "contradiction_history",
    }
    relations = api.invoke("agent-a", "read_relations")
    assert len(relations["result"]) == 1
    assert set(relations["result"][0]) == {
        "relation_id",
        "source_id",
        "target_id",
        "relation_type",
        "evidence_ref",
        "inferred",
    }
    with pytest.raises(SnapshotError) as blank:
        api.invoke("   ", "read_relations")
    assert str(blank.value) == "caller_id must be a non-empty string"
    with pytest.raises(ValueError) as opened:
        SkillEntrypoint().open("   ")
    assert str(opened.value) == "caller_id is required"
    early = SkillEntrypoint().open("agent-a")
    with pytest.raises(RuntimeError) as imported:
        early.import_selected(["missing.md"])
    assert str(imported.value) == "explicit import requires completed discovery"
    started = early.start(artifacts={})
    report = early.import_selected(["missing.md"])
    assert report["rejected"] == [{"path": "missing.md", "status": "rejected", "reason": "not_in_discovery"}]
    assert started["mechanism_memory_created"] is False
    other = SkillEntrypoint().open("agent-b")
    assert other.inventory() is None
    assert early.inventory() is not None
