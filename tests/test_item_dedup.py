"""Item dedup on MemoryStore and explicit import.

Fixtures in tests/fixtures/synthetic are invented. They are not user memory.
"""

import json
from pathlib import Path

import pytest

from memory_infra.dedup import ItemDedupPolicy, item_key, normalize_text
from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.memory import MemoryItem, MemoryStore
from memory_infra.redaction import RedactionPolicy

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "synthetic"
PREFERENCE = "The workspace prefers explicit confirmation before import."
STANDUP = "Standup notes live in the team channel."
UNIQUE = "Unique markdown fact: fixtures are checked in on purpose."
JSON_ONLY = "JSON-only reminder: review the dry-run report before import."


def test_near_key_folds_case_and_whitespace_not_punctuation():
    assert normalize_text("  The  Workspace\t") == "the workspace"
    assert item_key("The  Workspace", near=True) == item_key("the workspace", near=True)
    assert item_key("The  Workspace", near=False) != item_key("the workspace", near=False)
    assert item_key("Hello", near=True) != item_key("Hello!", near=True)
    with pytest.raises(ValueError):
        ItemDedupPolicy(mode="replace")
    with pytest.raises(TypeError):
        ItemDedupPolicy(near="yes")  # type: ignore[arg-type]


def _store_items() -> list[MemoryItem]:
    rows = json.loads((FIXTURES / "store_items.json").read_text(encoding="utf-8"))
    return [
        MemoryItem(
            row["id"],
            row["text"],
            list(row["embedding"]),
            tags=list(row["tags"]),
            success=row["success"],
            failure=row["failure"],
        )
        for row in rows
    ]


def test_store_add_keeps_same_text_under_different_ids():
    store = MemoryStore()
    items = _store_items()
    store.add(items[0])
    store.add(MemoryItem(items[1].id, items[0].text, [0.5, 0.5]))
    assert set(store.items) == {"pref-1", "pref-2"}


def test_store_skip_merge_and_keep_latest_from_fixture():
    items = _store_items()
    skipped = MemoryStore()
    first = skipped.add_deduped(items[0], ItemDedupPolicy("skip"))
    second = skipped.add_deduped(items[1], ItemDedupPolicy("skip"))
    third = skipped.add_deduped(items[2], ItemDedupPolicy("skip"))
    assert first.action == "added" and second.action == "skipped" and third.action == "added"
    assert second.item.id == "pref-1"
    assert skipped.get("pref-1").tags == ["preference"]
    assert skipped.get("pref-1").success == 2
    assert "pref-2" not in skipped.items

    merged = MemoryStore()
    merged.add_deduped(items[0], ItemDedupPolicy("merge"))
    merged.add_deduped(items[1], ItemDedupPolicy("merge"))
    kept = merged.get("pref-1")
    assert kept.text == PREFERENCE
    assert kept.embedding == [1.0, 0.0]
    assert kept.tags == ["preference", "confirm"]
    assert (kept.success, kept.failure) == (3, 1)

    latest = MemoryStore()
    latest.add_deduped(items[0], ItemDedupPolicy("keep_latest"))
    replaced = latest.add_deduped(items[1], ItemDedupPolicy("keep_latest"))
    assert replaced.action == "kept_latest" and replaced.item.id == "pref-1"
    assert latest.get("pref-1").text == items[1].text
    assert latest.get("pref-1").embedding == [0.2, 0.8]
    assert latest.get("pref-1").tags == ["confirm"]
    assert (latest.get("pref-1").success, latest.get("pref-1").failure) == (1, 1)
    again = latest.add_deduped(items[1], ItemDedupPolicy("keep_latest"))
    assert again.action == "skipped"

    exact = MemoryStore()
    exact.add_deduped(items[0], ItemDedupPolicy("skip", near=False))
    other = exact.add_deduped(items[1], ItemDedupPolicy("skip", near=False))
    assert other.action == "added" and set(exact.items) == {"pref-1", "pref-2"}

    clash = MemoryStore()
    clash.add_deduped(items[0])
    with pytest.raises(ValueError):
        clash.add_deduped(MemoryItem("pref-1", "a different synthetic fact", [0.0]))


def _open(root: Path, dedup: ItemDedupPolicy | None):
    handle = SkillEntrypoint(backend="memory", item_dedup=dedup).open("fixture-agent")
    handle.start(root=root)
    return handle


def test_default_import_does_not_collapse_fixture_lines():
    before = {path.name: path.read_bytes() for path in FIXTURES.iterdir()}
    handle = _open(FIXTURES, None)
    report = handle.import_selected(["MEMORY.md"])
    assert report["item_dedup"] == {"enabled": False, "mode": None, "near": None, "equality": None}
    assert report["duplicate_policy"] == "idempotent_by_source_digest"
    assert report["redaction"]["enabled"] is True
    assert report["skipped"] == [] and report["merged"] == [] and report["superseded"] == []
    assert len(report["created"]) == 6
    assert len({item["point_id"] for item in report["created"]}) == 6
    assert {path.name: path.read_bytes() for path in FIXTURES.iterdir()} == before


def test_import_skip_collapses_near_duplicates_across_files():
    handle = _open(FIXTURES, ItemDedupPolicy("skip"))
    preview = handle.preview_import(["MEMORY.md", "memories.json"])
    assert preview["dry_run"] is True and preview["mechanism_memory_created"] is False
    assert preview["item_dedup"]["equality"] == "normalized_text"
    assert [row["would_create"] for row in preview["sources"]] == [3, 1]
    assert [row["would_skip"] for row in preview["sources"]] == [3, 1]
    assert "memory" not in preview["sequence"]
    with pytest.raises(RuntimeError):
        handle.invoke("read_graph", {})

    report = handle.import_selected(["MEMORY.md", "memories.json"])
    assert report["redaction"]["enabled"] is True
    assert len(report["created"]) == 4
    assert len(report["skipped"]) == 4
    assert report["merged"] == [] and report["superseded"] == []
    observations = []
    for item in report["created"]:
        event = handle.invoke("read_event", {"event_id": item["event_id"]})["result"]
        observations.append(event["observation"])
    assert observations == [PREFERENCE, STANDUP, UNIQUE, JSON_ONLY]
    kinds = [step["kind"] for step in handle.invoke("inspect_trace", {})["result"]]
    assert kinds.count("point.create") == 4
    repeated = handle.import_selected(["MEMORY.md", "memories.json"])
    assert repeated["created"] == []
    assert [item["point_id"] for item in repeated["reused"]] == [item["point_id"] for item in report["created"]]
    assert repeated["skipped"] == []


def test_import_skip_on_changed_snapshot_keeps_known_lines(tmp_path: Path):
    source = tmp_path / "MEMORY.md"
    source.write_bytes((FIXTURES / "MEMORY.md").read_bytes())
    handle = _open(tmp_path, ItemDedupPolicy("skip"))
    first = handle.import_selected(["MEMORY.md"])
    source.write_text(source.read_text(encoding="utf-8") + "A brand new synthetic line.\n", encoding="utf-8")
    second = handle.import_selected(["MEMORY.md"])
    assert [item["occurrence"] for item in second["created"]] == [6]
    assert len(second["skipped"]) == 6
    assert {item["point_id"] for item in second["skipped"]} == {item["point_id"] for item in first["created"]}
    event = handle.invoke("read_event", {"event_id": second["created"][0]["event_id"]})["result"]
    assert event["observation"] == "A brand new synthetic line."


def test_import_merge_keeps_first_text_and_records_provenance():
    handle = _open(FIXTURES, ItemDedupPolicy("merge"))
    report = handle.import_selected(["MEMORY.md"])
    assert len(report["created"]) == 3 and len(report["merged"]) == 3
    preference = report["created"][0]
    assert preference["also_seen"] == [
        {"path": "MEMORY.md", "occurrence": 1, "source_digest": preference["source_digest"], "text_equal": False},
        {"path": "MEMORY.md", "occurrence": 2, "source_digest": preference["source_digest"], "text_equal": False},
    ]
    event = handle.invoke("read_event", {"event_id": preference["event_id"]})["result"]
    assert event["observation"] == PREFERENCE
    assert report["merged"][0]["point_id"] == preference["point_id"]
    assert report["merged"][0]["text_equal"] is False
    standup = next(item for item in report["created"] if item["occurrence"] == 3)
    assert standup["also_seen"][0]["text_equal"] is True
    assert len(handle.invoke("read_graph", {})["result"]["nodes"]) > 0
    kinds = [step["kind"] for step in handle.invoke("inspect_trace", {})["result"]]
    assert kinds.count("point.create") == 3


def test_import_keep_latest_supersedes_without_deleting():
    handle = _open(FIXTURES, ItemDedupPolicy("keep_latest"))
    report = handle.import_selected(["MEMORY.md"])
    assert len(report["superseded"]) == 2
    assert len(report["skipped"]) == 1
    assert report["skipped"][0]["text_equal"] is True
    active = [item for item in report["created"] if item.get("dedup_action") == "kept_latest"]
    assert active[-1]["supersedes"] == report["superseded"][-1]["point_id"]
    latest = handle.invoke("read_event", {"event_id": active[-1]["event_id"]})["result"]
    assert latest["observation"] == "The  workspace prefers explicit confirmation before import."
    first = handle.invoke("read_event", {"event_id": report["superseded"][0]["event_id"]})["result"]
    assert first["observation"] == PREFERENCE
    exact = _open(FIXTURES, ItemDedupPolicy("keep_latest", near=False))
    exact_report = exact.import_selected(["MEMORY.md"])
    assert len(exact_report["created"]) == 5
    assert len(exact_report["skipped"]) == 1
    assert exact_report["superseded"] == []


def test_dedup_sees_redacted_text_and_opt_out_still_stores_raw(tmp_path: Path):
    left = "someone" + "@" + "example.org"
    right = "other" + "@" + "example.org"
    secret = "sk-" + "a1B2c3D4e5F6g7H8i9J0"
    source = tmp_path / "MEMORY.md"
    source.write_text(f"- contact {left}\n- contact {right}\n- plain fact\n", encoding="utf-8")
    handle = _open(tmp_path, ItemDedupPolicy("skip"))
    report = handle.import_selected(["MEMORY.md"])
    assert report["redaction"]["enabled"] is True
    assert report["redaction"]["counts"] == {"email": 2}
    assert len(report["created"]) == 2 and len(report["skipped"]) == 1
    dump = str(handle.invoke("read_graph", {}))
    assert left not in dump and right not in dump and secret not in dump
    assert "[REDACTED:email]" in dump

    raw = SkillEntrypoint(
        backend="memory",
        item_dedup=ItemDedupPolicy("skip"),
        redaction=RedactionPolicy.disabled(),
    ).open("fixture-agent")
    raw.start(root=tmp_path)
    raw_report = raw.import_selected(["MEMORY.md"])
    assert raw_report["redaction"]["enabled"] is False
    assert len(raw_report["created"]) == 3 and raw_report["skipped"] == []
    assert left in str(raw.invoke("read_graph", {}))


def test_fixtures_have_no_secret_shaped_tokens():
    blob = "\n".join(path.read_text(encoding="utf-8") for path in FIXTURES.iterdir() if path.is_file())
    for marker in ("sk-", "AKIA", "ghp_", "xoxb-", "BEGIN ", "password", "@", "/Users/", "/home/"):
        assert marker not in blob


def test_example_skip_import_matches_policy():
    import importlib.util

    path = Path(__file__).resolve().parents[1] / "examples" / "dedup_import.py"
    spec = importlib.util.spec_from_file_location("dedup_import_example", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.run("skip")
    assert report["item_dedup"]["mode"] == "skip"
    assert len(report["created"]) == 4
    assert len(report["skipped"]) == 4
    assert report["redaction"]["enabled"] is True
