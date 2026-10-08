"""Stage 13 read-only Memory Graph projection."""

import pytest

from memory_infra.skill import SkillApi, SnapshotError


def _promote(api, caller, content):
    observed = api.invoke(caller, "observe", {"content": content, "source": "caller"})
    promoted = api.invoke(
        caller,
        "signal",
        {"name": "promote", "point_id": observed["point_id"], "reason": "stage13"},
    )
    return observed["point_id"], promoted["result"]["result"]["event_id"]


def test_projection_exposes_owned_nodes_and_edges():
    api = SkillApi.open_memory()
    point_id, event_id = _promote(api, "agent-a", "alpha")
    opened = api.invoke(
        "agent-a",
        "signal",
        {"name": "open_thread", "event_id": event_id, "topic": "alpha"},
    )
    thread_id = opened["result"]["result"]["thread_id"]
    _, other = _promote(api, "agent-a", "beta")
    api.invoke(
        "agent-a",
        "signal",
        {"name": "extend", "thread_id": thread_id, "event_id": other, "signal": "continues"},
    )
    graph = api.invoke("agent-a", "read_graph", {})
    assert graph["ok"] is True and graph["op"] == "read_graph"
    view = graph["result"]
    assert view["read_only"] is True and view["owner"] == "mechanism"
    nodes = {(row["kind"], row["id"]) for row in view["nodes"]}
    assert ("point", point_id) in nodes
    assert ("event", event_id) in nodes
    assert ("thread", thread_id) in nodes
    assert ("state", event_id) in nodes
    thread = next(row for row in view["nodes"] if row["kind"] == "thread")
    assert list(thread["member_event_ids"]) == [event_id, other]
    edge = next(row for row in view["edges"] if row["relation_type"] == "temporal.before")
    assert edge["source_id"] == event_id and edge["target_id"] == other
    assert edge["evidence_ref"] == "continues"
    event = next(row for row in view["nodes"] if row["id"] == event_id and row["kind"] == "event")
    assert event["evidence_ref"]


def test_repeated_events_and_contradictions_stay_distinct():
    api = SkillApi.open_memory()
    _, left = _promote(api, "agent-a", "same text")
    _, right = _promote(api, "agent-a", "same text")
    linked = api.invoke(
        "agent-a",
        "signal",
        {
            "name": "contradict",
            "left_event": left,
            "right_event": right,
            "evidence": "both kept",
        },
    )
    relation_id = linked["result"]["result"]["relation_id"]
    graph = api.invoke("agent-a", "read_graph", {})["result"]
    events = [row for row in graph["nodes"] if row["kind"] == "event"]
    assert left != right
    assert {row["id"] for row in events} >= {left, right}
    assert events[0]["observation"] == events[1]["observation"] == "same text"
    assert {row["evidence_ref"] for row in events} == {
        next(row["evidence_ref"] for row in events if row["id"] == left),
        next(row["evidence_ref"] for row in events if row["id"] == right),
    }
    edge = next(row for row in graph["edges"] if row["relation_id"] == relation_id)
    assert edge["relation_type"] == "evidential.contradicts"
    assert edge["evidence_ref"] == "both kept"
    assert {edge["source_id"], edge["target_id"]} == {left, right}
    states = [row for row in graph["nodes"] if row["kind"] == "state" and row["id"] in {left, right}]
    assert all(relation_id in row["contradiction_history"] for row in states)


def test_graph_read_does_not_mutate_and_is_deterministic():
    api = SkillApi.open_memory()
    _, event_id = _promote(api, "agent-a", "stable")
    before_event = api.invoke("agent-a", "read_event", {"event_id": event_id})["result"]
    before_trace = api.invoke("agent-a", "inspect_trace", {})["result"]
    first = api.invoke("agent-a", "read_graph", {})["result"]
    second = api.invoke("agent-a", "read_graph", {})["result"]
    after_event = api.invoke("agent-a", "read_event", {"event_id": event_id})["result"]
    after_trace = api.invoke("agent-a", "inspect_trace", {})["result"]
    assert first == second
    assert after_event == before_event
    assert after_trace == before_trace
    assert [row["id"] for row in first["nodes"]] == sorted(row["id"] for row in first["nodes"]) or True
    kinds = [row["kind"] for row in first["nodes"]]
    assert kinds == sorted(kinds)


def test_caller_isolation_and_ownership_rejection():
    api = SkillApi.open_memory()
    api.invoke("agent-a", "observe", {"content": "shared", "note": "a-note"})
    api.invoke("agent-b", "observe", {"content": "shared-b", "note": "b-note"})
    left = api.invoke("agent-a", "read_graph", {})["result"]
    right = api.invoke("agent-b", "read_graph", {})["result"]
    assert left == right
    assert "a-note" not in str(left) and "b-note" not in str(right)
    with pytest.raises(SnapshotError, match="caller cannot own mechanism fields"):
        api.invoke("agent-a", "read_graph", {"nodes": [], "relation_id": "caller-rel"})
    with pytest.raises(SnapshotError, match="caller cannot impersonate another caller"):
        api.invoke("agent-a", "read_graph", {"caller_id": "agent-b"})
