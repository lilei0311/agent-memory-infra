#!/usr/bin/env python3
"""Minimal CLI-free first-run journey for the single-Agent Memory Skill.

Demonstrates discovery-first startup, explicit import, read-only graph,
and representative retrieval. No new infrastructure.
Run with: PYTHONPATH=src python examples/first_run_journey.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.explorer import render_explorer


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "source"
        source.mkdir()
        (source / "MEMORY.md").write_text(
            "Remember to prefer explicit confirmation before import.\n", encoding="utf-8"
        )
        entry = SkillEntrypoint(backend="memory")
        handle = entry.open("demo-agent")
        discovery = handle.start(root=source)
        print("Discovery phase:")
        print(f"  imported: {discovery['imported']}")
        print(f"  recognized sources: {[s['path'] for s in discovery.get('sources', []) if s['status'] == 'recognized']}")

        recognized = [s["path"] for s in discovery.get("sources", []) if s["status"] == "recognized"]
        import_report = handle.import_selected(recognized)
        print(f"Explicit import created: {len(import_report.get('created', []))}")

        graph = handle.invoke("read_graph", {})["result"]
        html = render_explorer(graph)
        print(f"Graph nodes: {len(graph.get('nodes', []))}")
        print(f"Explorer contains read-only marker: {'read-only' in html.lower()}")

        retrieved = handle.invoke("retrieve", {"query": "explicit confirmation"})["result"]
        print(f"Retrieval selected: {len(retrieved.get('selected', []))}")

        print("Source file unchanged:", (source / "MEMORY.md").read_text().startswith("Remember"))
        print("Complete first-run journey demonstrated.")


if __name__ == "__main__":
    main()
