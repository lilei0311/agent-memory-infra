"""Stage 11 Skill entrypoint. Discovery before memory operations."""

from pathlib import Path

import pytest

from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.skill import SkillApi


def test_entrypoint_module_does_not_import_store():
    source = Path("src/memory_infra/entrypoint.py").read_text(encoding="utf-8")
    imports = [line.strip() for line in source.splitlines() if line.strip().startswith(("import ", "from "))]
    assert all("memory_infra.store" not in line for line in imports)
    assert any(line.startswith("from memory_infra.bootstrap import") for line in imports)
    assert "from memory_infra.skill import SkillApi" in source
    manifest = Path("src/memory_infra/SKILL.md").read_text(encoding="utf-8")
    assert "read-only discovery" in manifest
    assert "does not import" in manifest


def test_fresh_environment_startup():
    entry = SkillEntrypoint()
    report = entry.start("agent-a")
    assert report["ok"] is True
    assert report["phase"] == "discovered"
    assert report["sequence"] == ["discovery"]
    assert report["memory_operations_enabled"] is False
    assert report["imported"] is False
    assert report["mechanism_memory_created"] is False
    assert report["inventory"]["scanned"] == 0
    assert report["sources"] == []
    handle = entry.open("agent-a")
    assert handle.inventory() is None


def test_recognizable_discovery_before_memory_operations(tmp_path: Path):
    (tmp_path / "MEMORY.md").write_text("caller note\n", encoding="utf-8")
    (tmp_path / "memory.json").write_text("{}\n", encoding="utf-8")
    entry = SkillEntrypoint()
    handle = entry.open("agent-a")
    report = handle.start(root=tmp_path)
    assert report["sequence"] == ["discovery"]
    assert report["memory_operations_enabled"] is False
    recognized = {
        item["path"]
        for item in report["sources"]
        if item["status"] == "recognized"
    }
    assert recognized == {"MEMORY.md", "memory.json"}
    with pytest.raises(RuntimeError):
        handle.invoke("retrieve", {"query": "caller note"})
    ready = handle.enable_memory()
    assert ready["sequence"] == ["discovery", "memory"]
    traced = handle.invoke("inspect_trace", {})
    retrieved = handle.invoke("retrieve", {"query": "caller note"})
    assert traced["result"] == ()
    assert retrieved["result"]["selected"] == ()
    assert (tmp_path / "MEMORY.md").read_text(encoding="utf-8") == "caller note\n"


def test_unknown_and_unreadable_do_not_abort(tmp_path: Path):
    missing = tmp_path / "missing-root"
    entry = SkillEntrypoint()
    report = entry.start(
        "agent-a",
        root=missing,
        artifacts={"other.bin": b"nope", "secret.json": None, "MEMORY.md": b"keep"},
    )
    assert report["ok"] is True
    assert report["phase"] == "discovered"
    by_path = {item["path"]: item["status"] for item in report["sources"]}
    assert by_path["MEMORY.md"] == "recognized"
    assert by_path["other.bin"] == "unknown"
    assert by_path["secret.json"] == "unreadable"
    assert by_path["."] == "unreadable"
    assert report["imported"] is False


def test_no_implicit_import_or_mechanism_mutation(tmp_path: Path):
    (tmp_path / "MEMORY.md").write_text("do not ingest\n", encoding="utf-8")
    before = (tmp_path / "MEMORY.md").read_bytes()
    entry = SkillEntrypoint()
    report = entry.start("agent-a", root=tmp_path)
    assert report["mechanism_memory_created"] is False
    assert report["discovery"]["explicit_import"] == "not_invoked"
    api = SkillApi.open_memory()
    traced = api.invoke("agent-a", "inspect_trace", {})
    assert traced["result"] == ()
    assert (tmp_path / "MEMORY.md").read_bytes() == before


def test_caller_isolation_through_stage10_boundary():
    entry = SkillEntrypoint()
    agent_a = entry.open("agent-a")
    agent_b = entry.open("agent-b")
    agent_a.start(artifacts={"MEMORY.md": b"secret-a"})
    agent_b.start(artifacts={"notes.txt": b"secret-b"})
    assert agent_a.inventory()["caller_id"] == "agent-a"
    assert agent_a.inventory()["sources"][0]["path"] == "MEMORY.md"
    assert agent_b.inventory()["sources"][0]["path"] == "notes.txt"
    assert "secret-b" not in str(agent_a.inventory())
    other = entry.open("agent-b")
    assert other.inventory() is None
    with pytest.raises(PermissionError):
        entry._bootstrap.last_inventory("agent-a")


def test_repeated_startup_is_idempotent(tmp_path: Path):
    (tmp_path / "memory.md").write_text("stable\n", encoding="utf-8")
    entry = SkillEntrypoint()
    handle = entry.open("agent-a")
    first = handle.start(root=tmp_path)
    second = handle.start(root=tmp_path)
    assert first["sources"] == second["sources"]
    assert first["inventory"] == second["inventory"]
    assert first["diagnostics"] == second["diagnostics"]
    assert handle.inventory()["sources"] == second["sources"]
    assert (tmp_path / "memory.md").read_text(encoding="utf-8") == "stable\n"


def test_memory_before_discovery_rejected():
    entry = SkillEntrypoint()
    handle = entry.open("agent-a")
    with pytest.raises(RuntimeError):
        handle.enable_memory()
    with pytest.raises(RuntimeError):
        handle.invoke("observe", {"text": "no"})
