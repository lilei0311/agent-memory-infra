"""Stage 12 explicit historical-memory import."""

from pathlib import Path

import pytest

from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.skill import SkillApi


def test_import_module_does_not_import_store():
    source = Path("src/memory_infra/entrypoint.py").read_text(encoding="utf-8")
    importer = Path("src/memory_infra/importer.py").read_text(encoding="utf-8")
    for text in (source, importer):
        imports = [line.strip() for line in text.splitlines() if line.strip().startswith(("import ", "from "))]
        assert all("memory_infra.store" not in line for line in imports)
    assert "import_selected" in source
    assert "idempotent_by_source_digest" in Path("docs/STAGE12_IMPORT_SEAM.md").read_text(encoding="utf-8")


def test_discovery_alone_creates_no_mechanism_memory(tmp_path: Path):
    (tmp_path / "MEMORY.md").write_text("- keep this\n", encoding="utf-8")
    before = (tmp_path / "MEMORY.md").read_bytes()
    entry = SkillEntrypoint()
    handle = entry.open("agent-a")
    report = handle.start(root=tmp_path)
    assert report["imported"] is False
    assert report["mechanism_memory_created"] is False
    assert report["discovery"]["explicit_import"] == "not_invoked"
    with pytest.raises(RuntimeError):
        handle.import_selected(["MEMORY.md"]) if False else handle.invoke("retrieve", {"query": "keep"})
    api = SkillApi.open_memory()
    assert api.invoke("agent-a", "inspect_trace", {})["result"] == ()
    assert (tmp_path / "MEMORY.md").read_bytes() == before


def test_explicit_import_required_and_creates_owned_objects(tmp_path: Path):
    (tmp_path / "MEMORY.md").write_text("# notes\n- alpha fact\n\n- beta fact\n", encoding="utf-8")
    (tmp_path / "memory.json").write_text('{"memories": ["json fact"]}\n', encoding="utf-8")
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    entry = SkillEntrypoint()
    handle = entry.open("agent-a")
    discovered = handle.start(root=tmp_path)
    assert discovered["imported"] is False
    with pytest.raises(RuntimeError):
        entry.open("agent-a").import_selected(["MEMORY.md"])
    report = handle.import_selected(["MEMORY.md"])
    assert report["explicit_import"] == "invoked"
    assert report["duplicate_policy"] == "idempotent_by_source_digest"
    assert report["mechanism_memory_created"] is True
    assert [item["path"] for item in report["created"]] == ["MEMORY.md", "MEMORY.md"]
    assert len({item["point_id"] for item in report["created"]}) == 2
    assert len({item["event_id"] for item in report["created"]}) == 2
    for item in report["created"]:
        assert item["point_id"] != item["event_id"]
        assert item["source_ref"] == "import:MEMORY.md"
        event = handle.invoke("read_event", {"event_id": item["event_id"]})["result"]
        assert event["source"] == "import:MEMORY.md"
        assert event["evidence_ref"] == item["evidence_ref"]
        assert event["event_id"] == item["event_id"]
    skipped = handle.import_selected(["memory.json"])
    assert skipped["created"][0]["source_ref"] == "import:memory.json"
    for name, payload in before.items():
        assert (tmp_path / name).read_bytes() == payload


def test_repeated_import_is_idempotent(tmp_path: Path):
    (tmp_path / "memory.md").write_text("stable fact\n", encoding="utf-8")
    before = (tmp_path / "memory.md").read_bytes()
    entry = SkillEntrypoint()
    handle = entry.open("agent-a")
    handle.start(root=tmp_path)
    first = handle.import_selected(["memory.md"])
    second = handle.import_selected(["memory.md"])
    assert first["created"][0]["point_id"] == second["reused"][0]["point_id"]
    assert first["created"][0]["event_id"] == second["reused"][0]["event_id"]
    assert first["created"][0]["source_digest"] == second["reused"][0]["source_digest"]
    assert second["created"] == []
    assert second["mechanism_memory_created"] is False
    traced = handle.invoke("inspect_trace", {})["result"]
    kinds = [step["kind"] for step in traced]
    assert kinds.count("point.create") == 1
    assert (tmp_path / "memory.md").read_bytes() == before


def test_changed_source_digest_is_a_new_import(tmp_path: Path):
    path = tmp_path / "MEMORY.md"
    path.write_text("alpha fact\n", encoding="utf-8")
    before = path.read_bytes()
    entry = SkillEntrypoint()
    handle = entry.open("agent-a")
    handle.start(root=tmp_path)
    first = handle.import_selected(["MEMORY.md"])
    path.write_text("alpha fact\nbeta fact\n", encoding="utf-8")
    changed = path.read_bytes()
    assert changed != before
    second = handle.import_selected(["MEMORY.md"])
    assert second["reused"] == []
    assert len(second["created"]) == 2
    assert second["created"][0]["source_digest"] != first["created"][0]["source_digest"]
    assert second["created"][0]["source_ref"] == "import:MEMORY.md"
    assert second["created"][1]["source_ref"] == "import:MEMORY.md"
    created_ids = {item["point_id"] for item in first["created"] + second["created"]}
    assert len(created_ids) == 3
    third = handle.import_selected(["MEMORY.md"])
    assert third["created"] == []
    assert [item["point_id"] for item in third["reused"]] == [item["point_id"] for item in second["created"]]
    assert path.read_bytes() == changed


def test_repeated_identical_lines_are_not_collapsed(tmp_path: Path):
    path = tmp_path / "memory.md"
    path.write_text("same fact\nsame fact\n", encoding="utf-8")
    before = path.read_bytes()
    entry = SkillEntrypoint()
    handle = entry.open("agent-a")
    handle.start(root=tmp_path)
    report = handle.import_selected(["memory.md"])
    assert [item["occurrence"] for item in report["created"]] == [0, 1]
    assert len({item["point_id"] for item in report["created"]}) == 2
    assert len({item["event_id"] for item in report["created"]}) == 2
    assert report["created"][0]["source_digest"] == report["created"][1]["source_digest"]
    for item in report["created"]:
        event = handle.invoke("read_event", {"event_id": item["event_id"]})["result"]
        assert event["observation"] == "same fact"
        assert event["source"] == "import:memory.md"
    repeated = handle.import_selected(["memory.md"])
    assert repeated["created"] == []
    assert len(repeated["reused"]) == 2
    assert path.read_bytes() == before


def test_unknown_and_unreadable_are_rejected(tmp_path: Path):
    (tmp_path / "MEMORY.md").write_text("ok fact\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("nope\n", encoding="utf-8")
    entry = SkillEntrypoint()
    handle = entry.open("agent-a")
    handle.start(
        root=tmp_path,
        artifacts={"secret.json": None, "memory.json": b"{", "other.bin": b"nope"},
    )
    report = handle.import_selected(
        ["notes.txt", "secret.json", "memory.json", "other.bin", "missing.md", "MEMORY.md"]
    )
    reasons = {item["path"]: item["reason"] for item in report["rejected"]}
    assert reasons["notes.txt"] == "unknown"
    assert reasons["secret.json"] == "unreadable"
    assert reasons["memory.json"] == "unreadable"
    assert reasons["other.bin"] == "unknown"
    assert reasons["missing.md"] == "not_in_discovery"
    assert [item["path"] for item in report["created"]] == ["MEMORY.md"]
    assert "nope" not in str(handle.invoke("inspect_trace", {}))


def test_caller_isolation_on_import_handles():
    entry = SkillEntrypoint()
    agent_a = entry.open("agent-a")
    agent_b = entry.open("agent-b")
    agent_a.start(artifacts={"MEMORY.md": b"secret-a"})
    agent_b.start(artifacts={"MEMORY.md": b"secret-b"})
    imported = agent_a.import_selected(["MEMORY.md"])
    assert imported["created"][0]["source_ref"] == "import:MEMORY.md"
    event = agent_a.invoke("read_event", {"event_id": imported["created"][0]["event_id"]})["result"]
    assert event["observation"] == "secret-a"
    other = entry.open("agent-b")
    with pytest.raises(RuntimeError):
        other.import_selected(["MEMORY.md"])
    agent_b_report = agent_b.import_selected(["MEMORY.md"])
    assert agent_b_report["created"][0]["source_ref"] == "import:MEMORY.md"
    b_event = agent_b.invoke("read_event", {"event_id": agent_b_report["created"][0]["event_id"]})["result"]
    assert b_event["observation"] == "secret-b"
    assert agent_a.invoke("read_caller_context", {})["result"]["notes"] == ()
    assert "secret-b" not in str(agent_a.invoke("read_caller_context", {}))
    assert agent_a.invoke("read_caller_context", {})["result"]["attributions"][0]["point_id"] == imported["created"][0]["point_id"]
    assert "secret-a" not in str(agent_b.invoke("read_caller_context", {}))


def test_markdown_source_adapter_is_used_for_md(tmp_path: Path):
    """Regression: Markdown import path uses the internal adapter seam."""
    from memory_infra.source_adapter import MARKDOWN_ADAPTER, MarkdownSourceAdapter
    from memory_infra.importer import parse_recognized

    md = "# title\n- alpha\n\nbeta\n"
    payload = md.encode("utf-8")
    assert MARKDOWN_ADAPTER.can_handle("MEMORY.md")
    assert not MARKDOWN_ADAPTER.can_handle("memory.json")
    items, err = MARKDOWN_ADAPTER.parse(payload)
    assert err is None
    assert [item["text"] for item in items] == ["alpha", "beta"]
    routed, routed_err = parse_recognized("MEMORY.md", payload)
    assert routed_err is None
    assert routed == items
    # JSON still works and does not use the markdown adapter
    json_payload = b'{"memories": ["json item"]}'
    jitems, jerr = parse_recognized("memory.json", json_payload)
    assert jerr is None
    assert jitems[0]["text"] == "json item"
    assert isinstance(MARKDOWN_ADAPTER, MarkdownSourceAdapter)


def test_json_source_adapter_is_used_for_json():
    """JSON import path uses the internal adapter seam and preserves shapes."""
    from memory_infra.source_adapter import JSON_ADAPTER, JsonSourceAdapter
    from memory_infra.importer import parse_recognized

    assert JSON_ADAPTER.can_handle("memories.json")
    assert JSON_ADAPTER.can_handle("memory.json")
    assert not JSON_ADAPTER.can_handle("MEMORY.md")
    assert isinstance(JSON_ADAPTER, JsonSourceAdapter)

    # Representative valid shapes
    cases = [
        (b'["alpha", "beta"]', ["alpha", "beta"]),
        (b'"solo"', ["solo"]),
        (b'{"memories": ["m1", "m2"]}', ["m1", "m2"]),
        (b'{"items": ["i1"]}', ["i1"]),
        (b'{"text": "t"}', ["t"]),
        (b'{"content": "c"}', ["c"]),
        (b'{"memories": [{"text": "ot"}, {"content": "oc"}]}', ["ot", "oc"]),
    ]
    for payload, expected in cases:
        items, err = JSON_ADAPTER.parse(payload)
        assert err is None
        assert [i["text"] for i in items] == expected
        routed, rerr = parse_recognized("memory.json", payload)
        assert rerr is None
        assert routed == items

    # Invalid cases rejected as unreadable
    invalids = [
        b"{",
        b"not json",
        b'{"other": [1]}',
        b'{"memories": [1]}',
        b'{"memories": [{"bad": true}]}',
        b'{"memories": ["", "ok"]}',
        b'\xff',  # invalid utf-8
    ]
    for payload in invalids:
        items, err = JSON_ADAPTER.parse(payload)
        assert items == []
        assert err == "unreadable"
        routed, rerr = parse_recognized("memories.json", payload)
        assert routed == []
        assert rerr == "unreadable"
