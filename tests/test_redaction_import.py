"""Redaction at import: unit behavior, dry-run report, and import integration.

Secret-shaped strings are assembled at runtime so no realistic token literal
lives in the repository.
"""

from pathlib import Path

import pytest

from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.importer import parse_redacted
from memory_infra.redaction import (
    ALL_CATEGORIES,
    RedactionPolicy,
    redact_items,
    redact_text,
)

SK = "sk-" + "a1B2c3D4e5F6g7H8i9J0"
GH = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
AKIA = "AKIA" + "ABCDEFGHIJKLMNOP"
EMAIL = "someone" + "@" + "example.org"
PHONE = "138" + "00138000"
HOME = "/Users/" + "alice" + "/project"
BEARER = "Bearer " + "abcdefghijklmnopqrstuvwxyz0123456789"


def test_each_category_is_redacted_and_values_vanish():
    text = " | ".join([SK, GH, AKIA, EMAIL, PHONE, HOME, BEARER, "password=" + "Zx9Zx9Zx9Zx9Zx9Zx9"])
    out, counts = redact_text(text)
    for raw in (SK, GH, AKIA, EMAIL, PHONE, "alice", BEARER, "Zx9Zx9Zx9Zx9Zx9Zx9"):
        assert raw not in out
    assert counts == {
        "aws_access_key": 1,
        "github_token": 1,
        "api_key": 1,
        "bearer_token": 1,
        "credential_assignment": 1,
        "email": 1,
        "cn_phone": 1,
        "home_path": 1,
    }
    assert "password=[REDACTED:credential_assignment]" in out
    assert "/[REDACTED:home_path]/project" in out


def test_redaction_is_idempotent_and_deterministic():
    text = f"note {SK} and {EMAIL}"
    once, c1 = redact_text(text)
    twice, c2 = redact_text(once)
    assert once == redact_text(text)[0]
    assert twice == once
    assert c2 == {}


def test_clean_text_untouched():
    text = "prefers dark mode; meeting on 2026-10-15 at 10:30"
    assert redact_text(text) == (text, {})


def test_policy_only_and_disabled_and_unknown():
    text = f"{EMAIL} {PHONE}"
    out, counts = redact_text(text, RedactionPolicy.only("email"))
    assert PHONE in out and EMAIL not in out and counts == {"email": 1}
    assert redact_text(text, RedactionPolicy.disabled()) == (text, {})
    with pytest.raises(ValueError):
        RedactionPolicy.only("nope")
    assert set(ALL_CATEGORIES) >= {"email", "api_key", "home_path"}


def test_redact_items_recomputes_digest_and_keeps_order():
    import hashlib

    items = [{"text": "clean", "digest": "d0"}, {"text": f"key {SK}", "digest": "d1"}]
    out, report = redact_items(items)
    assert [i["text"] for i in out][0] == "clean"
    assert out[0]["digest"] == "d0" and "redacted" not in out[0]
    assert out[1]["redacted"] is True
    assert out[1]["digest"] == hashlib.sha256(out[1]["text"].encode()).hexdigest()
    assert report.as_dict() == {"items_total": 2, "items_redacted": 1, "counts": {"api_key": 1}}


def _source(tmp_path: Path) -> Path:
    src = tmp_path / "src"
    src.mkdir()
    (src / "MEMORY.md").write_text(
        f"# Notes\n- plain fact\n- contact {EMAIL}\n- deploy key {SK}\n", encoding="utf-8"
    )
    return src


def test_parse_redacted_default_keeps_text():
    items, err, report = parse_redacted("MEMORY.md", f"- contact {EMAIL}\n".encode())
    assert err is None
    assert EMAIL in items[0]["text"]
    assert report.items_redacted == 0


def test_preview_default_is_dry_run_without_redaction(tmp_path: Path):
    src = _source(tmp_path)
    before = (src / "MEMORY.md").read_bytes()
    handle = SkillEntrypoint(backend="memory").open("a")
    handle.start(root=src)
    report = handle.preview_import(["MEMORY.md"])
    assert report["dry_run"] is True and report["imported"] is False
    assert report["mechanism_memory_created"] is False
    assert report["redaction"]["enabled"] is False
    assert report["redaction"]["counts"] == {}
    assert report["redaction"]["items_redacted"] == 0
    assert report["sources"][0]["status"] == "would_import"
    assert report["sources"][0]["items"] == 3
    flat = str(report)
    assert SK not in flat and EMAIL not in flat
    assert "memory" not in report["sequence"]
    assert (src / "MEMORY.md").read_bytes() == before
    with pytest.raises(RuntimeError):
        handle.invoke("read_graph", {})


def test_preview_opt_in_reports_counts_only(tmp_path: Path):
    src = _source(tmp_path)
    before = (src / "MEMORY.md").read_bytes()
    handle = SkillEntrypoint(backend="memory").open("a")
    handle.start(root=src)
    report = handle.preview_import(["MEMORY.md"], redact=True)
    assert report["dry_run"] is True and report["imported"] is False
    assert report["mechanism_memory_created"] is False
    assert report["redaction"]["enabled"] is True
    assert report["redaction"]["counts"] == {"api_key": 1, "email": 1}
    assert report["sources"][0]["status"] == "would_import"
    assert report["sources"][0]["items"] == 3
    flat = str(report)
    assert SK not in flat and EMAIL not in flat
    assert "memory" not in report["sequence"]
    assert (src / "MEMORY.md").read_bytes() == before
    with pytest.raises(RuntimeError):
        handle.invoke("read_graph", {})


def test_preview_reports_rejections(tmp_path: Path):
    src = _source(tmp_path)
    handle = SkillEntrypoint(backend="memory").open("a")
    handle.start(root=src)
    report = handle.preview_import(["missing.md"])
    assert report["sources"][0]["reason"] == "not_in_discovery"
    opted = handle.preview_import(["missing.md"], redact=True)
    assert opted["sources"][0]["reason"] == "not_in_discovery"
    assert opted["redaction"]["enabled"] is True


def test_default_import_leaves_secret_like_strings_intact(tmp_path: Path):
    src = _source(tmp_path)
    handle = SkillEntrypoint(backend="memory").open("a")
    handle.start(root=src)
    result = handle.import_selected(["MEMORY.md"])
    assert result["redaction"]["enabled"] is False
    assert result["redaction"]["items_redacted"] == 0
    assert result["redaction"]["counts"] == {}
    assert len(result["created"]) == 3
    dump = str(handle.invoke("read_graph", {}))
    assert SK in dump and EMAIL in dump
    assert "[REDACTED:" not in dump


def test_constructor_redact_flag_stores_only_redacted_text(tmp_path: Path):
    src = _source(tmp_path)
    handle = SkillEntrypoint(backend="memory", redact=True).open("a")
    handle.start(root=src)
    preview = handle.preview_import(["MEMORY.md"])
    assert preview["redaction"]["enabled"] is True
    assert preview["redaction"]["counts"] == {"api_key": 1, "email": 1}
    result = handle.import_selected(["MEMORY.md"])
    assert result["redaction"]["enabled"] is True
    assert result["redaction"]["counts"] == {"api_key": 1, "email": 1}
    assert len(result["created"]) == 3
    dump = str(handle.invoke("read_graph", {})) + str(result)
    assert SK not in dump and EMAIL not in dump
    assert "[REDACTED:api_key]" in dump


def test_import_call_redact_flag_stores_only_redacted_text(tmp_path: Path):
    src = _source(tmp_path)
    handle = SkillEntrypoint(backend="memory").open("a")
    handle.start(root=src)
    result = handle.import_selected(["MEMORY.md"], redact=True)
    assert result["redaction"]["enabled"] is True
    assert result["redaction"]["counts"] == {"api_key": 1, "email": 1}
    dump = str(handle.invoke("read_graph", {}))
    assert SK not in dump and EMAIL not in dump
    assert "[REDACTED:email]" in dump


def test_narrow_policy_is_opt_in_and_disabled_policy_matches_default(tmp_path: Path):
    src = _source(tmp_path)
    narrow = SkillEntrypoint(backend="memory", redaction=RedactionPolicy.only("email")).open("a")
    narrow.start(root=src)
    narrowed = narrow.import_selected(["MEMORY.md"])
    assert narrowed["redaction"]["enabled"] is True
    assert narrowed["redaction"]["counts"] == {"email": 1}
    graph = str(narrow.invoke("read_graph", {}))
    assert EMAIL not in graph and SK in graph

    explicit_off = SkillEntrypoint(backend="memory", redaction=RedactionPolicy.disabled()).open("a")
    explicit_off.start(root=src)
    result = explicit_off.import_selected(["MEMORY.md"])
    assert result["redaction"]["enabled"] is False
    assert result["redaction"]["items_redacted"] == 0
    assert EMAIL in str(explicit_off.invoke("read_graph", {}))
    with pytest.raises(ValueError):
        SkillEntrypoint(redact=True, redaction=RedactionPolicy.disabled())
