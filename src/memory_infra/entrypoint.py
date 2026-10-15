"""Stage 11 Skill entrypoint. Discovery first, then the public Skill API.

Startup opens a caller-bound Stage 10 bootstrap session and runs a bounded
read-only scan before any memory operation. Existing caller files are not
imported. Stage 12 import is a separate caller-invoked method. This module
does not import memory_infra.store.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from memory_infra.bootstrap import (
    DEFAULT_MAX_DEPTH,
    DEFAULT_SCAN_LIMIT,
    SkillBootstrap,
)
from memory_infra.importer import DUPLICATE_POLICY, parse_redacted, snapshot_digest, source_ref_for
from memory_infra.redaction import RedactionPolicy, RedactionReport
from memory_infra.source_adapter import SourceConfig
from memory_infra.skill import SkillApi

__all__ = ["DUPLICATE_POLICY", "SKILL_NAME", "SkillEntrypoint", "SkillHandle"]

SKILL_NAME = "agent-memory-infra"


def resolve_import_redaction(
    redact: bool = False, redaction: RedactionPolicy | None = None
) -> RedactionPolicy:
    """Import policy. Off unless ``redact=True`` or an explicit policy is passed."""

    if redaction is not None:
        if redact and not redaction.enabled:
            raise ValueError("redact=True conflicts with a disabled redaction policy")
        return redaction
    if redact:
        return RedactionPolicy()
    return RedactionPolicy.disabled()


def policy_for_call(configured: RedactionPolicy, redact: bool | None) -> RedactionPolicy:
    """Per-call override. ``None`` keeps the entrypoint policy."""

    if redact is None:
        return configured
    if not redact:
        return RedactionPolicy.disabled()
    if configured.enabled and configured.categories:
        return configured
    return RedactionPolicy()


class SkillHandle:
    """Caller-bound startup handle. Discovery notes stay on this handle."""

    def __init__(self, entry: "SkillEntrypoint", caller_id: str) -> None:
        self._entry = entry
        self.caller_id = caller_id
        self._session = None
        self._api = None
        self._sequence: list[str] = []
        self._root: Path | None = None
        self._artifacts: Mapping[str, bytes | None] | None = None
        self._imports: dict[tuple[str, str], list[dict]] = {}

    def start(
        self,
        *,
        root: str | Path | None = None,
        artifacts: Mapping[str, bytes | None] | None = None,
        scan_limit: int = DEFAULT_SCAN_LIMIT,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        """Discovery-first startup. Does not open mechanism memory."""

        self._session = self._entry._bootstrap.open(self.caller_id)
        self._root = Path(root) if root is not None else None
        self._artifacts = artifacts
        self._imports = {}
        note = self._session.install(
            root=root,
            artifacts=artifacts,
            scan_limit=scan_limit,
            max_depth=max_depth,
            recognized_names=self._entry._sources.recognized_names,
        )
        self._api = None
        self._sequence = ["discovery"]
        return {
            "ok": True,
            "phase": "discovered",
            "skill": SKILL_NAME,
            "caller_id": self.caller_id,
            "memory_operations_enabled": False,
            "imported": False,
            "mechanism_memory_created": False,
            "sequence": list(self._sequence),
            "inventory": note["inventory"],
            "diagnostics": note["diagnostics"],
            "sources": note["sources"],
            "discovery": note,
        }

    def enable_memory(self) -> dict:
        """Open the public Skill API only after discovery has completed."""

        if "discovery" not in self._sequence or self._session is None:
            raise RuntimeError("discovery must complete before memory operations")
        if self._api is None:
            self._api = self._entry._open_api()
            self._sequence.append("memory")
        return {
            "ok": True,
            "phase": "ready",
            "caller_id": self.caller_id,
            "memory_operations_enabled": True,
            "imported": False,
            "sequence": list(self._sequence),
        }

    def packaging_seam(self):
        """Public access to the packaging SkillApi for process-restart handoff.

        Returns the SkillApi after memory is enabled. Use .reopen() for
        cross-session persistence on file backend. Does not expose internals.
        """
        if self._api is None:
            raise RuntimeError("memory operations require completed discovery and enable")
        return self._api

    def invoke(self, op: str, payload: Mapping | None = None) -> Mapping:
        if self._api is None or self._sequence[:1] != ["discovery"]:
            raise RuntimeError("memory operations require completed discovery")
        if "memory" not in self._sequence:
            raise RuntimeError("memory operations require completed discovery")
        return self._api.invoke(self.caller_id, op, payload)

    def import_selected(self, paths: list[str], *, redact: bool | None = None) -> dict:
        """Explicit structuring of selected discovered sources.

        Discovery never calls this. Unknown and unreadable selections are
        reported and are not ingested. Duplicate policy is idempotent by
        source path plus the SHA-256 of the selected source snapshot.
        Distinct parsed occurrences in that snapshot are preserved.
        Caller files are not rewritten.

        Text is stored as written. Redaction is off unless the entrypoint was
        built with ``redact=True`` or an enabled ``redaction`` policy, or this
        call passes ``redact=True``. ``redact=False`` forces this call off.
        """

        if self._session is None or "discovery" not in self._sequence:
            raise RuntimeError("explicit import requires completed discovery")
        self.enable_memory()
        inventory = self.inventory() or {"sources": []}
        by_path = {item["path"]: item for item in inventory["sources"]}
        created: list[dict] = []
        rejected: list[dict] = []
        reused: list[dict] = []
        redaction_total = RedactionReport()
        policy = self._policy_for_call(redact)
        for path in paths:
            item = by_path.get(path)
            if item is None:
                rejected.append({"path": path, "status": "rejected", "reason": "not_in_discovery"})
                continue
            if item["status"] != "recognized":
                rejected.append({"path": path, "status": "rejected", "reason": item["status"]})
                continue
            payload, read_error = self._read_source(path)
            if read_error is not None or payload is None:
                rejected.append({"path": path, "status": "rejected", "reason": read_error or "unreadable"})
                continue
            parsed, parse_error, path_report = parse_redacted(path, payload, policy, self._entry._sources)
            if parse_error is not None:
                rejected.append({"path": path, "status": "rejected", "reason": parse_error})
                continue
            source_ref = source_ref_for(path)
            source_digest = snapshot_digest(payload)
            key = (path, source_digest)
            existing = self._imports.get(key)
            if existing is not None:
                reused.extend(existing)
                continue
            records: list[dict] = []
            for occurrence, parsed_item in enumerate(parsed):
                observed = self.invoke(
                    "observe",
                    {"content": parsed_item["text"], "source": source_ref},
                )
                promoted = self.invoke(
                    "signal",
                    {
                        "name": "promote",
                        "point_id": observed["point_id"],
                        "reason": "explicit historical import",
                    },
                )
                mechanism = promoted["result"]["result"]
                record = {
                    "path": path,
                    "status": "imported",
                    "source_digest": source_digest,
                    "occurrence": occurrence,
                    "source_ref": source_ref,
                    "point_id": observed["point_id"],
                    "event_id": mechanism["event_id"],
                    "evidence_ref": mechanism["evidence_ref"],
                }
                records.append(record)
                created.append(record)
            self._imports[key] = records
            redaction_total.items_total += path_report.items_total
            redaction_total.items_redacted += path_report.items_redacted
            for cat, n in path_report.counts.items():
                redaction_total.counts[cat] = redaction_total.counts.get(cat, 0) + n
        if "import" not in self._sequence:
            self._sequence.append("import")
        imported = bool(created or reused)
        return {
            "ok": True,
            "phase": "imported" if imported else "import_reported",
            "caller_id": self.caller_id,
            "explicit_import": "invoked",
            "duplicate_policy": DUPLICATE_POLICY,
            "imported": imported,
            "mechanism_memory_created": bool(created),
            "created": created,
            "reused": reused,
            "rejected": rejected,
            "redaction": {"enabled": policy.enabled, **redaction_total.as_dict()},
            "sequence": list(self._sequence),
        }

    def preview_import(self, paths: list[str], *, redact: bool | None = None) -> dict:
        """Dry run of explicit import. Parse, and redact only when enabled.

        Reports per source how many items would be created and, when redaction
        is on, category counts (never values). Writes nothing, does not enable
        memory operations, and creates no mechanism state. ``redact`` overrides
        the entrypoint the same way as ``import_selected``.
        """

        if self._session is None or "discovery" not in self._sequence:
            raise RuntimeError("import preview requires completed discovery")
        inventory = self.inventory() or {"sources": []}
        by_path = {item["path"]: item for item in inventory["sources"]}
        policy = self._policy_for_call(redact)
        sources: list[dict] = []
        total = RedactionReport()
        for path in paths:
            item = by_path.get(path)
            if item is None:
                sources.append({"path": path, "status": "rejected", "reason": "not_in_discovery"})
                continue
            if item["status"] != "recognized":
                sources.append({"path": path, "status": "rejected", "reason": item["status"]})
                continue
            payload, read_error = self._read_source(path)
            if read_error is not None or payload is None:
                sources.append({"path": path, "status": "rejected", "reason": read_error or "unreadable"})
                continue
            parsed, parse_error, report = parse_redacted(path, payload, policy, self._entry._sources)
            if parse_error is not None:
                sources.append({"path": path, "status": "rejected", "reason": parse_error})
                continue
            total.items_total += report.items_total
            total.items_redacted += report.items_redacted
            for cat, n in report.counts.items():
                total.counts[cat] = total.counts.get(cat, 0) + n
            distinct = len({row["digest"] for row in parsed})
            sources.append(
                {
                    "path": path,
                    "status": "would_import",
                    "items": report.items_total,
                    "distinct_after_redaction": distinct,
                    "source_digest": snapshot_digest(payload),
                    "redaction": report.as_dict(),
                }
            )
        return {
            "ok": True,
            "phase": "import_preview",
            "dry_run": True,
            "caller_id": self.caller_id,
            "imported": False,
            "mechanism_memory_created": False,
            "redaction": {"enabled": policy.enabled, **total.as_dict()},
            "sources": sources,
            "sequence": list(self._sequence),
        }

    def _read_source(self, path: str) -> tuple[bytes | None, str | None]:
        if self._artifacts is not None and path in self._artifacts:
            payload = self._artifacts[path]
            if payload is None:
                return None, "unreadable"
            return payload, None
        if self._root is None:
            return None, "unreadable"
        target = (self._root / path).resolve()
        try:
            target.relative_to(self._root.resolve())
        except ValueError:
            return None, "unreadable"
        try:
            return target.read_bytes(), None
        except OSError:
            return None, "unreadable"

    def _policy_for_call(self, redact: bool | None) -> RedactionPolicy:
        return policy_for_call(self._entry._redaction, redact)

    def inventory(self) -> dict | None:
        if self._session is None:
            return None
        return self._session.last_inventory()


class SkillEntrypoint:
    """Minimal distributable Skill entry. Holds no mechanism state.

    Import redaction is off by default so local personal memory keeps text as
    written. Pass ``redact=True`` to enable every category, or ``redaction=``
    for a narrower ``RedactionPolicy``, before sharing or writing to a
    less-trusted store.
    """

    def __init__(
        self,
        *,
        seed: int = 7,
        context_budget: int = 4,
        policy: str = "none",
        backend: str = "memory",
        path: str | Path | None = None,
        redact: bool = False,
        redaction: RedactionPolicy | None = None,
        sources: SourceConfig | None = None,
    ) -> None:
        self._redaction = resolve_import_redaction(redact, redaction)
        self._sources = sources if sources is not None else SourceConfig()
        if backend not in {"memory", "file"}:
            raise ValueError("backend must be memory or file")
        if backend == "file" and path is None:
            raise ValueError("file backend requires a path")
        self._seed = seed
        self._budget = context_budget
        self._policy = policy
        self._backend = backend
        self._path = path
        self._bootstrap = SkillBootstrap()
        self._handles: dict[str, SkillHandle] = {}

    def open(self, caller_id: str) -> SkillHandle:
        if not isinstance(caller_id, str) or not caller_id.strip():
            raise ValueError("caller_id is required")
        handle = SkillHandle(self, caller_id)
        self._handles[caller_id] = handle
        return handle

    def start(
        self,
        caller_id: str,
        *,
        root: str | Path | None = None,
        artifacts: Mapping[str, bytes | None] | None = None,
        scan_limit: int = DEFAULT_SCAN_LIMIT,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        handle = self.open(caller_id)
        return handle.start(
            root=root,
            artifacts=artifacts,
            scan_limit=scan_limit,
            max_depth=max_depth,
        )

    def _open_api(self) -> SkillApi:
        if self._backend == "file":
            return SkillApi.open_file(
                self._path,
                seed=self._seed,
                context_budget=self._budget,
                policy=self._policy,
            )
        return SkillApi.open_memory(
            seed=self._seed,
            context_budget=self._budget,
            policy=self._policy,
        )
