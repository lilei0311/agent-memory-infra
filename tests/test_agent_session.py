"""Scripted agent session through memory_infra.agent_tools.

Synthetic fixtures only. The test calls the tool functions and does not
spell the raw Skill operations.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from memory_infra.agent_tools import AgentMemoryTools, personal_store_path, run_scripted_session

FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "synthetic"
REPO = Path(__file__).resolve().parents[1]


def test_scripted_session_imports_retrieves_and_signals(tmp_path: Path):
    summary = run_scripted_session(
        FIXTURES,
        caller_id="mac-agent",
        store_path=tmp_path / "store",
        select=["MEMORY.md"],
        consent=True,
        query="explicit confirmation",
        outcome_signal="consolidate",
    )
    assert summary["discovery_imported"] is False
    assert summary["preview_dry_run"] is True
    assert summary["preview_would_create"] == 6
    assert summary["redaction_enabled"] is False
    assert summary["graph_nodes_before_import"] == 0
    assert summary["imported"] is True
    assert summary["created_count"] == 6
    assert summary["graph_nodes_after_import"] > 0
    assert summary["reason"] is None
    assert any("explicit confirmation" in item["text"] for item in summary["memories"])
    assert summary["outcome"]["op"] == "signal"
    assert summary["outcome"]["name"] == "consolidate"
    assert summary["outcome"]["result"]["lifecycle_state"] == "STABLE"
    assert summary["sources_unchanged"] is True
    assert summary["saved"]["integrity"]
    store = tmp_path / "store"
    assert store.is_file()
    assert "MEMORY.md" in summary["recognized"]
    assert not store.is_relative_to(FIXTURES)


def test_scripted_session_does_not_import_without_consent(tmp_path: Path):
    summary = run_scripted_session(
        FIXTURES,
        store_path=tmp_path / "store",
        select=["MEMORY.md"],
        consent=False,
        query="explicit confirmation",
        outcome_signal="consolidate",
    )
    assert summary["discovery_imported"] is False
    assert summary["imported"] is False
    assert summary["created_count"] == 0
    assert summary["reason"] == "consent_required"
    assert summary["graph_nodes_before_import"] == 0
    assert summary["graph_nodes_after_import"] == 0
    assert summary["memories"] == ()
    assert summary["outcome"] is None
    assert summary["redaction_enabled"] is False
    assert summary["sources_unchanged"] is True


def test_import_requires_exact_consent(tmp_path: Path):
    root = tmp_path / "sources"
    root.mkdir()
    note = "- keep this local note\n"
    (root / "MEMORY.md").write_text(note, encoding="utf-8")
    tools = AgentMemoryTools.open("mac-agent", store_path=tmp_path / "store")
    found = tools.discover(root=root)
    assert found["imported"] is False
    assert found["tool"] == "discover"
    refused = tools.import_sources(["MEMORY.md"], consent=False)
    assert refused["reason"] == "consent_required"
    assert refused["imported"] is False
    also_refused = tools.import_sources(["MEMORY.md"], consent="yes")  # type: ignore[arg-type]
    assert also_refused["reason"] == "consent_required"
    assert tools.read_graph()["node_count"] == 0
    assert tools.read_graph()["read_only"] is True
    accepted = tools.import_sources(["MEMORY.md"], consent=True)
    assert accepted["imported"] is True
    assert accepted["redaction_enabled"] is False
    assert accepted["created_count"] == 1
    assert tools.read_graph()["node_count"] > 0
    retrieved = tools.retrieve("local note")
    assert any("keep this local note" in item["text"] for item in retrieved["memories"])
    assert (root / "MEMORY.md").read_text(encoding="utf-8") == note


def test_redact_defaults_off_and_opt_in_is_explicit(tmp_path: Path):
    root = tmp_path / "sources"
    root.mkdir()
    (root / "MEMORY.md").write_text("- hello from a fixture\n", encoding="utf-8")
    off = AgentMemoryTools.open("mac-agent")
    off.discover(root=root)
    assert off.preview(["MEMORY.md"])["redaction_enabled"] is False
    opted = AgentMemoryTools.open("mac-agent", redact=True)
    opted.discover(root=root)
    assert opted.preview(["MEMORY.md"])["redaction_enabled"] is True


def test_personal_store_path_is_under_home_outside_the_repo():
    path = personal_store_path()
    assert path == Path.home() / ".agent-memory-infra" / "store"
    assert path.is_relative_to(Path.home())
    assert REPO not in path.parents


def test_agent_tools_module_does_not_import_store():
    source = (REPO / "src" / "memory_infra" / "agent_tools.py").read_text(encoding="utf-8")
    assert "memory_infra.store" not in source
    manifest = (REPO / "src" / "memory_infra" / "SKILL.md").read_text(encoding="utf-8")
    for phrase in (
        "read-only discovery",
        "does not import",
        "Never auto-import",
        "consent=True",
        "Off by default",
        "personal_store_path",
        ".agent-memory-infra",
        "docs/LOCAL_SOURCES.md",
        "Quick start (personal Skill)",
        "discover",
        "preview",
        "import_sources",
        "retrieve",
        "record_outcome",
        "read_graph",
        "docs/AGENT_INSTALL.md",
    ):
        assert phrase in manifest


def test_session_test_does_not_spelunk_the_skill_api():
    source = (REPO / "tests" / "test_agent_session.py").read_text(encoding="utf-8")
    banned = (
        "import_" + "selected",
        ".in" + "voke(",
        "Skill" + "Entrypoint",
        "read_" + "event",
    )
    for needle in banned:
        assert needle not in source


def _example_env() -> dict[str, str]:
    env = os.environ.copy()
    src = str(REPO / "src")
    previous = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src if not previous else src + os.pathsep + previous
    return env


def test_example_cli_scripted_session_on_synthetic_fixtures():
    proc = subprocess.run(
        [
            sys.executable,
            "examples/agent_session.py",
            "--select",
            "MEMORY.md",
            "--consent",
            "--signal",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO,
        env=_example_env(),
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "discover imported: False" in out
    assert "redaction_enabled: False" in out
    assert "graph nodes before import: 0" in out
    assert "import created: 6" in out
    assert "explicit confirmation" in out
    assert "outcome: STABLE" in out
    assert "sources unchanged: True" in out
    assert "store saved: True" in out


def test_example_cli_declines_import_without_consent():
    proc = subprocess.run(
        [sys.executable, "examples/agent_session.py", "--select", "MEMORY.md"],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO,
        env=_example_env(),
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "discover imported: False" in out
    assert "import created: 0" in out
    assert "retrieve selected: 0" in out
    assert "memory:" not in out
    assert "sources unchanged: True" in out
    assert "redaction_enabled: False" in out
