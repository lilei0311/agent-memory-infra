"""Stage 10 Skill bootstrap and existing-memory discovery.

Installation inspects a caller-supplied environment and returns a bounded
inventory. It does not import, rewrite, or ingest caller memory into
mechanism-owned state. Discovery metadata stays on this seam.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

DEFAULT_SCAN_LIMIT = 32
DEFAULT_MAX_DEPTH = 2
RECOGNIZED_NAMES = frozenset({"MEMORY.md", "memory.md", "memories.json", "memory.json"})

__all__ = [
    "DEFAULT_MAX_DEPTH",
    "DEFAULT_SCAN_LIMIT",
    "RECOGNIZED_NAMES",
    "SkillBootstrap",
    "discover_environment",
]


def _kind_for(name: str) -> str:
    if name in RECOGNIZED_NAMES:
        if name.endswith(".json"):
            return "json_memory"
        return "markdown_memory"
    return "unknown"


def _entry(rel: str, kind: str, status: str, size: int | None, detail: str) -> dict:
    return {
        "path": rel,
        "kind": kind,
        "status": status,
        "bytes": size,
        "detail": detail,
    }


def _scan_root(root: Path, *, scan_limit: int, max_depth: int) -> tuple[list[dict], bool]:
    root = root.resolve()
    found: list[tuple[str, Path]] = []
    unreadable_dirs: list[str] = []
    if not root.exists():
        return ([_entry(".", "unknown", "unreadable", None, "root missing")], False)
    if not root.is_dir():
        return ([_entry(".", "unknown", "unreadable", None, "root is not a directory")], False)
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        try:
            rel_dir = current.relative_to(root)
        except ValueError:
            continue
        depth = 0 if rel_dir == Path(".") else len(rel_dir.parts)
        if depth > max_depth:
            dirnames[:] = []
            continue
        dirnames.sort()
        filenames.sort()
        try:
            names = list(filenames)
        except OSError as exc:
            unreadable_dirs.append(str(rel_dir))
            dirnames[:] = []
            found.append((str(rel_dir), current))
            continue
        for name in names:
            path = current / name
            rel = path.relative_to(root).as_posix()
            found.append((rel, path))
    found.sort(key=lambda item: item[0])
    truncated = len(found) > scan_limit
    selected = found[:scan_limit]
    entries: list[dict] = []
    for rel, path in selected:
        if rel in unreadable_dirs:
            entries.append(_entry(rel, "unknown", "unreadable", None, "directory unreadable"))
            continue
        try:
            if path.is_dir():
                continue
            size = path.stat().st_size
            with path.open("rb") as handle:
                handle.read(1)
        except OSError as exc:
            entries.append(_entry(rel, "unknown", "unreadable", None, type(exc).__name__))
            continue
        name = path.name
        kind = _kind_for(name)
        if kind == "unknown":
            entries.append(_entry(rel, "unknown", "unknown", size, "unrecognized source"))
        else:
            entries.append(_entry(rel, kind, "recognized", size, "recognized filename; not imported"))
    return entries, truncated


def _scan_artifacts(artifacts: Mapping[str, bytes | None], *, scan_limit: int) -> tuple[list[dict], bool]:
    keys = sorted(artifacts)
    truncated = len(keys) > scan_limit
    entries: list[dict] = []
    for key in keys[:scan_limit]:
        payload = artifacts[key]
        name = Path(key).name
        if payload is None:
            entries.append(_entry(key, "unknown", "unreadable", None, "unreadable artifact"))
            continue
        kind = _kind_for(name)
        if kind == "unknown":
            entries.append(_entry(key, "unknown", "unknown", len(payload), "unrecognized source"))
        else:
            entries.append(_entry(key, kind, "recognized", len(payload), "recognized filename; not imported"))
    return entries, truncated


def discover_environment(
    *,
    caller_id: str,
    root: str | Path | None = None,
    artifacts: Mapping[str, bytes | None] | None = None,
    scan_limit: int = DEFAULT_SCAN_LIMIT,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> dict:
    """Read-only bounded inventory. Does not create mechanism memory."""
    if not caller_id or not str(caller_id).strip():
        raise ValueError("caller_id is required")
    if scan_limit < 1:
        raise ValueError("scan_limit must be positive")
    if root is None and artifacts is None:
        entries: list[dict] = []
        truncated = False
        diagnostics = ["empty environment; nothing to scan"]
    else:
        entries = []
        truncated = False
        diagnostics = []
        if root is not None:
            root_entries, root_truncated = _scan_root(Path(root), scan_limit=scan_limit, max_depth=max_depth)
            entries.extend(root_entries)
            truncated = truncated or root_truncated
        if artifacts is not None:
            remaining = max(scan_limit - len(entries), 0)
            art_entries, art_truncated = _scan_artifacts(artifacts, scan_limit=remaining if root is not None else scan_limit)
            if root is not None and len(artifacts) > remaining:
                art_truncated = True
            entries.extend(art_entries)
            truncated = truncated or art_truncated
        if not entries:
            diagnostics.append("no files within scan bounds")
    recognized = sum(1 for item in entries if item["status"] == "recognized")
    unknown = sum(1 for item in entries if item["status"] == "unknown")
    unreadable = sum(1 for item in entries if item["status"] == "unreadable")
    if truncated:
        diagnostics.append("scan truncated at bound")
    if unreadable:
        diagnostics.append("partial discovery: unreadable sources skipped")
    return {
        "ok": True,
        "op": "bootstrap",
        "read_only": True,
        "imported": False,
        "explicit_import": "not_invoked",
        "mechanism_memory_created": False,
        "caller_id": caller_id,
        "sources": entries,
        "inventory": {
            "recognized": recognized,
            "unknown": unknown,
            "unreadable": unreadable,
            "scanned": len(entries),
            "truncated": truncated,
            "scan_limit": scan_limit,
            "max_depth": max_depth,
        },
        "diagnostics": diagnostics,
        "supported_sources": sorted(RECOGNIZED_NAMES),
    }


class SkillBootstrap:
    """Install seam. Holds discovery notes only; not a mechanism store."""

    def __init__(self) -> None:
        self._notes: dict[str, dict] = {}

    def install(
        self,
        caller_id: str,
        *,
        root: str | Path | None = None,
        artifacts: Mapping[str, bytes | None] | None = None,
        scan_limit: int = DEFAULT_SCAN_LIMIT,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        result = discover_environment(
            caller_id=caller_id,
            root=root,
            artifacts=artifacts,
            scan_limit=scan_limit,
            max_depth=max_depth,
        )
        self._notes[caller_id] = result
        return result

    def last_inventory(self, caller_id: str) -> dict | None:
        note = self._notes.get(caller_id)
        if note is None:
            return None
        return note
