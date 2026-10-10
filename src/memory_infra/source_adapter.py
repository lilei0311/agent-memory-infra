"""Internal source adapters for explicit historical import.

Markdown and JSON adapters implement the internal SourceAdapter protocol.
They are not public. Callers never import this module.
Mechanism IDs and state remain owned by the Skill API.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Protocol


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SourceAdapter(Protocol):
    """Smallest internal protocol for a recognized memory source."""

    def can_handle(self, path: str) -> bool: ...

    def parse(self, payload: bytes) -> tuple[list[dict], str | None]: ...


class MarkdownSourceAdapter:
    """Recognizes and parses Markdown memory files (MEMORY.md / memory.md).

    Returns text items with content digests. Does not assign mechanism IDs
    or write caller files.
    """

    def can_handle(self, path: str) -> bool:
        return Path(path).name in {"MEMORY.md", "memory.md"}

    def parse(self, payload: bytes) -> tuple[list[dict], str | None]:
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError:
            return [], "unreadable"
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
        return items, None


class JsonSourceAdapter:
    """Recognizes and parses JSON memory files (memories.json / memory.json).

    Supports the existing shapes: top-level list/string/object with keys
    memories/items/text/content; rows as strings or objects with string
    text/content. Returns text items with content digests. Does not assign
    mechanism IDs or write caller files.
    """

    def can_handle(self, path: str) -> bool:
        return Path(path).name in {"memories.json", "memory.json"}

    def parse(self, payload: bytes) -> tuple[list[dict], str | None]:
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError:
            return [], "unreadable"
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


MARKDOWN_ADAPTER: SourceAdapter = MarkdownSourceAdapter()
JSON_ADAPTER: SourceAdapter = JsonSourceAdapter()
