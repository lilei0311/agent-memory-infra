"""Markdown adapter v2: frontmatter, headings, dates, configurable names."""

from pathlib import Path

import pytest

from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.importer import parse_recognized
from memory_infra.redaction import RedactionPolicy
from memory_infra.source_adapter import (
    MARKDOWN_ADAPTER,
    EXTENDED_MARKDOWN_NAMES,
    MarkdownV2SourceAdapter,
    SourceConfig,
    split_frontmatter,
)

DOC = """---
name: user prefs
type: feedback
description: "how the user likes things"
tags: [a, b]
related:
  - one
  - two
---
# Preferences

## Style
- Prefers concise answers
- [x] Verified on 2026-10-01 that dark mode is on

```python
not_a_memory = 1
```

<!-- hidden
comment -->

---

## Tools
1. Use ripgrep
2) Avoid heavy GUI tools
"""


def test_frontmatter_split_variants():
    meta, body, has = split_frontmatter(DOC)
    assert has and meta["name"] == "user prefs" and meta["tags"] == ["a", "b"]
    assert meta["related"] == ["one", "two"] and meta["description"] == "how the user likes things"
    assert body.lstrip().startswith("# Preferences")
    # unterminated block is body, not frontmatter
    text = "---\nname: x\n# no end\n- real line\n"
    assert split_frontmatter(text) == ({}, text, False)
    assert split_frontmatter("no front\n")[2] is False


def test_v2_items_sections_dates_and_skips():
    items, err = MarkdownV2SourceAdapter().parse(DOC.encode())
    assert err is None
    texts = [i["text"] for i in items]
    assert texts == [
        "Prefers concise answers",
        "Verified on 2026-10-01 that dark mode is on",
        "Use ripgrep",
        "Avoid heavy GUI tools",
    ]
    assert items[0]["section"] == "Preferences > Style"
    assert items[2]["section"] == "Preferences > Tools" or items[2]["section"] == "Tools"
    assert items[1]["date"] == "2026-10-01" and "date" not in items[0]
    assert items[0]["doc_meta"] == {"name": "user prefs", "type": "feedback", "description": "how the user likes things"}
    assert not any("not_a_memory" in t or "hidden" in t or "name:" in t for t in texts)


def test_v2_heading_stack_pops_to_sibling():
    items, _ = MarkdownV2SourceAdapter().parse(b"# A\n## B\nx\n## C\ny\n# D\nz\n")
    assert [(i["text"], i["section"]) for i in items] == [("x", "A > B"), ("y", "A > C"), ("z", "D")]


def test_v2_digest_depends_on_text_only_and_duplicates_preserved():
    a, _ = MarkdownV2SourceAdapter().parse(b"# S1\n- same\n# S2\n- same\n")
    assert len(a) == 2 and a[0]["digest"] == a[1]["digest"] and a[0]["section"] != a[1]["section"]


def test_v2_handles_bom_crlf_and_bad_bytes():
    items, err = MarkdownV2SourceAdapter().parse("\ufeff# T\r\n- a\r\n- b\r\n".encode("utf-8"))
    assert err is None and [i["text"] for i in items] == ["a", "b"]
    assert MarkdownV2SourceAdapter().parse(b"\xff\xfe\x00bad")[1] == "unreadable"
    assert MarkdownV2SourceAdapter().parse(b"")[0] == []


def test_v1_behavior_unchanged_by_default():
    # Default parse path still the v1 adapter and the original four names.
    assert parse_recognized("AGENTS.md", b"- x")[1] == "unknown"
    items, _ = MARKDOWN_ADAPTER.parse(b"---\nname: x\n---\n- a\n")
    assert "name: x" in [i["text"] for i in items]  # v1 keeps frontmatter lines (documented gap)


def test_config_names_and_routing():
    cfg = SourceConfig.extended({"NOTES.md"})
    assert EXTENDED_MARKDOWN_NAMES <= cfg.markdown_names and "NOTES.md" in cfg.recognized_names
    items, err = parse_recognized("sub/CLAUDE.md", b"---\nname: n\n---\n# H\n- fact\n", cfg)
    assert err is None and items[0]["text"] == "fact" and items[0]["section"] == "H"
    assert parse_recognized("random.md", b"- x", cfg)[1] == "unknown"
    assert parse_recognized("memory.json", b'["j"]', cfg)[0][0]["text"] == "j"
    custom = SourceConfig(markdown_names=frozenset({"my.md"}), markdown_v2=True)
    assert parse_recognized("my.md", b"# A\n- t", custom)[0][0]["section"] == "A"
    assert parse_recognized("MEMORY.md", b"- t", custom)[1] == "unknown"


def test_discovery_uses_configured_names(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("- a\n", encoding="utf-8")
    (tmp_path / "SOUL.md").write_text("- s\n", encoding="utf-8")
    (tmp_path / "MEMORY.md").write_text("- m\n", encoding="utf-8")
    default = SkillEntrypoint(backend="memory").open("x")
    disc = default.start(root=tmp_path)
    status = {s["path"]: s["status"] for s in disc["sources"]}
    assert status == {"AGENTS.md": "unknown", "MEMORY.md": "recognized", "SOUL.md": "unknown"}
    ext = SkillEntrypoint(backend="memory", sources=SourceConfig.extended()).open("x")
    disc = ext.start(root=tmp_path)
    status = {s["path"]: s["status"] for s in disc["sources"]}
    assert set(status.values()) == {"recognized"}
    assert "AGENTS.md" in disc["discovery"]["supported_sources"]
    assert disc["imported"] is False


def test_import_with_v2_and_redaction_end_to_end(tmp_path: Path):
    email = "x" + "@" + "example.org"
    (tmp_path / "CLAUDE.md").write_text(
        f"---\nname: c\n---\n# Rules\n- mail {email} on 2026-09-30\n- keep tests green\n", encoding="utf-8"
    )
    before = (tmp_path / "CLAUDE.md").read_bytes()
    h = SkillEntrypoint(backend="memory", sources=SourceConfig.extended(), redact=True).open("agent")
    h.start(root=tmp_path)
    preview = h.preview_import(["CLAUDE.md"])
    assert preview["sources"][0]["items"] == 2 and preview["redaction"]["counts"] == {"email": 1}
    res = h.import_selected(["CLAUDE.md"])
    assert len(res["created"]) == 2 and res["rejected"] == []
    dump = str(h.invoke("read_graph", {}))
    assert email not in dump and "name: c" not in dump and "keep tests green" in dump
    assert (tmp_path / "CLAUDE.md").read_bytes() == before
    # idempotent re-import of same snapshot
    again = h.import_selected(["CLAUDE.md"])
    assert again["mechanism_memory_created"] is False and len(again["reused"]) == 2


def test_unreadable_md_rejected_not_aborting(tmp_path: Path):
    (tmp_path / "USER.md").write_bytes(b"\xff\xfe\x00")
    (tmp_path / "SOUL.md").write_text("- ok\n", encoding="utf-8")
    h = SkillEntrypoint(backend="memory", sources=SourceConfig.extended(), redaction=RedactionPolicy.disabled()).open("a")
    h.start(root=tmp_path)
    res = h.import_selected(["USER.md", "SOUL.md"])
    assert [r["path"] for r in res["rejected"]] == ["USER.md"]
    assert len(res["created"]) == 1
