# Local SQLite and JSONL sources

Read-only source adapters for two file shapes:

- an OpenClaw-shaped SQLite memory index (`*.sqlite`, `*.sqlite3`)
- a JSONL session or memory log (`*.jsonl`, one JSON object per line)

They join discovery and explicit import the same way Markdown and JSON do. `SkillEntrypoint` still refuses `backend="sqlite"`. These adapters do not store mechanism state. They only parse a selected file into observations.

`start` lists recognized paths and does not import them. `import_selected` is the consent step. It does not rewrite, delete, or append to the source file. Redaction stays off unless `redact=True` (or `--redact`). Item dedup stays off unless `item_dedup=ItemDedupPolicy(...)` (or `--dedup`).

Synthetic files live in `tests/fixtures/synthetic/` (`openclaw-agent.sqlite`, `openclaw-agent.sql`, `session.jsonl`, `memory.jsonl`). They are invented notes, not a person's memory, and they contain no secrets. Do not commit a real agent database or session log.

## Point at a local directory

`root` is a directory you choose. Paths in the inventory are relative to that directory, and import refuses a path that escapes it.

From the repo root after the README quick-start install (`pip install -e ".[dev]"`):

```bash
python3 examples/local_source_import.py \
  --root "$HOME/.openclaw/agents/<agentId>" \
  --max-depth 2 \
  --scan-limit 32 \
  --consent \
  --select agent/openclaw-agent.sqlite sessions/<sessionId>.jsonl
```

Without `--consent` the command only prints recognized paths. `--select` limits the import to those relative paths. Omit `--select` and every recognized file in the scan is imported.

The same call from Python:

```python
from pathlib import Path
from memory_infra.entrypoint import SkillEntrypoint

root = Path.home() / ".openclaw" / "agents" / "<agentId>"
handle = SkillEntrypoint().open("local-agent")
discovered = handle.start(root=root, max_depth=2, scan_limit=32)
chosen = [
    item["path"]
    for item in discovered["sources"]
    if item["status"] == "recognized" and item["path"] in {
        "agent/openclaw-agent.sqlite",
        "sessions/<sessionId>.jsonl",
    }
]
handle.import_selected(chosen)
```

Default `max_depth` is 2 and `scan_limit` is 32. An OpenClaw agent directory looks like this:

```text
~/.openclaw/agents/<agentId>/
  agent/openclaw-agent.sqlite
  sessions/<sessionId>.jsonl
```

Point `root` at `<agentId>` and the default depth reaches both. A scan that stops early adds `scan truncated at bound` to the diagnostics. Raise `scan_limit`, or point `root` at a smaller copy that contains only the files you intend to select.

Turn the new suffixes off with `SourceConfig(recognize_sqlite=False, recognize_jsonl=False)`. `SourceConfig.extended()` still recognizes them.

## SQLite snapshot

The adapter reads the file bytes and deserializes them into a private in-memory database with `PRAGMA query_only`. It does not open the path, so it does not create `-wal` or `-shm` sidecars and it does not checkpoint a live database.

That also means a live WAL database can be missing pages that are not in the main file yet. Copy a quiescent snapshot, then point `root` at the copy:

```bash
sqlite3 "$HOME/.openclaw/agents/<agentId>/agent/openclaw-agent.sqlite" \
  ".backup /tmp/openclaw-agent-snapshot.sqlite"
```

`/tmp/openclaw-agent-snapshot.sqlite` stays outside this git repo.

Observations are `memory_index_chunks.text`, ordered by path, start line, then id. Empty text is skipped. The embedding and model columns are not read. Extra columns (importance, triggers, and the rest) are ignored. `memory_index_sources` is provenance (`path`, `source`, `hash`, `mtime`, `size`) and is not a separate memory. A table named `sources` with those columns is used the same way when `memory_index_sources` is absent. A database without `memory_index_chunks` is rejected as unreadable and is not ingested. This matches the chunk table documented for OpenClaw's per-agent database (`openclaw-agent.sqlite`).

## JSONL records

Blank lines are ignored. A malformed line is skipped when the file has another recognized record. A non-empty file with no recognized record is unreadable.

Imported text:

- `message` / `custom_message` content blocks whose type is `text` (or a bare string block)
- a string `summary`, `text`, `content`, or `memory`
- string rows in `memories` or `items`
- a JSON string line

Not imported: a `session` header, `thinking` blocks, tool-call blocks, and extension `custom` state that has no text. Role and record id stay on the parsed item and are not written into the observation text.

## What stays opt-in

Import stores the parsed text as written. Pass `redact=True` on the entrypoint or on `import_selected` / `preview_import` before sharing or writing to a less-trusted store. See [REDACTION.md](REDACTION.md).

Repeated lines stay separate observations until `item_dedup` is set. See [DEDUP.md](DEDUP.md). A repeated import of the same path and the same snapshot bytes still returns the previous records and does not parse them again.
