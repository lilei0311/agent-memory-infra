"""Read-only SQLite and JSONL source adapters.

Fixtures under tests/fixtures/synthetic are invented. They are not user memory
and contain no secrets. Import must not rewrite them.
"""

import hashlib
import sqlite3
from pathlib import Path

from memory_infra.dedup import ItemDedupPolicy
from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.importer import parse_recognized
from memory_infra.source_adapter import (
    JSONL_ADAPTER,
    SQLITE_ADAPTER,
    SourceConfig,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "synthetic"
SQLITE_NAME = "openclaw-agent.sqlite"
PREFERENCE = "The workspace prefers explicit confirmation before import."
SQLITE_TEXTS = [
    PREFERENCE,
    "the workspace prefers explicit confirmation before import.",
    "SQLite fixture: the index is read and never rewritten.",
    "Unique sqlite fact: fixtures are checked in on purpose.",
    "Session chunk: standup notes live in the team channel.",
]
SESSION_TEXTS = [
    PREFERENCE,
    "JSONL fixture: one object per line, imported only after selection.",
    "Compaction summary: confirm before import.",
]
MEMORY_JSONL_TEXTS = [
    "Plain memory line: fixtures are invented and contain no secrets.",
    "Content field: confirm before import.",
    "Memory field: the source file stays on disk.",
    "List field: one string item.",
]


def _snapshot(root: Path) -> dict[str, bytes]:
    return {path.name: path.read_bytes() for path in root.iterdir() if path.is_file()}


def _open(root: Path, **kwargs):
    handle = SkillEntrypoint(backend="memory", **kwargs).open("local-agent")
    note = handle.start(root=root)
    return handle, note


def test_sqlite_fixture_reads_chunk_text_and_provenance():
    payload = (FIXTURES / SQLITE_NAME).read_bytes()
    before = payload
    items, err = SQLITE_ADAPTER.parse(payload)
    assert err is None
    assert [item["text"] for item in items] == SQLITE_TEXTS
    assert items[0]["section"] == "MEMORY.md"
    assert items[0]["origin"] == "memory"
    assert items[0]["chunk_id"] == "c1"
    assert items[0]["start_line"] == 1
    assert items[0]["end_line"] == 1
    assert items[0]["index_source"] == {
        "path": "MEMORY.md",
        "table": "memory_index_sources",
        "source": "memory",
        "hash": "mem-hash",
        "mtime": 1700000000,
        "size": 120,
    }
    unique = items[3]
    assert unique["section"] == "notes/extra.md"
    assert "index_source" not in unique
    session = items[4]
    assert session["origin"] == "sessions"
    assert session["index_source"]["hash"] == "ses-hash"
    assert session["index_source"]["table"] == "memory_index_sources"
    blob = "\n".join(item["text"] for item in items)
    assert "synthetic-embedder" not in blob
    assert "[]" not in blob
    assert (FIXTURES / SQLITE_NAME).read_bytes() == before
    assert SQLITE_ADAPTER.can_handle("agent/openclaw-agent.sqlite")
    assert SQLITE_ADAPTER.can_handle("notes.SQLITE3")
    assert not SQLITE_ADAPTER.can_handle("MEMORY.md")


def test_committed_sqlite_matches_sql_fixture():
    sql = (FIXTURES / "openclaw-agent.sql").read_text(encoding="utf-8")
    conn = sqlite3.connect(":memory:")
    conn.executescript(sql)
    payload = conn.serialize()
    conn.close()
    rebuilt, rebuilt_err = SQLITE_ADAPTER.parse(payload)
    committed, committed_err = SQLITE_ADAPTER.parse((FIXTURES / SQLITE_NAME).read_bytes())
    assert rebuilt_err is None and committed_err is None
    assert rebuilt == committed


def test_sqlite_tolerates_extra_columns_and_skips_embeddings(tmp_path: Path):
    path = tmp_path / "extra.sqlite"
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE memory_index_chunks (
          id TEXT PRIMARY KEY,
          path TEXT,
          source TEXT,
          start_line INTEGER,
          end_line INTEGER,
          hash TEXT,
          model TEXT,
          text TEXT,
          embedding BLOB,
          updated_at INTEGER,
          importance INTEGER,
          triggers TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO memory_index_chunks (
          id, path, source, start_line, end_line, hash, model, text, embedding, updated_at, importance, triggers
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "x1",
            "MEMORY.md",
            "memory",
            1,
            1,
            "h",
            "MODEL-MARKER",
            "Extra column chunk stays text.",
            b"EMBED-MARKER-BYTES",
            10,
            3,
            "curated",
        ),
    )
    conn.commit()
    conn.close()
    before = path.read_bytes()
    items, err = SQLITE_ADAPTER.parse(before)
    assert err is None
    assert [item["text"] for item in items] == ["Extra column chunk stays text."]
    assert "MODEL-MARKER" not in str(items)
    assert b"EMBED-MARKER-BYTES" not in str(items).encode()
    assert path.read_bytes() == before
    assert not (tmp_path / "extra.sqlite-wal").exists()
    assert not (tmp_path / "extra.sqlite-shm").exists()


def test_sources_alias_is_provenance_and_chunks_are_required(tmp_path: Path):
    alias = tmp_path / "alias.sqlite"
    conn = sqlite3.connect(alias)
    conn.executescript(
        """
        CREATE TABLE sources (
          path TEXT,
          source TEXT,
          hash TEXT,
          mtime INTEGER,
          size INTEGER
        );
        CREATE TABLE memory_index_chunks (
          id TEXT PRIMARY KEY,
          path TEXT,
          text TEXT
        );
        INSERT INTO sources VALUES ('notes.md', 'memory', 'alias-hash', 5, 9);
        INSERT INTO memory_index_chunks VALUES ('a', 'notes.md', 'Alias provenance attaches.');
        """
    )
    conn.commit()
    conn.close()
    items, err = SQLITE_ADAPTER.parse(alias.read_bytes())
    assert err is None
    assert items[0]["text"] == "Alias provenance attaches."
    assert items[0]["index_source"]["table"] == "sources"
    assert items[0]["index_source"]["hash"] == "alias-hash"

    empty = tmp_path / "empty.sqlite"
    empty_conn = sqlite3.connect(empty)
    empty_conn.execute(
        "CREATE TABLE memory_index_chunks (id TEXT PRIMARY KEY, text TEXT)"
    )
    empty_conn.commit()
    empty_conn.close()
    no_rows, no_err = SQLITE_ADAPTER.parse(empty.read_bytes())
    assert no_err is None and no_rows == []

    missing = tmp_path / "missing.sqlite"
    missing_conn = sqlite3.connect(missing)
    missing_conn.execute("CREATE TABLE sources (path TEXT, text TEXT)")
    missing_conn.execute("INSERT INTO sources VALUES ('a', 'not a chunk')")
    missing_conn.commit()
    missing_conn.close()
    rejected, reason = SQLITE_ADAPTER.parse(missing.read_bytes())
    assert rejected == [] and reason == "unreadable"
    assert SQLITE_ADAPTER.parse(b"not a database") == ([], "unreadable")


def test_jsonl_session_and_memory_logs():
    session, err = JSONL_ADAPTER.parse((FIXTURES / "session.jsonl").read_bytes())
    assert err is None
    assert [item["text"] for item in session] == SESSION_TEXTS
    assert session[0]["role"] == "user" and session[0]["record_id"] == "m1"
    assert session[1]["role"] == "assistant"
    assert session[2]["record_type"] == "compaction"
    assert "role" not in session[2]
    joined = "\n".join(item["text"] for item in session)
    assert "not an observation" not in joined
    assert "hidden reasoning" not in joined
    memory, memory_err = JSONL_ADAPTER.parse((FIXTURES / "memory.jsonl").read_bytes())
    assert memory_err is None
    assert [item["text"] for item in memory] == MEMORY_JSONL_TEXTS
    assert JSONL_ADAPTER.can_handle("sessions/demo.JSONL")
    assert not JSONL_ADAPTER.can_handle("memory.json")
    header, header_err = JSONL_ADAPTER.parse(
        b'{"type":"session","id":"only","cwd":"/tmp/synthetic"}\n'
    )
    assert header_err is None and header == []
    assert JSONL_ADAPTER.parse(b"") == ([], None)
    assert JSONL_ADAPTER.parse(b'{"foo": 1}\n') == ([], "unreadable")
    assert JSONL_ADAPTER.parse(b"\xff") == ([], "unreadable")
    bom, bom_err = JSONL_ADAPTER.parse('\ufeff{"text":"bom line"}\r\n'.encode("utf-8"))
    assert bom_err is None and bom[0]["text"] == "bom line"


def test_legacy_parse_without_config_ignores_new_suffixes():
    sqlite_payload = (FIXTURES / SQLITE_NAME).read_bytes()
    jsonl_payload = (FIXTURES / "session.jsonl").read_bytes()
    assert parse_recognized(SQLITE_NAME, sqlite_payload) == ([], "unknown")
    assert parse_recognized("session.jsonl", jsonl_payload) == ([], "unknown")
    routed, err = parse_recognized(SQLITE_NAME, sqlite_payload, SourceConfig())
    assert err is None and [item["text"] for item in routed] == SQLITE_TEXTS
    lines, line_err = parse_recognized("nested/session.jsonl", jsonl_payload, SourceConfig())
    assert line_err is None and [item["text"] for item in lines] == SESSION_TEXTS
    off = SourceConfig(recognize_sqlite=False, recognize_jsonl=False)
    assert off.recognized_names == frozenset(
        {"MEMORY.md", "memory.md", "memories.json", "memory.json"}
    )
    assert parse_recognized(SQLITE_NAME, sqlite_payload, off)[1] == "unknown"


def test_discovery_lists_suffixes_and_does_not_import():
    before = _snapshot(FIXTURES)
    handle, note = _open(FIXTURES)
    assert note["imported"] is False
    assert note["mechanism_memory_created"] is False
    assert "discovery" in note["sequence"] and "import" not in note["sequence"]
    kinds = {item["path"]: (item["kind"], item["status"]) for item in note["sources"]}
    assert kinds[SQLITE_NAME] == ("sqlite_memory", "recognized")
    assert kinds["session.jsonl"] == ("jsonl_memory", "recognized")
    assert kinds["memory.jsonl"] == ("jsonl_memory", "recognized")
    assert kinds["MEMORY.md"][1] == "recognized"
    assert kinds["store_items.json"] == ("unknown", "unknown")
    assert kinds["openclaw-agent.sql"] == ("unknown", "unknown")
    assert "*.sqlite" in note["discovery"]["supported_sources"]
    assert "*.jsonl" in note["discovery"]["supported_sources"]
    assert _snapshot(FIXTURES) == before
    extended = SkillEntrypoint(backend="memory", sources=SourceConfig.extended()).open("ext")
    extended_note = extended.start(root=FIXTURES)
    extended_kinds = {item["path"]: item["status"] for item in extended_note["sources"]}
    assert extended_kinds[SQLITE_NAME] == "recognized"
    assert extended_kinds["session.jsonl"] == "recognized"


def test_import_is_explicit_and_does_not_rewrite_sources():
    before = _snapshot(FIXTURES)
    handle, _note = _open(FIXTURES)
    preview = handle.preview_import([SQLITE_NAME, "session.jsonl"])
    assert preview["dry_run"] is True
    assert preview["mechanism_memory_created"] is False
    assert preview["redaction"]["enabled"] is False
    assert preview["item_dedup"]["enabled"] is False
    assert [row["items"] for row in preview["sources"]] == [len(SQLITE_TEXTS), len(SESSION_TEXTS)]
    assert "memory" not in preview["sequence"]

    report = handle.import_selected(["session.jsonl"])
    assert report["redaction"]["enabled"] is False
    assert report["redaction"]["counts"] == {}
    assert report["item_dedup"]["enabled"] is False
    assert report["skipped"] == [] and report["merged"] == []
    assert [item["path"] for item in report["created"]] == ["session.jsonl"] * len(SESSION_TEXTS)
    observations = [
        handle.invoke("read_event", {"event_id": item["event_id"]})["result"]["observation"]
        for item in report["created"]
    ]
    assert observations == SESSION_TEXTS
    assert report["created"][0]["source_ref"] == "import:session.jsonl"
    graph = str(handle.invoke("read_graph", {}))
    assert "JSONL fixture" in graph
    assert "SQLite fixture" not in graph
    assert _snapshot(FIXTURES) == before
    assert not any(name.endswith(("-wal", "-shm")) for name in _snapshot(FIXTURES))


def test_sqlite_import_keeps_distinct_lines_until_dedup_is_on():
    before = _snapshot(FIXTURES)
    handle, _note = _open(FIXTURES)
    report = handle.import_selected([SQLITE_NAME])
    assert report["item_dedup"]["enabled"] is False
    assert len(report["created"]) == len(SQLITE_TEXTS)
    assert report["skipped"] == []
    assert len({item["point_id"] for item in report["created"]}) == len(SQLITE_TEXTS)
    digest = hashlib.sha256(before[SQLITE_NAME]).hexdigest()
    assert report["created"][0]["source_digest"] == digest
    assert _snapshot(FIXTURES) == before

    deduped, _ignored = _open(FIXTURES, item_dedup=ItemDedupPolicy("skip"))
    collapsed = deduped.import_selected([SQLITE_NAME, "MEMORY.md"])
    assert collapsed["redaction"]["enabled"] is False
    assert len(collapsed["created"]) == 6
    assert len(collapsed["skipped"]) == 5
    assert _snapshot(FIXTURES) == before


def test_redaction_stays_off_unless_opt_in(tmp_path: Path):
    address = "person" + "@" + "example.org"
    path = tmp_path / "memory.sqlite"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE memory_index_chunks (id TEXT PRIMARY KEY, text TEXT)")
    conn.execute(
        "INSERT INTO memory_index_chunks VALUES (?, ?)",
        ("e1", f"contact {address}"),
    )
    conn.commit()
    conn.close()
    before = path.read_bytes()
    plain, _note = _open(tmp_path)
    plain_report = plain.import_selected(["memory.sqlite"])
    assert plain_report["redaction"]["enabled"] is False
    assert address in str(plain.invoke("read_graph", {}))
    assert "[REDACTED:" not in str(plain.invoke("read_graph", {}))
    assert path.read_bytes() == before

    redacted, _ignored = _open(tmp_path, redact=True)
    redacted_report = redacted.import_selected(["memory.sqlite"])
    assert redacted_report["redaction"]["enabled"] is True
    assert redacted_report["redaction"]["counts"] == {"email": 1}
    dumped = str(redacted.invoke("read_graph", {}))
    assert address not in dumped
    assert "[REDACTED:email]" in dumped
    assert path.read_bytes() == before


def test_unreadable_sqlite_and_opt_out_are_not_ingested(tmp_path: Path):
    (tmp_path / "notes.sqlite").write_bytes(b"not-a-database")
    (tmp_path / "session.jsonl").write_text('{"text":"keep this line"}\n', encoding="utf-8")
    before = _snapshot(tmp_path)
    handle, note = _open(tmp_path)
    statuses = {item["path"]: item["status"] for item in note["sources"]}
    assert statuses["notes.sqlite"] == "recognized"
    report = handle.import_selected(["notes.sqlite", "session.jsonl"])
    assert report["created"][0]["path"] == "session.jsonl"
    assert report["rejected"] == [{"path": "notes.sqlite", "status": "rejected", "reason": "unreadable"}]
    assert _snapshot(tmp_path) == before

    opted_out = SkillEntrypoint(
        backend="memory",
        sources=SourceConfig(recognize_sqlite=False, recognize_jsonl=False),
    ).open("local-agent")
    opted_note = opted_out.start(root=tmp_path)
    opted_status = {item["path"]: item["status"] for item in opted_note["sources"]}
    assert opted_status["notes.sqlite"] == "unknown"
    assert opted_status["session.jsonl"] == "unknown"
    rejected = opted_out.import_selected(["session.jsonl"])
    assert rejected["created"] == []
    assert rejected["rejected"][0]["reason"] == "unknown"


def test_artifacts_snapshot_imports_without_a_root_file():
    sqlite_payload = (FIXTURES / SQLITE_NAME).read_bytes()
    jsonl_payload = (FIXTURES / "memory.jsonl").read_bytes()
    handle = SkillEntrypoint(backend="memory").open("local-agent")
    note = handle.start(
        artifacts={
            "agent/openclaw-agent.sqlite": sqlite_payload,
            "sessions/memory.jsonl": jsonl_payload,
        }
    )
    assert note["imported"] is False
    report = handle.import_selected(["agent/openclaw-agent.sqlite"])
    assert len(report["created"]) == len(SQLITE_TEXTS)
    assert report["created"][0]["source_ref"] == "import:agent/openclaw-agent.sqlite"
    assert "List field" not in str(handle.invoke("read_graph", {}))


def test_example_consent_and_select(tmp_path: Path):
    import importlib.util

    for name in (SQLITE_NAME, "session.jsonl", "memory.jsonl"):
        target = tmp_path / name
        target.write_bytes((FIXTURES / name).read_bytes())
    path = Path(__file__).resolve().parents[1] / "examples" / "local_source_import.py"
    spec = importlib.util.spec_from_file_location("local_source_import_example", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    declined = module.run(tmp_path, consent=False)
    assert declined["import_report"] is None
    assert declined["discovery"]["imported"] is False
    assert SQLITE_NAME in declined["recognized"]

    selected = module.run(tmp_path, consent=True, select=["memory.jsonl"])
    assert selected["import_report"]["redaction"]["enabled"] is False
    assert selected["import_report"]["item_dedup"]["enabled"] is False
    assert len(selected["import_report"]["created"]) == len(MEMORY_JSONL_TEXTS)
    assert {item["path"] for item in selected["import_report"]["created"]} == {"memory.jsonl"}
    assert _snapshot(tmp_path) == {name: (FIXTURES / name).read_bytes() for name in (SQLITE_NAME, "session.jsonl", "memory.jsonl")}
