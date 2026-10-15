"""Internal source adapters for explicit historical import.

Markdown and JSON adapters implement the internal SourceAdapter protocol.
They are not public. Callers never import this module.
Mechanism IDs and state remain owned by the Skill API.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
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


DEFAULT_MARKDOWN_NAMES = frozenset({"MEMORY.md", "memory.md"})
EXTENDED_MARKDOWN_NAMES = frozenset(
    {"AGENTS.md", "SOUL.md", "USER.md", "IDENTITY.md", "TOOLS.md", "HEARTBEAT.md", "CLAUDE.md"}
)
JSON_NAMES = frozenset({"memories.json", "memory.json"})

_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_BULLET = re.compile(r"^(?:[-*+]|\d{1,3}[.)])\s+(.*)$")
_CHECKBOX = re.compile(r"^\[[ xX]\]\s+")
_FENCE = re.compile(r"^(```|~~~)")
_ISO_DATE = re.compile(r"(?<![0-9])(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])(?![0-9])")
_FM_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$")
_FM_META_KEYS = ("name", "type", "description")


def _scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def split_frontmatter(text: str) -> tuple[dict, str, bool]:
    """Split a leading ``---`` YAML-subset block from the body.

    Supports ``key: value``, inline ``[a, b]`` lists and ``- item`` block lists.
    An unterminated block is not frontmatter: returns ({}, text, False).
    """

    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text, False
    end = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() in {"---", "..."}:
            end = idx
            break
    if end is None:
        return {}, text, False
    meta: dict = {}
    current: str | None = None
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        stripped = raw.strip()
        if stripped.startswith("- ") and current is not None and raw[:1] in " \t-":
            bucket = meta.setdefault(current, [])
            if isinstance(bucket, list):
                bucket.append(_scalar(stripped[2:]))
            continue
        match = _FM_KEY.match(raw)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        current = key
        if value == "":
            meta[key] = []
        elif value.startswith("[") and value.endswith("]"):
            meta[key] = [_scalar(v) for v in value[1:-1].split(",") if v.strip()]
        else:
            meta[key] = _scalar(value)
    meta = {k: (v if v != [] else "") for k, v in meta.items()}
    return meta, "\n".join(lines[end + 1 :]), True


class MarkdownV2SourceAdapter:
    """Markdown adapter v2: frontmatter, heading context, dates, configurable names.

    Compared with v1: a leading YAML frontmatter block is parsed as metadata
    (not as observations); every item carries its heading path (``section``)
    and the first ISO date on the line (``date``); fenced code blocks, HTML
    comments and horizontal rules are skipped; numbered lists and task
    checkboxes are unwrapped. Items keep ``text`` and ``digest`` (digest is of
    the text only, so sections/dates never change identity). Distinct
    occurrences are preserved. No mechanism IDs, no file writes.
    """

    def __init__(self, names: frozenset[str] | set[str] | None = None) -> None:
        self.names = frozenset(names) if names is not None else DEFAULT_MARKDOWN_NAMES | EXTENDED_MARKDOWN_NAMES

    def can_handle(self, path: str) -> bool:
        return Path(path).name in self.names

    def parse(self, payload: bytes) -> tuple[list[dict], str | None]:
        items, _meta, error = self.parse_document(payload)
        return items, error

    def parse_document(self, payload: bytes) -> tuple[list[dict], dict, str | None]:
        try:
            text = payload.decode("utf-8-sig")
        except UnicodeDecodeError:
            return [], {}, "unreadable"
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        meta, body, _has = split_frontmatter(text)
        doc_meta = {k: meta[k] for k in _FM_META_KEYS if isinstance(meta.get(k), str) and meta.get(k)}
        stack: list[tuple[int, str]] = []
        items: list[dict] = []
        in_fence = False
        in_comment = False
        for raw in body.split("\n"):
            line = raw.strip()
            if in_comment:
                if "-->" in line:
                    in_comment = False
                continue
            if line.startswith("<!--"):
                if "-->" not in line:
                    in_comment = True
                continue
            if _FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence or not line:
                continue
            if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", line):
                continue
            heading = _HEADING.match(line)
            if heading:
                level = len(heading.group(1))
                while stack and stack[-1][0] >= level:
                    stack.pop()
                if heading.group(2):
                    stack.append((level, heading.group(2)))
                continue
            bullet = _BULLET.match(line)
            if bullet:
                line = bullet.group(1).strip()
            line = _CHECKBOX.sub("", line).strip()
            if not line:
                continue
            item: dict = {"text": line, "digest": _digest(line)}
            if stack:
                item["section"] = " > ".join(title for _lvl, title in stack)
            date = _ISO_DATE.search(line)
            if date:
                item["date"] = date.group(0)
            if doc_meta:
                item["doc_meta"] = dict(doc_meta)
            items.append(item)
        return items, meta, None


@dataclass(frozen=True)
class SourceConfig:
    """Which file names are recognized and which Markdown adapter parses them.

    Default keeps the original behavior (v1 adapter, four recognized names).
    ``SourceConfig.extended()`` enables the v2 adapter and the persona/memory
    names AGENTS.md, SOUL.md, USER.md, IDENTITY.md, TOOLS.md, HEARTBEAT.md and
    CLAUDE.md. Names are matched on the file's base name.
    """

    markdown_names: frozenset[str] = DEFAULT_MARKDOWN_NAMES
    json_names: frozenset[str] = JSON_NAMES
    markdown_v2: bool = False

    @property
    def recognized_names(self) -> frozenset[str]:
        return frozenset(self.markdown_names) | frozenset(self.json_names)

    @classmethod
    def extended(cls, extra_markdown_names: frozenset[str] | set[str] = frozenset()) -> "SourceConfig":
        return cls(
            markdown_names=DEFAULT_MARKDOWN_NAMES | EXTENDED_MARKDOWN_NAMES | frozenset(extra_markdown_names),
            markdown_v2=True,
        )

    def markdown_adapter(self) -> SourceAdapter:
        if self.markdown_v2:
            return MarkdownV2SourceAdapter(self.markdown_names)
        return MarkdownSourceAdapter()


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
