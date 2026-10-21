# Install the Skill for a personal Mac agent

This is a local copy or symlink plus an editable install. It is not a marketplace listing, and it does not start an MCP or HTTP server. Cursor, Grok, or another in-process host calls `memory_infra.agent_tools` in the interpreter where this package is installed.

The behavior contract the agent should follow is [`src/memory_infra/SKILL.md`](../src/memory_infra/SKILL.md). Source shapes, scan caps, and the quiescent SQLite copy are [`LOCAL_SOURCES.md`](LOCAL_SOURCES.md). The clone-and-test commands are the README section "Quick start (personal Skill)".

## 1. Editable install

Python 3.11 or newer. From a clean clone:

```bash
git clone https://github.com/lilei0311/agent-memory-infra.git
cd agent-memory-infra
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
python3 -m pytest
```

`pip install -e ".[dev]"` puts `memory_infra` on that interpreter, including `SKILL.md`. If the agent runs a different interpreter, install the package there too. Keep the quotes around `".[dev]"`.

## 2. Point the agent at SKILL.md

After the install, this prints the instruction file the package ships:

```bash
python3 -c "import memory_infra, pathlib; print(pathlib.Path(memory_infra.__file__).resolve().parent / 'SKILL.md')"
```

On a Mac, Cursor reads a personal skill from `~/.cursor/skills/<name>/SKILL.md`. From the clone:

```bash
mkdir -p "$HOME/.cursor/skills/agent-memory"
ln -sfn "$(pwd)/src/memory_infra/SKILL.md" "$HOME/.cursor/skills/agent-memory/SKILL.md"
```

A plain copy works if you would rather not symlink. Copy again after you pull changes to that file. Nothing here publishes the skill.

Grok and other in-process hosts use the same file. Put it where that host reads skill markdown. There is no second package.

## 3. Local store and sources

```python
from memory_infra.agent_tools import AgentMemoryTools, personal_store_path

tools = AgentMemoryTools.open("cursor", store_path=personal_store_path())
```

`personal_store_path()` is `~/.agent-memory-infra/store`, under your home and outside this repo. Do not commit it. A scratch store inside a checkout belongs in `local-memory/` or `.agent-memory-infra/` (both gitignored).

`AgentMemoryTools.open` discovers and imports with `SourceConfig.extended()`: `MEMORY.md`, `memory.md`, `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`, `HEARTBEAT.md`, `CLAUDE.md`, plus `memories.json`, `memory.json`, `*.sqlite`, `*.sqlite3`, and `*.jsonl`. The v2 Markdown parser is on for those files. A basename that is exactly `YYYY-MM-DD.md` stays unrecognized unless you pass `sources=SourceConfig.extended(recognize_dated_markdown=True)`. Item dedup stays off. `SkillEntrypoint()` with no `sources` argument is still the narrow set. Stage and conformance tests keep that default.

Point `discover(root=...)` at a directory outside the repo when the files are real. Use `tests/fixtures/synthetic/` when you want a safe stand-in. Redaction is off unless you pass `redact=True`. Import only with `import_sources(..., consent=True)` for paths you selected. Details are in `SKILL.md`. The OpenClaw freeze rules are the next section.

## 4. Synthetic smoke

From the repo root, with the virtualenv active:

```bash
python3 examples/agent_session.py --select MEMORY.md --consent --signal
```

Expected:

- `discover imported: False`
- `redaction_enabled: False`
- `import created: 6`
- a retrieved line containing `explicit confirmation`
- `outcome: STABLE`
- `sources unchanged: True`

The example store is a temporary directory, not your home directory. Pass `--store ~/.agent-memory-infra/store` only when you want that personal file. Omit `--show-text` when `--root` is a real directory; the command then prints counts and leaves memory text out of the terminal.

## OpenClaw hygiene

Clone, install the Skill, freeze a Markdown copy, discover, import only after consent, then retrieve. This path does not start Hub or MCP.

Freeze Markdown into `$HOME/agent-memory-infra-eval/` (outside this git clone) before `discover`. Copy only the curated notes you intend to import. Do not scan a live multi-gigabyte agent tree, and do not point discovery at a live `~/.openclaw` tree. CI does not touch a live `~/.openclaw` tree.

The personal mechanism store is `~/.agent-memory-infra/store` (`personal_store_path()`), also outside the clone. Leave `redact=False`. Personal import stores text as written.

Tier B SQLite is not part of the default import. If you import an index later, copy it with `sqlite3 .backup` to a file under `$HOME/agent-memory-infra-eval/`, then discover that copy. The live database stays where it is. The snapshot stays outside the repo.

```bash
sqlite3 "$SOURCE_DB" ".backup $HOME/agent-memory-infra-eval/openclaw-agent-snapshot.sqlite"
```

Never commit real memory, session databases, explorer HTML, observation text, or personal paths. A pull request may quote an aggregate count. It does not quote observation text. Scan caps, dated-name flags, and the Tier A checklist are [LOCAL_EVAL.md](LOCAL_EVAL.md).

```python
from pathlib import Path
from memory_infra.agent_tools import AgentMemoryTools, personal_store_path

frozen = Path.home() / "agent-memory-infra-eval" / "openclaw-md-copy"
tools = AgentMemoryTools.open("cursor", store_path=personal_store_path())
found = tools.discover(root=frozen)
chosen = [item["path"] for item in found["sources"] if item["status"] == "recognized"]
tools.preview(chosen)  # dry run
# consent=True only after you confirm this list in this turn
tools.import_sources(chosen, consent=True)
tools.retrieve("the question")
tools.save()
```

## What stays out

No MCP server, Agent Memory Hub, Memory Bridge, vector database, or anonymous telemetry. The public operation list remains [`SKILL_API.md`](SKILL_API.md).
