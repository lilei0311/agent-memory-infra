"""Stage 12 explicit historical-memory structuring/import.

Discovery stays read-only. This module parses already-recognized source
payloads and records caller-selected items through the public Skill API.
It does not import memory_infra.store and does not rewrite caller files.
Markdown and JSON parsing are delegated to internal SourceAdapters.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from memory_infra.source_adapter import JSON_ADAPTER, MARKDOWN_ADAPTER

RECOGNIZED_NAMES = frozenset({"MEMORY.md", "memory.md", "memories.json", "memory.json"})
DUPLICATE_POLICY = "idempotent_by_source_digest"

__all__ = ["DUPLICATE_POLICY", "RECOGNIZED_NAMES", "parse_recognized", "snapshot_digest", "source_ref_for"]


def source_ref_for(path: str) -> str:
    return f"import:{path}"


def snapshot_digest(payload: bytes) -> str:
    """SHA-256 of the selected source snapshot bytes."""

    return hashlib.sha256(payload).hexdigest()


def parse_recognized(name: str, payload: bytes) -> tuple[list[dict], str | None]:
    """Parse one recognized payload. Returns items or a rejection reason.

    Items are caller text plus a content digest. Mechanism ids are not assigned here.
    Markdown and JSON sources are routed through their SourceAdapters.
    """

    if Path(name).name not in RECOGNIZED_NAMES:
        return [], "unknown"
    if MARKDOWN_ADAPTER.can_handle(name):
        return MARKDOWN_ADAPTER.parse(payload)
    if JSON_ADAPTER.can_handle(name):
        return JSON_ADAPTER.parse(payload)
    return [], "unknown"
