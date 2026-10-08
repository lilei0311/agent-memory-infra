"""Stage 10 bootstrap discovery. Does not import memory_infra.store."""

from pathlib import Path

import pytest

from memory_infra.bootstrap import BootstrapSession, SkillBootstrap, discover_environment
from memory_infra.skill import SkillApi, SkillBootstrap as SkillBootstrapFromSkill


def test_public_entry_does_not_require_store_import():
    assert SkillBootstrapFromSkill is SkillBootstrap


def test_empty_environment():
    boot = SkillBootstrap()
    result = boot.install("agent-a")
    assert result["ok"] is True
    assert result["op"] == "bootstrap"
    assert result["read_only"] is True
    assert result["imported"] is False
    assert result["explicit_import"] == "not_invoked"
    assert result["mechanism_memory_created"] is False
    assert result["sources"] == []
    assert result["inventory"]["scanned"] == 0
    assert "empty environment" in result["diagnostics"][0]


def test_recognizable_existing_memory(tmp_path: Path):
    (tmp_path / "MEMORY.md").write_text("caller note\n", encoding="utf-8")
    (tmp_path / "memories.json").write_text("[]", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("other", encoding="utf-8")
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    result = discover_environment(caller_id="agent-a", root=tmp_path)
    after = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    assert before == after
    kinds = {item["path"]: item["status"] for item in result["sources"]}
    assert kinds["MEMORY.md"] == "recognized"
    assert kinds["memories.json"] == "recognized"
    assert kinds["notes.txt"] == "unknown"
    assert result["imported"] is False
    assert result["inventory"]["recognized"] == 2
    assert result["inventory"]["unknown"] == 1


def test_unknown_and_unreadable_sources():
    artifacts = {
        "MEMORY.md": b"keep",
        "other.bin": b"nope",
        "secret.json": None,
    }
    result = discover_environment(caller_id="agent-a", artifacts=artifacts)
    by_path = {item["path"]: item for item in result["sources"]}
    assert by_path["MEMORY.md"]["status"] == "recognized"
    assert by_path["other.bin"]["status"] == "unknown"
    assert by_path["secret.json"]["status"] == "unreadable"
    assert result["inventory"]["unreadable"] == 1
    assert any("partial discovery" in line for line in result["diagnostics"])


def test_bounded_scan_is_deterministic():
    artifacts = {f"file-{index:02d}.txt": b"x" for index in range(5)}
    artifacts["MEMORY.md"] = b"m"
    first = discover_environment(caller_id="agent-a", artifacts=artifacts, scan_limit=3)
    second = discover_environment(caller_id="agent-a", artifacts=artifacts, scan_limit=3)
    assert first["sources"] == second["sources"]
    assert first["inventory"]["truncated"] is True
    assert first["inventory"]["scanned"] == 3
    assert [item["path"] for item in first["sources"]] == sorted(artifacts)[:3]


def test_repeated_bootstrap_is_idempotent(tmp_path: Path):
    target = tmp_path / "memory.md"
    target.write_text("stable\n", encoding="utf-8")
    boot = SkillBootstrap()
    session = boot.open("agent-a")
    first = session.install(root=tmp_path)
    second = session.install(root=tmp_path)
    assert first == second
    assert target.read_text(encoding="utf-8") == "stable\n"
    assert session.last_inventory() == first


def test_caller_isolation():
    boot = SkillBootstrap()
    agent_a = boot.open("agent-a")
    agent_b = boot.open("agent-b")
    agent_a.install(artifacts={"MEMORY.md": b"a"})
    agent_b.install(artifacts={"notes.txt": b"b"})
    assert agent_a.last_inventory()["caller_id"] == "agent-a"
    assert agent_b.last_inventory()["sources"][0]["path"] == "notes.txt"
    assert agent_a.last_inventory()["sources"][0]["path"] == "MEMORY.md"
    assert boot.open("agent-c").last_inventory() is None


def test_cross_caller_inventory_access_rejected():
    boot = SkillBootstrap()
    agent_a = boot.open("agent-a")
    agent_b = boot.open("agent-b")
    agent_a.install(artifacts={"MEMORY.md": b"secret-a"})
    agent_b.install(artifacts={"notes.txt": b"secret-b"})
    with pytest.raises(TypeError):
        agent_a.last_inventory("agent-b")
    with pytest.raises(PermissionError):
        boot.last_inventory("agent-b")
    other = boot.open("agent-b")
    assert other.last_inventory() is None
    assert "secret-b" not in str(agent_a.last_inventory())
    assert isinstance(agent_a, BootstrapSession)


def test_no_implicit_import_or_mechanism_mutation(tmp_path: Path):
    (tmp_path / "MEMORY.md").write_text("do not ingest\n", encoding="utf-8")
    boot = SkillBootstrap()
    found = boot.install("agent-a", root=tmp_path)
    api = SkillApi.open_memory()
    traced = api.invoke("agent-a", "inspect_trace", {})
    retrieved = api.invoke("agent-a", "retrieve", {"query": "do not ingest"})
    assert found["mechanism_memory_created"] is False
    assert traced == {"ok": True, "op": "inspect_trace", "result": ()}
    assert retrieved["ok"] is True
    assert retrieved["result"]["selected"] == ()


def test_unreadable_directory(tmp_path: Path):
    missing = tmp_path / "missing-root"
    result = discover_environment(caller_id="agent-a", root=missing)
    assert result["ok"] is True
    assert result["sources"][0]["status"] == "unreadable"
    assert result["imported"] is False


def test_caller_id_required():
    with pytest.raises(ValueError):
        discover_environment(caller_id="  ")
