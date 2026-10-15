#!/usr/bin/env python3
"""Import the synthetic fixtures with opt-in item dedup.

The fixtures under tests/fixtures/synthetic are invented notes. They are not
a user's memory and contain no secrets. Source files are only read.

After `pip install -e ".[dev]"` from the repo root: python3 examples/dedup_import.py
"""

from __future__ import annotations

from pathlib import Path

from memory_infra.dedup import ItemDedupPolicy
from memory_infra.entrypoint import SkillEntrypoint

FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "synthetic"


def run(mode: str = "skip") -> dict:
    before = {path.name: path.read_bytes() for path in FIXTURES.iterdir() if path.is_file()}
    entry = SkillEntrypoint(backend="memory", item_dedup=ItemDedupPolicy(mode=mode))
    handle = entry.open("fixture-agent")
    handle.start(root=FIXTURES)
    report = handle.import_selected(["MEMORY.md", "memories.json"])
    after = {path.name: path.read_bytes() for path in FIXTURES.iterdir() if path.is_file()}
    if after != before:
        raise RuntimeError("synthetic fixtures must not be rewritten")
    return report


def main() -> None:
    report = run("skip")
    print(f"item_dedup: {report['item_dedup']}")
    print(f"created: {len(report['created'])}")
    print(f"skipped: {len(report['skipped'])}")
    print(f"redaction_enabled: {report['redaction']['enabled']}")
    print("sources unchanged")


if __name__ == "__main__":
    main()
