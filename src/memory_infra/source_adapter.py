"""Internal source adapters for explicit historical import.

Markdown, JSON, JSONL, and SQLite adapters implement the internal
SourceAdapter protocol. They are not public. Callers never import this
module. Mechanism IDs and state remain owned by the Skill API.

SQLite parsing deserializes a byte snapshot into a private in-memory
database and runs queries with ``PRAGMA query_only``. It does not open the
caller's path and does not write the source file.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Basename token, not a literal file. Present in a name set only when dated
# Markdown recognition is on. Matches ``2026-04-02.md``, not ``notes-2026-04-02.md``.
DATED_MARKDOWN_TOKEN = "YYYY-MM-DD.md"
_DATED_MARKDOWN_NAME = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])\.md$")


def is_dated_markdown_basename(filename: str) -> bool:
    """True when the basename is exactly ``YYYY-MM-DD.md`` with a calendar-shaped date.

    Month is 01–12 and day is 01–31. The suffix is lowercase ``.md``. A date
    inside a longer name does not match.
    """

    return _DATED_MARKDOWN_NAME.match(Path(filename).name) is not None


def matches_recognized_name(filename: str, names: frozenset[str]) -> bool:
    """True when ``filename`` is an exact recognized name or a ``*.ext`` token.

    If ``names`` contains ``DATED_MARKDOWN_TOKEN``, basenames that pass
    ``is_dated_markdown_basename`` match as well. The token itself is not
    a dated basename.
    """

    base = Path(filename).name
    if base in names:
        return True
    if DATED_MARKDOWN_TOKEN in names and is_dated_markdown_basename(base):
        return True
    lower = base.lower()
    for token in names:
        if token.startswith("*.") and len(token) > 2 and lower.endswith(token[1:].lower()):
            return True
    return False


def kind_for_filename(filename: str, names: frozenset[str]) -> str:
    """Inventory kind for a recognized name, or ``unknown``."""

    if not matches_recognized_name(filename, names):
        return "unknown"
    lower = Path(filename).name.lower()
    if lower.endswith(".jsonl"):
        return "jsonl_memory"
    if lower.endswith(".sqlite") or lower.endswith(".sqlite3"):
        return "sqlite_memory"
    if lower.endswith(".json"):
        return "json_memory"
    return "markdown_memory"


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
SQLITE_GLOBS = frozenset({"*.sqlite", "*.sqlite3"})
JSONL_GLOBS = frozenset({"*.jsonl"})
_CHUNK_TABLE = "memory_index_chunks"
_PROVENANCE_TABLES = ("memory_index_sources", "sources")
_CHUNK_COLUMNS = ("id", "path", "source", "start_line", "end_line", "hash", "text", "updated_at")
_PROVENANCE_COLUMNS = ("path", "source", "hash", "mtime", "size")
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SQLITE_HEADER = b"SQLite format 3\x00"
_JSONL_TEXT_KEYS = ("text", "content", "memory", "summary")
_JSONL_LIST_KEYS = ("memories", "items")
_JSONL_KNOWN_TYPES = frozenset(
    {"message", "custom_message", "compaction", "custom", "reset", "branch_summary"}
)

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
        return matches_recognized_name(path, self.names)

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


def _q(identifier: str) -> str:
    if not _IDENT.fullmatch(identifier):
        raise ValueError("bad identifier")
    return '"' + identifier + '"'


def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [str(row[1]) for row in conn.execute(f"PRAGMA table_info({_q(table)})")]


def _load_provenance(conn: sqlite3.Connection, tables: set[str]) -> dict[tuple[str, str], dict]:
    """Read path/hash rows from the first provenance table that has a path column.

    ``memory_index_sources`` is the OpenClaw table. ``sources`` is accepted as
    the same shape. Rows are not observations.
    """

    found: dict[tuple[str, str], dict] = {}
    for table in _PROVENANCE_TABLES:
        if table not in tables:
            continue
        columns = _table_columns(conn, table)
        if "path" not in columns:
            continue
        wanted = [column for column in _PROVENANCE_COLUMNS if column in columns]
        sql = "SELECT " + ", ".join(_q(column) for column in wanted) + " FROM " + _q(table)
        for row in conn.execute(sql):
            path = row["path"]
            if not isinstance(path, str):
                continue
            source = ""
            if "source" in wanted and isinstance(row["source"], str):
                source = row["source"]
            meta: dict = {"path": path, "table": table}
            if source:
                meta["source"] = source
            if "hash" in wanted and isinstance(row["hash"], str):
                meta["hash"] = row["hash"]
            mtime = row["mtime"] if "mtime" in wanted else None
            if isinstance(mtime, (int, float)) and not isinstance(mtime, bool):
                meta["mtime"] = mtime
            size = row["size"] if "size" in wanted else None
            if isinstance(size, int) and not isinstance(size, bool):
                meta["size"] = size
            found[(path, source)] = meta
        break
    return found


def _parse_sqlite_conn(conn: sqlite3.Connection) -> tuple[list[dict], str | None]:
    tables = {
        str(row[0])
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")
    }
    if _CHUNK_TABLE not in tables:
        return [], "unreadable"
    columns = _table_columns(conn, _CHUNK_TABLE)
    if "text" not in columns:
        return [], "unreadable"
    selected = [column for column in _CHUNK_COLUMNS if column in columns]
    order = [column for column in ("path", "start_line", "id") if column in columns]
    sql = "SELECT " + ", ".join(_q(column) for column in selected) + " FROM " + _q(_CHUNK_TABLE)
    if order:
        sql += " ORDER BY " + ", ".join(_q(column) for column in order)
    provenance = _load_provenance(conn, tables)
    items: list[dict] = []
    for row in conn.execute(sql):
        raw = row["text"]
        if not isinstance(raw, str):
            continue
        value = raw.strip()
        if not value:
            continue
        item: dict = {"text": value, "digest": _digest(value)}
        path = row["path"] if "path" in selected else None
        source = row["source"] if "source" in selected else None
        if isinstance(path, str) and path:
            item["section"] = path
        if isinstance(source, str) and source:
            item["origin"] = source
        if "id" in selected and row["id"] is not None:
            item["chunk_id"] = str(row["id"])
        if "start_line" in selected and isinstance(row["start_line"], int) and not isinstance(row["start_line"], bool):
            item["start_line"] = row["start_line"]
        if "end_line" in selected and isinstance(row["end_line"], int) and not isinstance(row["end_line"], bool):
            item["end_line"] = row["end_line"]
        if isinstance(path, str):
            source_key = source if isinstance(source, str) else ""
            meta = provenance.get((path, source_key))
            if meta is None and source_key:
                meta = provenance.get((path, ""))
            if meta is None and not source_key:
                matches = [
                    candidate
                    for (row_path, _row_source), candidate in provenance.items()
                    if row_path == path
                ]
                if len(matches) == 1:
                    meta = matches[0]
            if meta is not None:
                item["index_source"] = dict(meta)
        items.append(item)
    return items, None


class SqliteMemorySourceAdapter:
    """Read chunk text from an OpenClaw-shaped SQLite memory index.

    Observations are ``memory_index_chunks.text``. ``memory_index_sources``
    (or a ``sources`` table with the same path/hash columns) is attached as
    provenance and is not imported as its own items. Embeddings are not read.
    The payload is a snapshot of the database file. Parsing does not open or
    rewrite that file.
    """

    def can_handle(self, path: str) -> bool:
        return matches_recognized_name(path, SQLITE_GLOBS)

    def parse(self, payload: bytes) -> tuple[list[dict], str | None]:
        if not payload.startswith(_SQLITE_HEADER):
            return [], "unreadable"
        conn = sqlite3.connect(":memory:")
        try:
            conn.deserialize(payload)
            conn.execute("PRAGMA query_only = ON")
            conn.row_factory = sqlite3.Row
            return _parse_sqlite_conn(conn)
        except (sqlite3.Error, ValueError):
            return [], "unreadable"
        finally:
            conn.close()


def _text_blocks(content: object) -> list[str]:
    if isinstance(content, str):
        value = content.strip()
        return [value] if value else []
    if not isinstance(content, list):
        return []
    texts: list[str] = []
    for block in content:
        if isinstance(block, str):
            value = block.strip()
            if value:
                texts.append(value)
            continue
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type not in (None, "text"):
            continue
        raw = block.get("text")
        if isinstance(raw, str) and raw.strip():
            texts.append(raw.strip())
    return texts


def _string_list(rows: object) -> list[str] | None:
    if not isinstance(rows, list):
        return None
    texts: list[str] = []
    for row in rows:
        if isinstance(row, str) and row.strip():
            texts.append(row.strip())
        elif isinstance(row, dict) and isinstance(row.get("text"), str) and row["text"].strip():
            texts.append(row["text"].strip())
        elif isinstance(row, dict) and isinstance(row.get("content"), str) and row["content"].strip():
            texts.append(row["content"].strip())
        else:
            return None
    return texts


def _jsonl_record(obj: object) -> tuple[list[str], dict, bool]:
    """Return extracted texts, metadata, and whether the object is a known shape."""

    if isinstance(obj, str):
        value = obj.strip()
        if not value:
            return [], {}, True
        return [value], {"record_type": "string"}, True
    if not isinstance(obj, dict):
        return [], {}, False
    record_type = obj.get("type") if isinstance(obj.get("type"), str) else None
    if record_type == "session":
        return [], {"record_type": "session"}, True
    meta: dict = {}
    if record_type:
        meta["record_type"] = record_type
    if isinstance(obj.get("id"), str) and obj["id"]:
        meta["record_id"] = obj["id"]
    message = obj.get("message")
    if isinstance(message, dict):
        role = message.get("role")
        if isinstance(role, str) and role:
            meta["role"] = role
        return _text_blocks(message.get("content")), meta, True
    for key in _JSONL_LIST_KEYS:
        extracted = _string_list(obj.get(key))
        if extracted is not None:
            return extracted, meta, True
    for key in _JSONL_TEXT_KEYS:
        raw = obj.get(key)
        if isinstance(raw, str):
            value = raw.strip()
            if value:
                return [value], meta, True
            return [], meta, True
    if record_type in _JSONL_KNOWN_TYPES:
        return [], meta, True
    return [], {}, False


class JsonlMemorySourceAdapter:
    """Read one JSON object per line from a session or memory log.

    Session headers, thinking blocks, and tool-call blocks are not
    observations. Message text blocks, compaction summaries, and objects with
    ``text`` / ``content`` / ``memory`` / ``summary`` (or ``memories`` /
    ``items``) are. A malformed line is skipped when the file has another
    recognized record. A non-empty file with no recognized record is
    ``unreadable``. Parsing does not write the file.
    """

    def can_handle(self, path: str) -> bool:
        return matches_recognized_name(path, JSONL_GLOBS)

    def parse(self, payload: bytes) -> tuple[list[dict], str | None]:
        try:
            text = payload.decode("utf-8-sig")
        except UnicodeDecodeError:
            return [], "unreadable"
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        items: list[dict] = []
        recognized = False
        saw_line = False
        for raw in text.split("\n"):
            if not raw.strip():
                continue
            saw_line = True
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            texts, meta, known = _jsonl_record(obj)
            if not known:
                continue
            recognized = True
            for value in texts:
                item = {"text": value, "digest": _digest(value)}
                item.update(meta)
                items.append(item)
        if items or recognized or not saw_line:
            return items, None
        return [], "unreadable"


@dataclass(frozen=True)
class SourceConfig:
    """Which sources discovery recognizes and which adapter parses them.

    Markdown and JSON names stay exact (``MEMORY.md``, ``memory.md``,
    ``memories.json``, ``memory.json``). ``*.sqlite``, ``*.sqlite3``, and
    ``*.jsonl`` are recognized as well, on the file's base name. Pass
    ``recognize_sqlite=False`` or ``recognize_jsonl=False`` to opt out of
    those suffixes. ``SourceConfig.extended()`` enables the v2 Markdown
    adapter and the persona/memory names. It leaves the SQLite and JSONL
    suffixes on. ``recognize_dated_markdown=True`` also recognizes basenames
    that are exactly ``YYYY-MM-DD.md`` by adding ``DATED_MARKDOWN_TOKEN``
    to the Markdown name set. That token is off unless requested.
    """

    markdown_names: frozenset[str] = DEFAULT_MARKDOWN_NAMES
    json_names: frozenset[str] = JSON_NAMES
    markdown_v2: bool = False
    recognize_sqlite: bool = True
    recognize_jsonl: bool = True

    @property
    def recognized_names(self) -> frozenset[str]:
        names: set[str] = set(self.markdown_names) | set(self.json_names)
        if self.recognize_sqlite:
            names |= set(SQLITE_GLOBS)
        if self.recognize_jsonl:
            names |= set(JSONL_GLOBS)
        return frozenset(names)

    @classmethod
    def extended(
        cls,
        extra_markdown_names: frozenset[str] | set[str] = frozenset(),
        *,
        recognize_dated_markdown: bool = False,
    ) -> "SourceConfig":
        names = set(DEFAULT_MARKDOWN_NAMES) | set(EXTENDED_MARKDOWN_NAMES) | set(extra_markdown_names)
        if recognize_dated_markdown:
            names.add(DATED_MARKDOWN_TOKEN)
        return cls(markdown_names=frozenset(names), markdown_v2=True)

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
SQLITE_ADAPTER: SourceAdapter = SqliteMemorySourceAdapter()
JSONL_ADAPTER: SourceAdapter = JsonlMemorySourceAdapter()
