"""Focused tests for the complete single-Agent first-run journey with explicit consent/selection and cross-session."""

from pathlib import Path

from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.explorer import render_explorer


def _setup_source(tmp_path: Path, files: dict[str, str] | None = None) -> Path:
    source = tmp_path / "source"
    source.mkdir()
    if files:
        for name, content in files.items():
            (source / name).write_text(content, encoding="utf-8")
    return source


def test_empty_discovery_no_import(tmp_path: Path):
    source = _setup_source(tmp_path, files=None)
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
    source = _setup_source(tmp_path, {"MEMORY.md": "Remember to prefer explicit confirmation before import.\n"})
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


def test_consent_select_subset_and_cross_session(tmp_path: Path):
    files = {
        "MEMORY.md": "Remember to prefer explicit confirmation before import.\n",
        "memory.json": "{\"items\": [{\"text\": \"Secondary json note not selected.\"}]}\n",
    }
    source = _setup_source(tmp_path, files)
    original_memory = (source / "MEMORY.md").read_text(encoding="utf-8")
    original_json = (source / "memory.json").read_text(encoding="utf-8")

    store_path = tmp_path / "store"
    entry1 = SkillEntrypoint(backend="file", path=store_path)
    handle1 = entry1.open("demo-agent")
    discovery = handle1.start(root=source)
    assert discovery["imported"] is False
    recognized = [s["path"] for s in discovery.get("sources", []) if s["status"] == "recognized"]
    assert "MEMORY.md" in recognized
    assert "memory.json" in recognized

    handle1.enable_memory()
    graph_before = handle1.invoke("read_graph", {})["result"]
    nodes_before = len(graph_before.get("nodes", []))
    assert nodes_before == 0

    # Select only MEMORY.md
    selected = ["MEMORY.md"]
    import_report = handle1.import_selected(selected)
    assert len(import_report.get("created", [])) >= 1
    created_paths = [item["path"] for item in import_report.get("created", [])]
    assert "MEMORY.md" in created_paths
    assert "memory.json" not in created_paths

    graph = handle1.invoke("read_graph", {})["result"]
    assert len(graph.get("nodes", [])) > nodes_before
    html = render_explorer(graph)
    assert "read-only" in html.lower()

    # Cross-session via packaging handoff
    handle1.invoke("save", {})
    api = handle1._api
    api2 = api.reopen()
    api2.invoke("demo-agent", "load", {})
    retrieved = api2.invoke("demo-agent", "retrieve", {"query": "explicit confirmation"})["result"]
    assert len(retrieved.get("selected", [])) >= 1

    # Sources unchanged
    assert (source / "MEMORY.md").read_text(encoding="utf-8") == original_memory
    assert (source / "memory.json").read_text(encoding="utf-8") == original_json
