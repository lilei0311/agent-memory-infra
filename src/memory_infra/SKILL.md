# Agent Memory Skill

In-process memory for one agent. This is not an MCP server, HTTP service, marketplace plugin, or agent SDK.

Call `memory_infra.agent_tools`. Do not open caller databases yourself and do not import `memory_infra.store`. The tool module does not import `memory_infra.store`. It calls `SkillEntrypoint` and the public Skill API only.

Install and the Mac copy/link path: `docs/AGENT_INSTALL.md`. Prove the package with the README section "Quick start (personal Skill)". Source shapes and caps: `docs/LOCAL_SOURCES.md`.

## When to call what

1. `discover` first. That is `handle.start`: bounded read-only discovery. Unknown and unreadable sources do not abort. Discovery does not import.
2. Show the user the recognized paths. `preview` is `preview_import`: a dry run with counts. It writes nothing.
3. `import_sources(..., consent=True)` is `import_selected`. Call it only after the user confirms those paths in this turn. It imports only that list and does not rewrite caller files.
4. `retrieve` answers a task. It is `invoke("retrieve")`, then `read_event` for each selected id, so you get observation text without walking internal objects. A non-empty query ranks observation text by bag-of-words overlap. An empty query keeps recency order when policy is `none`.
5. `record_outcome` is optional and comes after you use a memory. It is `invoke("signal")` with an allowed signal name and that signal's fields.
6. `read_graph` is `invoke("read_graph")`. It is a read-only projection of mechanism-owned objects. It does not create graph state. Do not dump the whole graph into the prompt.
7. `save` / `load` are `invoke("save")` / `invoke("load")`. Call `save` before the process exits when `store_path` is set. Snapshots hold mechanism state, not caller notes.

`enable_memory` stays inside the tools that need it (`retrieve`, `read_graph`, `save`, `load`, and `import_selected`). Do not call it before discovery. `discover` and `preview` do not enable memory.

If you call `SkillEntrypoint` yourself, the same order holds: `open(caller_id)`, then `start`, then `enable_memory`, then `invoke`. Historical import is still only `import_selected` after discovery.

## Consent

Never auto-import. Discovery is not consent. Installation does not ingest files into mechanism state.

- Pass `consent=True` only for paths the user named in this turn. A truthy string is not consent.
- Omitting consent leaves source files and mechanism memory unchanged.
- Do not import a path that was absent from this handle's discovery.
- A second `open` cannot read another handle's inventory.

## Store path

Personal file backend: `personal_store_path()` → `~/.agent-memory-infra/store`.

That directory is under the user home and outside this git repo. Pass it as `store_path=` to `AgentMemoryTools.open`. Do not commit the store, imported sources, explorer HTML, or traces.

If a scratch store must sit inside a clone, use `local-memory/` or `.agent-memory-infra/`. Both are gitignored. Real memory stays outside the public repo. Point `root` at a directory you choose, not at a committed personal copy. Synthetic stand-ins live in `tests/fixtures/synthetic/`.

`AgentMemoryTools.open` recognizes `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`, `HEARTBEAT.md`, and `CLAUDE.md` in addition to `MEMORY.md` and `memory.md`. A basename that is exactly `YYYY-MM-DD.md` stays unrecognized. Do not scan a live agent tree. Freeze Markdown under `$HOME/agent-memory-infra-eval/` first. Tier B SQLite, if imported at all, is a `sqlite3 .backup` copy in that same outside directory. `redact=False` for personal use. Never commit what you imported. The checklist is `docs/AGENT_INSTALL.md`.

## Redaction

Off by default. Personal import stores text as written.

Pass `redact=True` only when sharing or writing to a less-trusted store. Counts in a redaction report never include the matched secret. See `docs/REDACTION.md`.

Item dedup is also off unless you construct `SkillEntrypoint` with `item_dedup`. The agent tools do not turn it on.

## caller_id

Use one non-empty stable id per agent install, such as `cursor` or `grok`. Do not put another caller's id in a payload. Empty ids are rejected.

## Tool mapping

```python
from memory_infra.agent_tools import AgentMemoryTools, personal_store_path

tools = AgentMemoryTools.open("cursor", store_path=personal_store_path())
found = tools.discover(root="/path/outside/this/repo")
chosen = ["MEMORY.md"]  # only paths the user confirmed
preview = tools.preview(chosen)  # dry run; stop here unless they said yes
if user_confirmed_these_paths:
    tools.import_sources(chosen, consent=True)
found_memories = tools.retrieve("the task question")
if found_memories["memories"]:
    tools.record_outcome(
        "consolidate",
        event_id=found_memories["memories"][0]["event_id"],
        evidence="used on this task",
    )
tools.save()
```

| Tool | Skill API | Rule |
| --- | --- | --- |
| `discover` | `handle.start` | read-only; never imports |
| `preview` | `handle.preview_import` | dry run; writes nothing |
| `import_sources(..., consent=True)` | `handle.import_selected` | explicit paths only |
| `retrieve` | `invoke("retrieve")` then `read_event` | returns observation text |
| `record_outcome` | `invoke("signal")` | allowed signal names only |
| `read_graph` | `invoke("read_graph")` | read-only projection |
| `save` / `load` | `invoke("save")` / `invoke("load")` | mechanism snapshot |

`record_outcome` must not invent `user_feedback`, `task_success`, or `used`. A missing outcome stays unknown. Allowed signal names and their fields are in `docs/SKILL_API.md`. `consolidate` needs `event_id` and `evidence`.

## Scripted check

From the repo root after the editable install, on synthetic fixtures only:

```bash
python3 examples/agent_session.py --select MEMORY.md --consent --signal
```

You should see discovery `imported: False`, `redaction_enabled: False`, import created `6`, a retrieved line about explicit confirmation, outcome `STABLE`, and sources unchanged. The example store is a temporary directory unless you pass `--store`.

## Out of scope

No MCP, Agent Memory Hub, Memory Bridge, vector database, or anonymous telemetry.
