"""Cross-adapter conformance for explicit import at the public Skill boundary.

Maps requirements from Issue #50 to evidence.
"""

from pathlib import Path

import pytest

from memory_infra.entrypoint import SkillEntrypoint


def test_cross_adapter_explicit_import_conformance(tmp_path: Path):
    """Both Markdown and JSON require explicit selection; shared behaviors hold.

    Covers:
    - no automatic import during discovery (both formats)
    - explicit selection enforced
    - unknown/unreadable rejected without ingestion
    - repeated import preserves digest idempotency
    - caller-owned source files remain byte-for-byte unchanged
    - source provenance and public result shapes consistent
    """
    md_content = "# notes\n- md fact alpha\n"
    json_content = '{"memories": ["json fact beta"]}\n'
    (tmp_path / "MEMORY.md").write_text(md_content, encoding="utf-8")
    (tmp_path / "memory.json").write_text(json_content, encoding="utf-8")
    (tmp_path / "unknown.txt").write_text("ignore me", encoding="utf-8")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}

    entry = SkillEntrypoint()
    handle = entry.open("cross-agent")
    discovered = handle.start(root=tmp_path)

    # No automatic import during discovery
    assert discovered["imported"] is False
    assert discovered["mechanism_memory_created"] is False
    assert any(s["path"] == "MEMORY.md" and s["status"] == "recognized" for s in discovered["sources"])
    assert any(s["path"] == "memory.json" and s["status"] == "recognized" for s in discovered["sources"])

    # Explicit selection required; import both
    report = handle.import_selected(["MEMORY.md", "memory.json"])
    assert report["explicit_import"] == "invoked"
    assert report["duplicate_policy"] == "idempotent_by_source_digest"
    assert report["mechanism_memory_created"] is True
    created_paths = [item["path"] for item in report["created"]]
    assert "MEMORY.md" in created_paths
    assert "memory.json" in created_paths
    for item in report["created"]:
        assert item["source_ref"].startswith("import:")
        assert "source_digest" in item
        assert item["point_id"] != item["event_id"]
        event = handle.invoke("read_event", {"event_id": item["event_id"]})["result"]
        assert event["source"] == item["source_ref"]
        assert event["observation"] in ("md fact alpha", "json fact beta")

    # Caller files unchanged
    for name, payload in before.items():
        assert (tmp_path / name).read_bytes() == payload

    # Repeated import is idempotent for both
    second = handle.import_selected(["MEMORY.md", "memory.json"])
    assert second["created"] == []
    assert len(second["reused"]) == 2
    assert second["mechanism_memory_created"] is False
    for reused in second["reused"]:
        assert reused["path"] in ("MEMORY.md", "memory.json")
        matching = next(c for c in report["created"] if c["path"] == reused["path"])
        assert reused["point_id"] == matching["point_id"]
        assert reused["source_digest"] == matching["source_digest"]

    # Unknown / unreadable rejected without ingestion
    reject = handle.import_selected(["unknown.txt", "nonexistent.md"])
    assert reject["created"] == []
    reasons = {r["path"]: r["reason"] for r in reject["rejected"]}
    assert reasons["unknown.txt"] in ("not_in_discovery", "unknown") or "unknown" in str(reasons["unknown.txt"])
    assert reasons["nonexistent.md"] == "not_in_discovery"
    # Trace does not contain rejected content
    trace = handle.invoke("inspect_trace", {})["result"]
    assert "ignore me" not in str(trace)
