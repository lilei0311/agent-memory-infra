#!/usr/bin/env python3
"""Point discovery at a local directory and import only selected sources.

SQLite (``*.sqlite``, ``*.sqlite3``) and JSONL (``*.jsonl``) are recognized
the same way as Markdown and JSON: ``start`` lists them and does not import.
Pass ``--consent`` to import, and ``--select`` to limit the paths. Redaction
is off unless ``--redact`` is set. Item dedup is off unless ``--dedup`` is set.
Source files are only read.

The default directory is the synthetic fixture set. Those files are invented
notes, not a person's memory, and they contain no secrets. To try a copy that
lives outside this repo, pass ``--root``:

    python3 examples/local_source_import.py \\
        --root "$HOME/.openclaw/agents/<agentId>" \\
        --consent --select agent/openclaw-agent.sqlite

Run that from the repo root after `pip install -e ".[dev]"`.

See docs/LOCAL_SOURCES.md for depth, scan bounds, and a quiescent SQLite copy.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from memory_infra.dedup import ItemDedupPolicy
from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.source_adapter import select_discovered_paths

FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "synthetic"


def _file_bytes(root: Path) -> dict[str, bytes]:
    found: dict[str, bytes] = {}
    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink():
            found[path.relative_to(root).as_posix()] = path.read_bytes()
    return found


def run(
    root: str | Path | None = None,
    *,
    consent: bool = False,
    select: list[str] | None = None,
    redact: bool = False,
    dedup: bool = False,
    max_depth: int = 2,
    scan_limit: int = 32,
) -> dict:
    target = Path(root) if root is not None else FIXTURES
    before = _file_bytes(target)
    entry = SkillEntrypoint(
        backend="memory",
        redact=redact,
        item_dedup=ItemDedupPolicy("skip") if dedup else None,
    )
    handle = entry.open("local-agent")
    discovery = handle.start(root=target, max_depth=max_depth, scan_limit=scan_limit)
    recognized = [item["path"] for item in discovery["sources"] if item["status"] == "recognized"]
    report = None
    if consent:
        chosen = recognized if select is None else select_discovered_paths(select, recognized)
        if chosen:
            report = handle.import_selected(chosen)
    after = _file_bytes(target)
    if after != before:
        raise RuntimeError("source files must not be rewritten")
    return {"discovery": discovery, "recognized": recognized, "import_report": report}


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover a local directory and optionally import selected sources")
    parser.add_argument("--root", type=Path, default=None, help="Directory to scan (default: synthetic fixtures)")
    parser.add_argument("--consent", action="store_true", help="Import after discovery (default: decline)")
    parser.add_argument("--select", nargs="*", default=None, help="Recognized paths to import")
    parser.add_argument("--redact", action="store_true", help="Opt in to redaction (off by default)")
    parser.add_argument("--dedup", action="store_true", help="Opt in to near-duplicate skip")
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--scan-limit", type=int, default=32)
    args = parser.parse_args()
    result = run(
        args.root,
        consent=args.consent,
        select=args.select,
        redact=args.redact,
        dedup=args.dedup,
        max_depth=args.max_depth,
        scan_limit=args.scan_limit,
    )
    print(f"recognized: {result['recognized']}")
    report = result["import_report"]
    if report is None:
        print("import skipped (no explicit consent, or nothing selected)")
    else:
        print(f"created: {len(report['created'])}")
        print(f"skipped: {len(report['skipped'])}")
        print(f"redaction_enabled: {report['redaction']['enabled']}")
        print(f"item_dedup_enabled: {report['item_dedup']['enabled']}")
    print("sources unchanged")


if __name__ == "__main__":
    main()
