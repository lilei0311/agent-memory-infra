"""In-process tools an agent can call without spelling the Skill API.

Maps discover, preview, import, retrieve, and record_outcome onto
``SkillEntrypoint``. This is not an MCP server, HTTP service, or marketplace
plugin. Redaction stays off unless the caller passes ``redact=True``.
Discovery never imports. ``import_sources`` runs only when ``consent is True``.

``open`` discovers and imports with ``SourceConfig.extended()``: the OpenClaw
persona markdown names and the v2 parser, plus the usual JSON, SQLite, and
JSONL names. Dated ``YYYY-MM-DD.md`` names stay off unless the caller passes
``sources=``. Item dedup stays off. ``SkillEntrypoint()`` with no ``sources``
argument is still the narrow set.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.source_adapter import SourceConfig, select_discovered_paths

__all__ = ["AgentMemoryTools", "personal_store_path", "run_scripted_session"]


def personal_store_path() -> Path:
    """File-backend snapshot under the user home, outside a git clone.

    ``~/.agent-memory-infra/store``. Do not point this at the public repo.
    A scratch directory created inside a clone belongs in ``local-memory/``
    or ``.agent-memory-infra/``, both gitignored.
    """

    return Path.home() / ".agent-memory-infra" / "store"


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return tuple(_plain(item) for item in value)
    return value


def _tree_digest(root: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    if not root.exists():
        return found
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            found[path.relative_to(root).as_posix()] = digest
    return found


class AgentMemoryTools:
    """Caller-bound tools. One ``caller_id``. No mechanism ownership."""

    def __init__(self, handle) -> None:
        self._handle = handle

    @classmethod
    def open(
        cls,
        caller_id: str,
        *,
        store_path: str | Path | None = None,
        redact: bool = False,
        seed: int = 7,
        context_budget: int = 4,
        policy: str = "none",
        sources: SourceConfig | None = None,
    ) -> "AgentMemoryTools":
        """Open a session.

        ``redact`` defaults to false. ``store_path`` selects the file backend.
        Discovery and import use ``SourceConfig.extended()`` unless ``sources``
        is passed. Dated ``YYYY-MM-DD.md`` names stay off on that default.
        Item dedup is not enabled.
        """

        kwargs = {
            "seed": seed,
            "context_budget": context_budget,
            "policy": policy,
            "redact": redact,
            "sources": sources if sources is not None else SourceConfig.extended(),
        }
        if store_path is None:
            entry = SkillEntrypoint(**kwargs)
        else:
            entry = SkillEntrypoint(backend="file", path=store_path, **kwargs)
        return cls(entry.open(caller_id))

    def discover(
        self,
        *,
        root: str | Path | None = None,
        artifacts: Mapping[str, bytes | None] | None = None,
        scan_limit: int | None = None,
        max_depth: int | None = None,
    ) -> dict:
        """Read-only discovery. Does not import and does not enable memory writes."""

        kwargs: dict = {}
        if scan_limit is not None:
            kwargs["scan_limit"] = scan_limit
        if max_depth is not None:
            kwargs["max_depth"] = max_depth
        report = self._handle.start(root=root, artifacts=artifacts, **kwargs)
        sources = tuple(
            {
                "path": item["path"],
                "status": item["status"],
                "kind": item.get("kind", ""),
            }
            for item in report["sources"]
        )
        return {
            "ok": True,
            "tool": "discover",
            "imported": False,
            "caller_id": report["caller_id"],
            "sources": sources,
            "diagnostics": tuple(report["diagnostics"]),
        }

    def preview(self, paths: list[str], *, redact: bool | None = None) -> dict:
        """Dry run. Parses and counts. Writes nothing and does not enable memory."""

        report = self._handle.preview_import(list(paths), redact=redact)
        return {
            "ok": True,
            "tool": "preview",
            "dry_run": True,
            "imported": False,
            "redaction_enabled": bool(report["redaction"]["enabled"]),
            "sources": tuple(report["sources"]),
        }

    def import_sources(
        self,
        paths: list[str],
        *,
        consent: bool = False,
        redact: bool | None = None,
    ) -> dict:
        """Import only when ``consent is True``. A truthy string is not consent."""

        if consent is not True:
            return {
                "ok": True,
                "tool": "import",
                "imported": False,
                "consent": False,
                "reason": "consent_required",
                "created_count": 0,
                "created": (),
            }
        report = self._handle.import_selected(list(paths), redact=redact)
        created = tuple(
            {
                "path": row["path"],
                "event_id": row["event_id"],
                "point_id": row["point_id"],
            }
            for row in report["created"]
        )
        return {
            "ok": True,
            "tool": "import",
            "imported": bool(report["imported"]),
            "consent": True,
            "created_count": len(created),
            "created": created,
            "rejected": tuple(report["rejected"]),
            "redaction_enabled": bool(report["redaction"]["enabled"]),
        }

    def retrieve(self, query: str) -> dict:
        """Retrieve, then resolve each selected id to observation text.

        Uses ``invoke("retrieve")`` and ``invoke("read_event")`` only.
        """

        self._handle.enable_memory()
        result = self._handle.invoke("retrieve", {"query": query})["result"]
        memories = []
        for event_id in result["selected"]:
            event = self._handle.invoke("read_event", {"event_id": event_id})["result"]
            memories.append(
                {
                    "event_id": event["event_id"],
                    "text": event["observation"],
                    "source": event["source"],
                }
            )
        return {
            "ok": True,
            "tool": "retrieve",
            "op": "retrieve",
            "query": result["query"],
            "retrieval_id": result["retrieval_id"],
            "query_used_for_ranking": bool(result["query_used_for_ranking"]),
            "memories": tuple(memories),
        }

    def record_outcome(self, name: str, **fields: object) -> dict:
        """Record a Skill API signal. Does not invent user_feedback, task_success, or used."""

        self._handle.enable_memory()
        body = self._handle.invoke("signal", {"name": name, **fields})["result"]
        return {
            "ok": True,
            "tool": "record_outcome",
            "op": "signal",
            "name": body["signal"],
            "result": _plain(body["result"]),
        }

    def read_graph(self) -> dict:
        """Read-only projection. Does not create graph state."""

        self._handle.enable_memory()
        result = self._handle.invoke("read_graph", {})["result"]
        return {
            "ok": True,
            "tool": "read_graph",
            "read_only": bool(result["read_only"]),
            "node_count": len(result["nodes"]),
            "edge_count": len(result["edges"]),
        }

    def save(self) -> dict:
        """Persist the mechanism snapshot when a file backend is open."""

        self._handle.enable_memory()
        envelope = self._handle.invoke("save", {})
        return {
            "ok": True,
            "tool": "save",
            "op": "save",
            "integrity": envelope["integrity"],
        }

    def load(self) -> dict:
        """Restore a mechanism snapshot. Caller notes are not part of the snapshot."""

        self._handle.enable_memory()
        envelope = self._handle.invoke("load", {})
        return {
            "ok": True,
            "tool": "load",
            "op": "load",
            "integrity": envelope["integrity"],
        }


def run_scripted_session(
    root: str | Path,
    *,
    caller_id: str = "mac-agent",
    store_path: str | Path | None = None,
    select: list[str] | None = None,
    consent: bool = False,
    query: str,
    outcome_signal: str | None = None,
    outcome_fields: Mapping[str, object] | None = None,
    redact: bool = False,
    sources: SourceConfig | None = None,
) -> dict:
    """Discover, preview, maybe import, retrieve, and optionally signal.

    The agent-facing path. Callers do not touch ``invoke`` or ``import_selected``.
    Import runs only when ``consent`` is exactly true. Redaction stays off
    unless ``redact=True``.
    """

    root_path = Path(root)
    before = _tree_digest(root_path)
    tools = AgentMemoryTools.open(
        caller_id, store_path=store_path, redact=redact, sources=sources
    )
    discovered = tools.discover(root=root_path)
    recognized = [item["path"] for item in discovered["sources"] if item["status"] == "recognized"]
    chosen = recognized if select is None else select_discovered_paths(select, recognized)
    preview = tools.preview(chosen)
    graph_before = tools.read_graph()
    imported = tools.import_sources(chosen, consent=consent)
    graph_after = tools.read_graph()
    retrieved = tools.retrieve(query)
    outcome = None
    if outcome_signal and retrieved["memories"]:
        fields = dict(outcome_fields or {})
        if outcome_signal == "consolidate" and "event_id" not in fields:
            fields["event_id"] = retrieved["memories"][0]["event_id"]
            fields.setdefault("evidence", "scripted agent session")
        outcome = tools.record_outcome(outcome_signal, **fields)
    saved = tools.save() if store_path is not None else None
    after = _tree_digest(root_path)
    would_create = 0
    for source in preview["sources"]:
        if isinstance(source, Mapping) and source.get("status") == "would_import":
            would_create += int(source.get("would_create", 0))
    return {
        "discovery_imported": discovered["imported"],
        "recognized": tuple(recognized),
        "preview_dry_run": preview["dry_run"],
        "preview_would_create": would_create,
        "redaction_enabled": preview["redaction_enabled"],
        "graph_nodes_before_import": graph_before["node_count"],
        "graph_nodes_after_import": graph_after["node_count"],
        "consent": consent is True,
        "imported": imported["imported"],
        "created_count": imported["created_count"],
        "reason": imported.get("reason"),
        "memories": retrieved["memories"],
        "outcome": outcome,
        "saved": saved,
        "sources_unchanged": before == after,
    }
