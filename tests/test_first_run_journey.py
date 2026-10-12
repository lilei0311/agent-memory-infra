"""Focused tests for the complete single-Agent first-run journey with explicit consent."""

from pathlib import Path

from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.explorer import render_explorer


def _setup_source(tmp_path: Path, content: str | None = "Remember to prefer explicit confirmation before import.\n") -> Path:
    source = tmp_path / "source"
    source.mkdir()
    if content is not None:
        (source / "MEMORY.md").write_text(content, encoding="utf-8")
    return source


def test_empty_discovery_no_import(tmp_path: Path):
    source = _setup_source(tmp_path, content=None)
    entry = SkillEntrypoint(backend="memory")
    handle = entry.open("demo-agent")
    discovery = handle.start(root=source)
    assert discovery["imported"] is False
    recognized = [s["path"] for s in discovery.get("sources", []) if s["status"] == "recognized"]
    assert recognized == []
    handle.enable_memory()
    graph = handle.invoke("read_graph", {})["result"]
    assert len(graph.get("nodes", [])) == 0


def test_decline_import_leaves_state_unchanged(tmp_path: Path):
    source = _setup_source(tmp_path)
    original = (source / "MEMORY.md").read_text(encoding="utf-8")
    entry = SkillEntrypoint(backend="memory")
    handle = entry.open("demo-agent")
    discovery = handle.start(root=source)
    assert discovery["imported"] is False
    recognized = [s["path"] for s in discovery.get("sources", []) if s["status"] == "recognized"]
    assert "MEMORY.md" in recognized

    handle.enable_memory()
    graph_before = handle.invoke("read_graph", {})["result"]
    nodes_before = len(graph_before.get("nodes", []))
    assert nodes_before == 0

    # Explicit decline: do not call import_selected
    graph_after = handle.invoke("read_graph", {})["result"]
    assert len(graph_after.get("nodes", [])) == nodes_before
    assert (source / "MEMORY.md").read_text(encoding="utf-8") == original


def test_consent_import_then_retrieval(tmp_path: Path):
    source = _setup_source(tmp_path)
    original = (source / "MEMORY.md").read_text(encoding="utf-8")
    entry = SkillEntrypoint(backend="memory")
    handle = entry.open("demo-agent")
    discovery = handle.start(root=source)
    assert discovery["imported"] is False
    recognized = [s["path"] for s in discovery.get("sources", []) if s["status"] == "recognized"]
    assert "MEMORY.md" in recognized

    handle.enable_memory()
    graph_before = handle.invoke("read_graph", {})["result"]
    nodes_before = len(graph_before.get("nodes", []))
    assert nodes_before == 0

    import_report = handle.import_selected(recognized)
    assert len(import_report.get("created", [])) >= 1

    graph = handle.invoke("read_graph", {})["result"]
    assert len(graph.get("nodes", [])) > nodes_before
    html = render_explorer(graph)
    assert "read-only" in html.lower()

    retrieved = handle.invoke("retrieve", {"query": "explicit confirmation"})["result"]
    assert len(retrieved.get("selected", [])) >= 1

    assert (source / "MEMORY.md").read_text(encoding="utf-8") == original
