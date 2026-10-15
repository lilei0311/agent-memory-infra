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

Point `discover(root=...)` at a directory outside the repo when the files are real. Use `tests/fixtures/synthetic/` when you want a safe stand-in. Redaction is off unless you pass `redact=True`. Import only with `import_sources(..., consent=True)` for paths you selected. Details are in `SKILL.md`.

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

## What stays out

No MCP server, Agent Memory Hub, Memory Bridge, vector database, or anonymous telemetry. The public operation list remains [`SKILL_API.md`](SKILL_API.md).
