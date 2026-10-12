#!/usr/bin/env python3
"""Minimal CLI-free first-run journey for the single-Agent Memory Skill.

Demonstrates discovery-first startup, explicit consent for import,
read-only graph, and representative retrieval. No new infrastructure.
Run with: PYTHONPATH=src python examples/first_run_journey.py [--consent]
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.explorer import render_explorer


def run_journey(consent: bool = False) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "source"
        source.mkdir()
        memory_path = source / "MEMORY.md"
        memory_path.write_text(
            "Remember to prefer explicit confirmation before import.\n", encoding="utf-8"
        )
        original_source = memory_path.read_text(encoding="utf-8")

        entry = SkillEntrypoint(backend="memory")
        handle = entry.open("demo-agent")
        discovery = handle.start(root=source)
        print("Discovery phase:")
        print(f"  imported: {discovery['imported']}")
        recognized = [s["path"] for s in discovery.get("sources", []) if s["status"] == "recognized"]
        print(f"  recognized sources: {recognized}")

        handle.enable_memory()
        graph_before = handle.invoke("read_graph", {})["result"]
        nodes_before = len(graph_before.get("nodes", []))
        print(f"Graph nodes before import decision: {nodes_before}")

        if consent and recognized:
            import_report = handle.import_selected(recognized)
            print(f"Explicit import created: {len(import_report.get('created', []))}")
        else:
            print("Import skipped (no explicit consent or no sources).")

        graph = handle.invoke("read_graph", {})["result"]
        nodes_after = len(graph.get("nodes", []))
        html = render_explorer(graph)
        print(f"Graph nodes after: {nodes_after}")
        print(f"Explorer contains read-only marker: {'read-only' in html.lower()}")
        if not consent:
            print(f"Graph unchanged on decline: {nodes_after == nodes_before}")

        if consent:
            retrieved = handle.invoke("retrieve", {"query": "explicit confirmation"})["result"]
            print(f"Retrieval selected: {len(retrieved.get('selected', []))}")
        else:
            print("Retrieval skipped (no import).")

        print("Source file unchanged:", memory_path.read_text(encoding="utf-8") == original_source)
        print("Complete first-run journey demonstrated.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Single-Agent Skill first-run journey")
    parser.add_argument("--consent", action="store_true", help="Explicitly consent to import recognized sources")
    args = parser.parse_args()
    run_journey(consent=args.consent)


if __name__ == "__main__":
    main()
