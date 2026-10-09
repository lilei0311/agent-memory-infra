"""Pin the public Skill API contract in docs/SKILL_API.md to current code."""

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
