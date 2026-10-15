#!/usr/bin/env python3
"""Minimal CLI-free first-run journey for the single-Agent Memory Skill.

Demonstrates discovery-first startup, explicit consent/selection for import,
read-only graph, cross-session retrieval via file backend, and source immutability.
No new infrastructure.
Run with: PYTHONPATH=src python examples/first_run_journey.py [--consent] [--select PATH ...] [--redact]
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.explorer import render_explorer


def run_journey(consent: bool = False, select: list[str] | None = None, redact: bool = False) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "source"
        source.mkdir()
        (source / "MEMORY.md").write_text(
            "Remember to prefer explicit confirmation before import.\n", encoding="utf-8"
        )
        (source / "memory.json").write_text(
            "{\"memories\": [{\"content\": \"Secondary json note.\"}]}\n", encoding="utf-8"
        )
        original_memory = (source / "MEMORY.md").read_text(encoding="utf-8")
        original_json = (source / "memory.json").read_text(encoding="utf-8")

        store_path = tmp_path / "memory_store"

        # First session
        entry1 = SkillEntrypoint(backend="file", path=store_path, redact=redact)
        handle1 = entry1.open("demo-agent")
        discovery = handle1.start(root=source)
        print("Discovery phase (session 1):")
        print(f"  imported: {discovery['imported']}")
        recognized = [s["path"] for s in discovery.get("sources", []) if s["status"] == "recognized"]
        print(f"  recognized sources: {recognized}")

        handle1.enable_memory()
        graph_before = handle1.invoke("read_graph", {})["result"]
        nodes_before = len(graph_before.get("nodes", []))
        print(f"Graph nodes before import decision: {nodes_before}")

        to_import = []
        if consent and recognized:
            if select:
                to_import = [p for p in select if p in recognized]
                print(f"Explicit selection for import: {to_import}")
            else:
                to_import = recognized
                print(f"Explicit consent to import all recognized: {to_import}")
            if to_import:
                import_report = handle1.import_selected(to_import)
                print(f"Explicit import created: {len(import_report.get('created', []))}")
            else:
                print("No matching sources selected for import.")
        else:
            print("Import skipped (no explicit consent or no sources).")

        graph = handle1.invoke("read_graph", {})["result"]
        nodes_after = len(graph.get("nodes", []))
        html = render_explorer(graph)
        print(f"Graph nodes after: {nodes_after}")
        print(f"Explorer contains read-only marker: {'read-only' in html.lower()}")
        if not consent:
            print(f"Graph unchanged on decline: {nodes_after == nodes_before}")

        # Cross-session: use supported packaging handoff (SkillApi.reopen) + public load/retrieve
        print("\nSecond session (via SkillApi.reopen packaging handoff):")
        if to_import:
            # Explicit save for file persistence
            handle1.invoke("save", {})
            api = handle1.packaging_seam()  # public packaging handoff
            api2 = api.reopen()
            api2.invoke("demo-agent", "load", {})
            retrieved = api2.invoke("demo-agent", "retrieve", {"query": "explicit confirmation"})["result"]
            print(f"Retrieval in second session selected: {len(retrieved.get('selected', []))}")
        else:
            print("Retrieval skipped in second session (no prior import).")

        print("Source files unchanged:")
        print("  MEMORY.md:", (source / "MEMORY.md").read_text(encoding="utf-8") == original_memory)
        print("  memory.json:", (source / "memory.json").read_text(encoding="utf-8") == original_json)
        print("Complete first-run journey demonstrated (including selection and cross-session).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Single-Agent Skill first-run journey")
    parser.add_argument("--consent", action="store_true", help="Explicitly consent to import (all recognized by default)")
    parser.add_argument("--select", nargs="*", help="Optional list of recognized paths to import (subset)")
    parser.add_argument(
        "--redact",
        action="store_true",
        help="Opt in to secret/PII redaction on import (off by default for local memory)",
    )
    args = parser.parse_args()
    run_journey(consent=args.consent, select=args.select, redact=args.redact)


if __name__ == "__main__":
    main()
