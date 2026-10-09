"""Stage 14 read-only Visual Memory Explorer."""

import ast
from pathlib import Path

import pytest

from memory_infra.explorer import EDGE_KINDS, NODE_KINDS, presentation_key, render_explorer
from memory_infra.skill import SkillApi, SnapshotError


def _promote(api, caller, content):
    observed = api.invoke(caller, "observe", {"content": content, "source": "caller"})
    promoted = api.invoke(
        caller,
        "signal",
        {"name": "promote", "point_id": observed["point_id"], "reason": "stage14"},
    )
    return observed["point_id"], promoted["result"]["result"]["event_id"]


def _live_graph():
    api = SkillApi.open_memory()
    point_id, left = _promote(api, "agent-a", "same text")
    opened = api.invoke(
        "agent-a",
        "signal",
        {"name": "open_thread", "event_id": left, "topic": "same text"},
    )
    thread_id = opened["result"]["result"]["thread_id"]
    _, right = _promote(api, "agent-a", "same text")
    contradicted = api.invoke(
        "agent-a",
        "signal",
        {
            "name": "contradict",
            "left_event": left,
            "right_event": right,
            "evidence": "both kept",
        },
    )
    relation_id = contradicted["result"]["result"]["relation_id"]
    graph = api.invoke("agent-a", "read_graph", {})["result"]
    return api, graph, point_id, left, right, thread_id, relation_id


def test_renderer_does_not_import_store():
    source = Path("src/memory_infra/explorer.py").read_text()
    tree = ast.parse(source)
    imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    rendered = " ".join(ast.dump(node) for node in imports)
    assert "store" not in rendered


def test_all_kinds_repeated_events_and_contradiction_are_represented():
    api, graph, point_id, left, right, thread_id, relation_id = _live_graph()
    before = api.invoke("agent-a", "read_graph", {})["result"]
    page = render_explorer(graph)
    after = api.invoke("agent-a", "read_graph", {})["result"]
    assert after == before == graph
    assert "READ-ONLY" in page
    for kind in NODE_KINDS:
        assert f'data-kind="{kind}"' in page
    assert f'data-id="{point_id}"' in page
    assert f'data-id="{left}"' in page
    assert f'data-id="{right}"' in page
    assert left != right
    assert page.count("same text") >= 2
    assert f'data-id="{thread_id}"' in page
    assert 'data-relation-type="evidential.contradicts"' in page
    assert "both kept" in page
    assert relation_id in page
    assert "evidential.contradicts" in page


def test_projection_edges_of_every_kind_render_with_endpoints():
    nodes = [
        {"kind": "point", "id": "p1", "evidence_ref": "ev-p", "content": "point"},
        {"kind": "event", "id": "e1", "evidence_ref": "ev-1", "observation": "same text"},
        {"kind": "event", "id": "e2", "evidence_ref": "ev-2", "observation": "same text"},
        {"kind": "thread", "id": "t1", "member_event_ids": ["e1", "e2"]},
        {"kind": "state", "id": "e1", "contradiction_history": ["r-con"]},
    ]
    edges = [
        {
            "relation_id": f"r-{index}",
            "source_id": "e1",
            "target_id": "e2",
            "relation_type": kind,
            "evidence_ref": f"evidence-{kind}",
        }
        for index, kind in enumerate(EDGE_KINDS)
    ]
    page = render_explorer(
        {"read_only": True, "owner": "mechanism", "nodes": nodes, "edges": edges}
    )
    for kind in EDGE_KINDS:
        assert f'data-relation-type="{kind}"' in page
        assert f"evidence-{kind}" in page
    assert page.count('data-shape="rectangle"') == 2
    assert 'data-shape="circle"' in page
    assert 'data-shape="rectangle"' in page
    assert 'data-shape="rounded-rectangle"' in page
    assert 'data-shape="diamond"' in page


def test_render_is_deterministic_and_does_not_mutate_input():
    _, graph, *_ = _live_graph()
    snapshot = repr(graph)
    first = render_explorer(graph)
    second = render_explorer(graph)
    assert first == second
    assert repr(graph) == snapshot


def test_caller_isolation_notes_are_not_rendered():
    api = SkillApi.open_memory()
    api.invoke("agent-a", "observe", {"content": "shared", "note": "a-note"})
    api.invoke("agent-b", "observe", {"content": "shared-b", "note": "b-note"})
    left = render_explorer(api.invoke("agent-a", "read_graph", {})["result"])
    right = render_explorer(api.invoke("agent-b", "read_graph", {})["result"])
    assert left == right
    assert "a-note" not in left and "b-note" not in right
    with pytest.raises(SnapshotError, match="caller cannot own mechanism fields"):
        api.invoke("agent-a", "read_graph", {"nodes": []})


def test_same_id_different_kind_nodes_stay_separately_addressable():
    nodes = [
        {"kind": "event", "id": "ev-7-2", "observation": "left event"},
        {"kind": "state", "id": "ev-7-2", "contradiction_history": ["rel-7-6"]},
        {"kind": "thread", "id": "th-7-3", "member_event_ids": ["ev-7-2"]},
        {"kind": "state", "id": "th-7-3", "contradiction_history": []},
        {"kind": "event", "id": "ev-7-5", "observation": "right event"},
        {"kind": "state", "id": "ev-7-5", "contradiction_history": ["rel-7-6"]},
    ]
    edges = [
        {
            "relation_id": "rel-7-6",
            "source_id": "ev-7-2",
            "target_id": "ev-7-5",
            "relation_type": "evidential.contradicts",
            "evidence_ref": "both kept",
        }
    ]
    page = render_explorer(
        {"read_only": True, "owner": "mechanism", "nodes": nodes, "edges": edges}
    )
    anchors = [
        presentation_key(row["kind"], row["id"])
        for row in nodes
    ]
    assert len(anchors) == len(set(anchors))
    for anchor in anchors:
        assert page.count(f'id="inspect-{anchor}"') == 1
        assert page.count(f'href="#inspect-{anchor}"') == 1
        assert page.count(f'data-anchor="{anchor}"') == 2
    assert page.count('data-id="ev-7-2"') == 4
    assert 'data-id="ev-7-2"' in page
    assert "ev-7-2" in page
    event_pos = page.index('data-anchor="' + presentation_key("event", "ev-7-2"))
    state_pos = page.index('data-anchor="' + presentation_key("state", "ev-7-2"))
    assert event_pos != state_pos
    assert 'x="252"' in page
    assert "680,50" in page


def test_view_filters_and_search_are_client_side_and_do_not_mutate():
    nodes = [
        {"kind": "event", "id": "ev-7-2", "observation": "left event"},
        {"kind": "state", "id": "ev-7-2", "contradiction_history": ["rel-7-6"]},
        {"kind": "thread", "id": "th-7-3", "member_event_ids": ["ev-7-2"]},
        {"kind": "event", "id": "ev-7-5", "observation": "right event"},
        {"kind": "point", "id": "pt-7-1", "content": "same text"},
    ]
    edges = [
        {
            "relation_id": "rel-7-6",
            "source_id": "ev-7-2",
            "target_id": "ev-7-5",
            "relation_type": "evidential.contradicts",
            "evidence_ref": "both kept",
        }
    ]
    graph = {"read_only": True, "owner": "mechanism", "nodes": nodes, "edges": edges}
    snapshot = repr(graph)
    page = render_explorer(graph)
    assert repr(graph) == snapshot
    assert 'name="view" value="all"' in page
    assert 'name="view" value="thread"' in page
    assert 'name="view" value="event"' in page
    assert 'name="view" value="contradiction"' in page
    assert 'name="q"' in page
    assert "function apply()" in page
    assert "addEventListener" in page
    assert "classList.toggle('is-hidden'" in page
    assert "localStorage" not in page
    assert "fetch(" not in page
    assert "XMLHttpRequest" not in page
    assert page.count('data-contradiction-endpoint="true"') >= 4
    assert 'data-contradiction="true"' in page
    assert "both kept" in page
    assert page.count('data-id="ev-7-2"') >= 2
    assert page.count('data-id="ev-7-5"') >= 2
    assert 'data-kind="thread"' in page
    assert 'data-kind="event"' in page
