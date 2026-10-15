#!/usr/bin/env python3
"""Scripted agent session through the in-process tools.

Discover → preview → import only with --consent → retrieve → optional signal.
Does not call the Skill API directly. Redaction is off unless --redact is set.
The default root is the synthetic fixtures. Those files are invented notes.

    python3 examples/agent_session.py --select MEMORY.md --consent --signal

The default store is a temporary directory, not your home directory. Pass
``--store ~/.agent-memory-infra/store`` only when you want the personal file
backend. Do not point ``--root`` at real memory if you also pass ``--show-text``.
Without ``--show-text``, a non-fixture root prints counts and omits memory text.

See docs/AGENT_INSTALL.md and src/memory_infra/SKILL.md.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from memory_infra.agent_tools import run_scripted_session

FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "synthetic"


def main() -> None:
    parser = argparse.ArgumentParser(description="Scripted in-process agent memory session")
    parser.add_argument("--root", type=Path, default=None, help="Directory to scan (default: synthetic fixtures)")
    parser.add_argument("--consent", action="store_true", help="Import after preview (default: decline)")
    parser.add_argument("--select", nargs="*", default=None, help="Recognized paths to preview and maybe import")
    parser.add_argument("--query", default="explicit confirmation", help="Retrieval query")
    parser.add_argument("--signal", action="store_true", help="Record a consolidate signal on the first hit")
    parser.add_argument("--redact", action="store_true", help="Opt in to redaction (off by default)")
    parser.add_argument("--store", type=Path, default=None, help="File-backend path (default: a temp directory)")
    parser.add_argument("--caller-id", default="mac-agent", help="Stable caller id for this agent")
    parser.add_argument(
        "--show-text",
        action="store_true",
        help="Print retrieved text. Implied for the synthetic fixtures; omit for a real root",
    )
    args = parser.parse_args()
    root = args.root if args.root is not None else FIXTURES
    show_text = args.show_text or root.resolve() == FIXTURES.resolve()
    temp = None
    store = args.store
    if store is None:
        temp = tempfile.TemporaryDirectory()
        store = Path(temp.name) / "store"
    try:
        summary = run_scripted_session(
            root,
            caller_id=args.caller_id,
            store_path=store,
            select=args.select,
            consent=args.consent,
            query=args.query,
            outcome_signal="consolidate" if args.signal else None,
            redact=args.redact,
        )
    finally:
        if temp is not None:
            temp.cleanup()
    print(f"discover imported: {summary['discovery_imported']}")
    print(f"recognized: {list(summary['recognized'])}")
    print(f"preview dry_run: {summary['preview_dry_run']}")
    print(f"redaction_enabled: {summary['redaction_enabled']}")
    print(f"graph nodes before import: {summary['graph_nodes_before_import']}")
    print(f"import created: {summary['created_count']}")
    print(f"graph nodes after import: {summary['graph_nodes_after_import']}")
    print(f"retrieve selected: {len(summary['memories'])}")
    if show_text:
        for memory in summary["memories"]:
            print(f"memory: {memory['text']}")
    else:
        print("memory text omitted (root is not the synthetic fixtures)")
    if summary["outcome"] is not None:
        print(f"outcome: {summary['outcome']['result'].get('lifecycle_state')}")
    print(f"sources unchanged: {summary['sources_unchanged']}")
    print(f"store saved: {summary['saved'] is not None}")
    if not summary["sources_unchanged"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
