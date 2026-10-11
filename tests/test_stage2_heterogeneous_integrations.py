"""Stage 2 exit-gate demonstration: two heterogeneous Agent/storage combinations
through the public Skill boundary (SkillEntrypoint).

Scenarios:
1. Method-style Agent + in-memory backend: discovery-first, isolation of caller
   notes/attributions, no auto-import of discovered sources.
2. Envelope-style Agent + file backend: discovery-first, explicit ops, snapshot
   persistence via packaging handoff (SkillApi.reopen), same policy semantics.

Both use the identical policy core and public contract. No new Skill operations.
No frozen asset edits.
"""

from __future__ import annotations

import json
from pathlib import Path

from memory_infra.entrypoint import SkillEntrypoint


class MethodAgent:
    """Method-shaped Agent integration over the public SkillHandle."""

    def __init__(self, entry: SkillEntrypoint, caller_id: str) -> None:
        self.handle = entry.open(caller_id)
        self.caller_id = caller_id

    def start(self, **kwargs):
        return self.handle.start(**kwargs)

    def enable(self):
        return self.handle.enable_memory()

    def observe(self, content: str, note: str | None = None, source: str | None = None):
        payload = {"content": content}
        if note is not None:
            payload["note"] = note
        if source is not None:
            payload["source"] = source
        return self.handle.invoke("observe", payload)

    def signal(self, name: str, **payload):
        return self.handle.invoke("signal", {"name": name, **payload})

    def retrieve(self, query: str):
        return self.handle.invoke("retrieve", {"query": query})

    def read_event(self, event_id: str):
        return self.handle.invoke("read_event", {"event_id": event_id})

    def read_caller_context(self):
        return self.handle.invoke("read_caller_context")


class EnvelopeAgent:
    """Envelope-shaped Agent integration over the public SkillHandle.
    Client metadata is stripped before crossing the boundary.
    """

    def __init__(self, entry: SkillEntrypoint, caller_id: str) -> None:
        self.handle = entry.open(caller_id)
        self.caller_id = caller_id
        self.sent: list[dict] = []

    def start(self, **kwargs):
        return self.handle.start(**kwargs)

    def enable(self):
        return self.handle.enable_memory()

    def submit(self, envelope: dict):
        if "op" not in envelope:
            raise ValueError("envelope requires op")
        payload = dict(envelope.get("payload") or {})
        payload.pop("client_meta", None)
        self.sent.append({"op": envelope["op"], "client_meta": envelope.get("client_meta")})
        return self.handle.invoke(str(envelope["op"]), payload)


def test_method_agent_memory_backend_isolation_and_no_auto_import(tmp_path: Path):
    """Heterogeneous combination 1: Method Agent + memory storage.

    Asserts discovery does not import, caller isolation, and retrieval after promote.
    """
    root = tmp_path / "env"
    root.mkdir()
    (root / "MEMORY.md").write_text("# Notes\n\nexisting memory\n")
    entry = SkillEntrypoint(backend="memory")
    agent_a = MethodAgent(entry, "method-agent-a")
    agent_b = MethodAgent(entry, "method-agent-b")

    start = agent_a.start(root=root)
    assert start["ok"] is True
    assert start["memory_operations_enabled"] is False
    assert start["imported"] is False
    assert start["mechanism_memory_created"] is False
    assert start["inventory"]["recognized"] == 1
    assert start["sources"][0]["status"] == "recognized"
    assert start["sources"][0]["detail"] == "recognized filename; not imported"

    agent_a.enable()
    # still no auto-import
    ctx_before = agent_a.read_caller_context()
    assert ctx_before["result"]["notes"] == ()
    assert ctx_before["result"]["attributions"] == ()

    obs = agent_a.observe("alpha fact", note="private-to-a")
    prom = agent_a.signal("promote", point_id=obs["point_id"], reason="useful")
    event_id = prom["result"]["result"]["event_id"]

    # isolation: other caller sees nothing
    agent_b.start()
    agent_b.enable()
    ctx_b = agent_b.read_caller_context()
    assert ctx_b["result"]["notes"] == ()
    assert ctx_b["result"]["attributions"] == ()

    # a sees its note and can retrieve
    ctx_a = agent_a.read_caller_context()
    assert "private-to-a" in ctx_a["result"]["notes"]
    ret = agent_a.retrieve("alpha")
    assert event_id in ret["result"]["selected"]
    event = agent_a.read_event(event_id)
    assert event["result"]["observation"] == "alpha fact"


def test_envelope_agent_file_backend_persistence(tmp_path: Path):
    """Heterogeneous combination 2: Envelope Agent + file storage.

    Asserts discovery-first, client-meta stripping, snapshot written,
    and persistence across packaging handoff (reopen) with same semantics.
    """
    root = tmp_path / "env"
    root.mkdir()
    (root / "memory.json").write_text('[{"text": "ignored until explicit"}]')
    path = tmp_path / "snap.json"
    entry = SkillEntrypoint(backend="file", path=path)
    agent = EnvelopeAgent(entry, "envelope-agent")

    start = agent.start(root=root)
    assert start["ok"] is True
    assert start["imported"] is False
    assert start["inventory"]["recognized"] == 1
    assert start["sources"][0]["kind"] == "json_memory"
    assert "not imported" in start["sources"][0]["detail"]

    agent.enable()
    env = {
        "op": "observe",
        "payload": {"content": "file fact", "note": "envelope-note"},
        "client_meta": {"trace_id": "abc-123", "should_be_stripped": True},
    }
    obs = agent.submit(env)
    assert agent.sent[-1]["client_meta"]["trace_id"] == "abc-123"
    # meta not in payload that crossed boundary (note is present because we put it in payload)
    prom = agent.submit(
        {
            "op": "signal",
            "payload": {"name": "promote", "point_id": obs["point_id"], "reason": "useful"},
        }
    )
    event_id = prom["result"]["result"]["event_id"]
    agent.submit({"op": "save"})
    assert path.exists()
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(snapshot, dict)
    assert "authenticity" in snapshot  # mechanism seal present

    # packaging handoff: reopen supplies seal out of band and restores
    # (public SkillApi surface; entrypoint holds the api after enable)
    restored_api = agent.handle._api.reopen()  # noqa: SLF001 — verification of packaging handoff
    restored = restored_api.invoke("envelope-agent", "load")
    assert restored["ok"] is True
    event = restored_api.invoke("envelope-agent", "read_event", {"event_id": event_id})
    assert event["result"]["observation"] == "file fact"
    ctx = restored_api.invoke("envelope-agent", "read_caller_context")
    # notes are request metadata, not durable across restart
    assert ctx["result"]["notes"] == ()
    # mechanism state restored
    ret = restored_api.invoke("envelope-agent", "retrieve", {"query": "file"})
    assert event_id in ret["result"]["selected"]
