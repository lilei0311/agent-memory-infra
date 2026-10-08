"""Minimal heterogeneous agent-facing wrappers over CallerSession.

These are local test doubles, not an agent framework, Skill package, or
authentication layer. They do not own durable state transitions.
"""

from __future__ import annotations

from typing import Mapping

from memory_infra.store import CallerSession, MemoryService, SnapshotError


class MethodCaller:
    """Method-shaped client. Local command log stays on the client."""

    def __init__(self, service: MemoryService, caller_id: str) -> None:
        self.session = CallerSession(service, caller_id)
        self.caller_id = caller_id
        self.local_log: list[str] = []

    def observe(self, content: str, note: str | None = None, source: str | None = None) -> Mapping:
        payload: dict[str, str] = {"content": content}
        if note is not None:
            payload["note"] = note
        if source is not None:
            payload["source"] = source
        self.local_log.append(f"observe:{content}")
        return self.session.request("observe", payload)

    def signal(self, name: str, **payload: object) -> Mapping:
        self.local_log.append(f"signal:{name}")
        return self.session.request("signal", {"name": name, **payload})

    def retrieve(self, query: str) -> Mapping:
        self.local_log.append(f"retrieve:{query}")
        return self.session.request("retrieve", {"query": query})

    def read_event(self, event_id: str) -> Mapping:
        return self.session.request("read_event", {"event_id": event_id})

    def read_lifecycle(self, target_id: str) -> Mapping:
        return self.session.request("read_lifecycle", {"target_id": target_id})

    def read_relations(self) -> Mapping:
        return self.session.request("read_relations")

    def inspect_trace(self) -> Mapping:
        return self.session.request("inspect_trace")

    def read_context(self) -> Mapping:
        return self.session.request("read_caller_context")

    def save(self) -> Mapping:
        return self.session.request("save")

    def load(self) -> Mapping:
        return self.session.request("load")


class EnvelopeCaller:
    """Envelope-shaped client. Client metadata is stripped before the boundary."""

    def __init__(self, service: MemoryService, caller_id: str) -> None:
        self.session = CallerSession(service, caller_id)
        self.caller_id = caller_id
        self.sent: list[dict] = []

    def submit(self, envelope: Mapping) -> Mapping:
        if "op" not in envelope:
            raise SnapshotError("envelope requires op")
        payload = dict(envelope.get("payload") or {})
        payload.pop("client_meta", None)
        self.sent.append({"op": envelope["op"], "client_meta": envelope.get("client_meta")})
        return self.session.request(str(envelope["op"]), payload)
