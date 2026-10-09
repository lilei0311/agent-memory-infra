"""Internal source adapters for explicit historical import.

The Markdown adapter is the first bounded source adapter. It is not public.
Callers never import this module. Mechanism IDs and state remain owned by the Skill API.
"""

from __future__ import annotations

import hashlib
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


MARKDOWN_ADAPTER: SourceAdapter = MarkdownSourceAdapter()
