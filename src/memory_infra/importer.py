"""Stage 12 explicit historical-memory structuring/import.

Discovery stays read-only. This module parses already-recognized source
payloads and records caller-selected items through the public Skill API.
It does not import memory_infra.store and does not rewrite caller files.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

RECOGNIZED_NAMES = frozenset({"MEMORY.md", "memory.md", "memories.json", "memory.json"})
DUPLICATE_POLICY = "idempotent_by_source_digest"

__all__ = ["DUPLICATE_POLICY", "RECOGNIZED_NAMES", "parse_recognized", "snapshot_digest", "source_ref_for"]


def source_ref_for(path: str) -> str:
    return f"import:{path}"


def snapshot_digest(payload: bytes) -> str:
    """SHA-256 of the selected source snapshot bytes."""

    return hashlib.sha256(payload).hexdigest()


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_recognized(name: str, payload: bytes) -> tuple[list[dict], str | None]:
    """Parse one recognized payload. Returns items or a rejection reason.

    Items are caller text plus a content digest. Mechanism ids are not assigned here.
    """

    if Path(name).name not in RECOGNIZED_NAMES:
        return [], "unknown"
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        return [], "unreadable"
    if name.endswith(".json"):
        return _parse_json(text)
    return _parse_markdown(text), None


def _parse_markdown(text: str) -> list[dict]:
    items: list[dict] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("- ", "* ")):
            line = line[2:].strip()
        if not line:
            continue
        items.append({"text": line, "digest": _digest(line)})
    return items


def _parse_json(text: str) -> tuple[list[dict], str | None]:
    try:
        body = json.loads(text)
    except json.JSONDecodeError:
        return [], "unreadable"
    rows = _json_rows(body)
    if rows is None:
        return [], "unreadable"
    items: list[dict] = []
    for row in rows:
        if not isinstance(row, str) or not row.strip():
            return [], "unreadable"
        value = row.strip()
        items.append({"text": value, "digest": _digest(value)})
    return items, None


def _json_rows(body: object) -> list | None:
    if isinstance(body, list):
        return body
    if isinstance(body, str):
        return [body]
    if isinstance(body, dict):
        if "memories" in body:
            rows = body["memories"]
        elif "items" in body:
            rows = body["items"]
        elif "text" in body:
            rows = [body["text"]]
        elif "content" in body:
            rows = [body["content"]]
        else:
            return None
        if isinstance(rows, str):
            return [rows]
        if not isinstance(rows, list):
            return None
        extracted: list = []
        for row in rows:
            if isinstance(row, str):
                extracted.append(row)
            elif isinstance(row, dict) and isinstance(row.get("text"), str):
                extracted.append(row["text"])
            elif isinstance(row, dict) and isinstance(row.get("content"), str):
                extracted.append(row["content"])
            else:
                return None
        return extracted
    return None
