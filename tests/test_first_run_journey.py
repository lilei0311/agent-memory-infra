"""Focused test for the complete single-Agent first-run journey."""

from pathlib import Path

from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.explorer import render_explorer


def test_complete_first_run_journey(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "MEMORY.md").write_text(
        "Remember to prefer explicit confirmation before import.\n", encoding="utf-8"
    )
    entry = SkillEntrypoint(backend="memory")
    handle = entry.open("demo-agent")
    discovery = handle.start(root=source)
    assert discovery["imported"] is False
    recognized = [
        s["path"] for s in discovery.get("sources", []) if s["status"] == "recognized"
    ]
    assert "MEMORY.md" in recognized

    import_report = handle.import_selected(recognized)
    assert len(import_report.get("created", [])) >= 1
    graph = handle.invoke("read_graph", {})["result"]
    assert len(graph.get("nodes", [])) >= 1
    html = render_explorer(graph)
    assert "read-only" in html.lower()

    # Representative retrieval after import (simulated subsequent invocation)
    retrieved = handle.invoke("retrieve", {"query": "explicit confirmation"})["result"]
    assert len(retrieved.get("selected", [])) >= 1

    # Source unchanged
    assert (source / "MEMORY.md").read_text(encoding="utf-8").startswith("Remember")
