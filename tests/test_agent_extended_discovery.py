"""Personal agent tools discover OpenClaw persona markdown names.

Synthetic files only. ``SkillEntrypoint()`` stays on bare ``SourceConfig()``.
Dated markdown names and item dedup stay opt-in.
"""

from __future__ import annotations

from pathlib import Path

from memory_infra.agent_tools import AgentMemoryTools
from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.importer import parse_recognized
from memory_infra.source_adapter import (
    DEFAULT_MARKDOWN_NAMES,
    EXTENDED_MARKDOWN_NAMES,
    MARKDOWN_ADAPTER,
    SourceConfig,
    matches_recognized_name,
    resolve_discovered_path,
    select_discovered_paths,
)

REPO = Path(__file__).resolve().parents[1]


def _write(root: Path, name: str, text: str) -> None:
    (root / name).write_text(text, encoding="utf-8")


def _persona_tree(root: Path) -> None:
    for name in sorted(EXTENDED_MARKDOWN_NAMES):
        if name == "AGENTS.md":
            continue
        _write(root, name, f"- synthetic fact from {name}\n")
    _write(
        root,
        "AGENTS.md",
        "---\nname: persona\n---\n# Rules\n- keep the suite green\n",
    )
    # One memory.md casing only. Writing both in the same directory folds
    # together on case-insensitive APFS, then status["memory.md"] KeyErrors
    # when os.walk reports MEMORY.md (or the reverse).
    _write(root, "MEMORY.md", "- synthetic fact from MEMORY.md\n")
    _write(root, "2026-04-02.md", "- dated fact stays out\n")
    _write(root, "notes-2026-04-02.md", "- date inside a longer name stays out\n")
    _write(root, "random.md", "- not a persona file\n")


def _status(found: dict) -> dict[str, str]:
    return {item["path"]: item["status"] for item in found["sources"]}


def test_agent_tools_discover_extended_markdown_names(tmp_path: Path):
    _persona_tree(tmp_path)
    tools = AgentMemoryTools.open("cursor")
    found = tools.discover(root=tmp_path)
    assert found["imported"] is False
    assert found["tool"] == "discover"
    status = _status(found)
    kinds = {item["path"]: item["kind"] for item in found["sources"]}
    expected = set(EXTENDED_MARKDOWN_NAMES)
    for name in expected:
        assert status[name] == "recognized"
        assert kinds[name] == "markdown_memory"
    memory_path = resolve_discovered_path(status, "MEMORY.md")
    assert memory_path is not None
    assert status[memory_path] == "recognized"
    assert kinds[memory_path] == "markdown_memory"
    assert status["2026-04-02.md"] == "unknown"
    assert status["notes-2026-04-02.md"] == "unknown"
    assert status["random.md"] == "unknown"

    preview = tools.preview(["AGENTS.md"])
    assert preview["dry_run"] is True
    assert preview["redaction_enabled"] is False
    refused = tools.import_sources(["AGENTS.md"], consent=False)
    assert refused["imported"] is False
    assert refused["created_count"] == 0
    accepted = tools.import_sources(["AGENTS.md"], consent=True)
    assert accepted["imported"] is True
    assert accepted["created_count"] == 1
    assert accepted["redaction_enabled"] is False
    texts = [item["text"] for item in tools.retrieve("suite green")["memories"]]
    assert "keep the suite green" in texts
    assert all("name:" not in text and "persona" not in text for text in texts)


def test_agent_tools_leave_dated_names_and_item_dedup_opt_in(tmp_path: Path):
    root = tmp_path / "sources"
    root.mkdir()
    _write(root, "USER.md", "- same synthetic line\n- same synthetic line\n")
    _write(root, "2026-04-02.md", "- dated fact stays out\n")
    tools = AgentMemoryTools.open("cursor")
    status = _status(tools.discover(root=root))
    assert status["USER.md"] == "recognized"
    assert status["2026-04-02.md"] == "unknown"
    imported = tools.import_sources(["USER.md"], consent=True)
    assert imported["created_count"] == 2

    dated = AgentMemoryTools.open(
        "cursor",
        sources=SourceConfig.extended(recognize_dated_markdown=True),
    )
    dated_status = _status(dated.discover(root=root))
    assert dated_status["2026-04-02.md"] == "recognized"
    assert dated_status["USER.md"] == "recognized"


def test_agent_tools_narrow_sources_override_and_entrypoint_default(tmp_path: Path):
    root = tmp_path / "sources"
    root.mkdir()
    _write(root, "AGENTS.md", "- synthetic persona line\n")
    _write(root, "MEMORY.md", "- synthetic memory line\n")
    narrow = AgentMemoryTools.open("cursor", sources=SourceConfig())
    status = _status(narrow.discover(root=root))
    assert status["AGENTS.md"] == "unknown"
    assert status["MEMORY.md"] == "recognized"

    handle = SkillEntrypoint().open("stage-agent")
    disc = handle.start(root=root)
    entry_status = {item["path"]: item["status"] for item in disc["sources"]}
    assert entry_status["AGENTS.md"] == "unknown"
    assert entry_status["MEMORY.md"] == "recognized"
    assert disc["imported"] is False


def test_install_docs_state_openclaw_hygiene_and_current_main():
    install = (REPO / "docs" / "AGENT_INSTALL.md").read_text(encoding="utf-8")
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    status = (REPO / "docs" / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    for phrase in (
        "agent-memory-infra-eval",
        ".agent-memory-infra/store",
        "redact=False",
        ".backup",
        "AGENTS.md",
        "YYYY-MM-DD.md",
        "Never commit real memory",
    ):
        assert phrase in install
    assert "agent-memory-infra-eval" in readme
    assert "docs/AGENT_INSTALL.md" in readme
    top = status.split("## Immutable product goal")[0]
    assert "usable(f)" in top
    assert "a8912d8" in top
    assert "#62" in top
    assert "#46" in top
    assert "active work unit" not in top
    assert "#61" in top


def test_memory_md_name_aliases_are_case_insensitive():
    names = DEFAULT_MARKDOWN_NAMES
    for alias in ("MEMORY.md", "memory.md", "Memory.md", "MEMORY.MD"):
        assert matches_recognized_name(alias, names)
        assert MARKDOWN_ADAPTER.can_handle(alias)
    assert not matches_recognized_name("memory.json", names)
    items, err = parse_recognized("Memory.md", b"- alias fact\n")
    assert err is None and items[0]["text"] == "alias fact"
    assert resolve_discovered_path(["memory.md", "notes.txt"], "MEMORY.md") == "memory.md"
    assert resolve_discovered_path(["MEMORY.md"], "memory.md") == "MEMORY.md"
    assert resolve_discovered_path(["MEMORY.md", "memory.md"], "MEMORY.md") == "MEMORY.md"
    assert resolve_discovered_path(["MEMORY.md", "memory.md"], "Memory.md") is None
    assert select_discovered_paths(["MEMORY.md", "missing.md"], ["memory.md"]) == ["memory.md"]


def test_lowercase_memory_md_is_recognized_and_importable(tmp_path: Path):
    _write(tmp_path, "memory.md", "- lowercase synthetic fact\n")
    tools = AgentMemoryTools.open("cursor")
    found = tools.discover(root=tmp_path)
    status = _status(found)
    actual = resolve_discovered_path(status, "MEMORY.md")
    assert actual is not None
    assert status[actual] == "recognized"
    preview = tools.preview(["MEMORY.md"])
    assert preview["sources"][0]["status"] == "would_import"
    imported = tools.import_sources(["MEMORY.md"], consent=True)
    assert imported["imported"] is True
    assert imported["created_count"] == 1
    assert imported["created"][0]["path"] == actual


def test_both_memory_md_casings_when_filesystem_allows(tmp_path: Path):
    _write(tmp_path, "MEMORY.md", "- synthetic fact from MEMORY.md\n")
    _write(tmp_path, "memory.md", "- synthetic fact from memory.md\n")
    on_disk = {path.name for path in tmp_path.iterdir() if path.is_file()}
    tools = AgentMemoryTools.open("cursor")
    status = _status(tools.discover(root=tmp_path))
    memory_status = {
        path: value for path, value in status.items() if path.casefold() == "memory.md"
    }
    assert memory_status and all(value == "recognized" for value in memory_status.values())
    if {"MEMORY.md", "memory.md"} <= on_disk:
        assert status["MEMORY.md"] == "recognized"
        assert status["memory.md"] == "recognized"
        refused = tools.import_sources(["Memory.md"], consent=True)
        assert refused["created_count"] == 0
        assert refused["rejected"][0]["reason"] == "not_in_discovery"
