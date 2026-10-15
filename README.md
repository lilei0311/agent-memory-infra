# Agent Memory Infrastructure
> A research infrastructure for building adaptive memory systems for AI agents.

## Quick start (personal Skill)

This path is the in-process Agent Memory Skill on your own machine. It discovers local files, imports only what you select, and retrieves through the memory policy. Agent Memory Hub, Memory Bridge, an MCP or HTTP server, a vector database, and anonymous telemetry are out of scope here.

Python 3.11 or newer. From a clean clone:

```bash
git clone https://github.com/lilei0311/agent-memory-infra.git
cd agent-memory-infra
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
python3 -m pytest
python3 examples/first_run_journey.py --consent
python3 examples/local_source_import.py --consent
```

Run these from the repository root with the virtualenv active. `pip install -e ".[dev]"` installs `memory_infra` from `src/` (setuptools package discovery in `pyproject.toml`) and installs pytest. The examples import that installed package. Keep the quotes around `".[dev]"` so the shell does not treat the brackets as a glob.

`python3 -m pytest` is the suite command. It collects `tests/` with the repo root on the path, which `from tests.skill_conformance import ...` needs. CI runs the same install, then `python -m pytest -q tests` and `python examples/first_run_journey.py --consent`.

The first-run script builds its own temporary `MEMORY.md` and `memory.json`. It does not read your home directory and it does not commit anything. `local_source_import.py` defaults to the synthetic fixtures in `tests/fixtures/synthetic/`.

### What you should see

`python3 examples/first_run_journey.py --consent` exits 0 and prints:

- discovery `imported: False` (discovery never imports)
- recognized sources `MEMORY.md` and `memory.json`
- graph nodes before the import decision: `0`
- explicit consent imports both recognized paths
- explicit import created: `2`
- graph nodes after: `6`
- explorer contains the read-only marker: `True`
- second session retrieval selected: `2`
- both source files unchanged: `True`

Omit `--consent` and the same script skips import, leaves the graph at `0` nodes, and skips second-session retrieval. Source files stay unchanged either way.

`python3 examples/local_source_import.py --consent` exits 0. The recognized set is `MEMORY.md`, `memories.json`, `memory.jsonl`, `openclaw-agent.sqlite`, and `session.jsonl` (print order follows the directory walk). It then prints `created: 20`, `skipped: 0`, `redaction_enabled: False`, `item_dedup_enabled: False`, and `sources unchanged`. `store_items.json` and `openclaw-agent.sql` sit in the same folder for other tests and are not in that recognized set.

### Consent, redaction, fixtures

Discovery (`start`) lists sources and stops there. Import runs when you pass `--consent`, which calls `import_selected` on the recognized paths. `--select PATH ...` keeps a subset of those recognized paths. Declining leaves source files and memory unchanged.

`--redact` is off by default. Personal import stores text as written. Pass `--redact` when you are preparing a shareable export or writing into a less-trusted store. Counts in the redaction report never include the matched secret. Details: [Redaction](docs/REDACTION.md).

Synthetic fixtures under `tests/fixtures/synthetic/` are invented notes. They are the safe stand-in for Markdown, JSON, SQLite, and JSONL shapes. Do not commit real memory, session databases, or explorer HTML from a real import. Point `--root` at a directory outside this repo when you want to read a local copy. Item dedup is also off unless you opt in (`--dedup`, or `examples/dedup_import.py`). See [Local sources](docs/LOCAL_SOURCES.md) and [Dedup](docs/DEDUP.md).

## Overview
Most Agent memory systems focus on **storing** and **retrieving** information.
This project focuses on a different question:
> **Can an Agent learn from its past experience to decide what should be remembered, retrieved, retained, or forgotten?**
The goal is to build a lightweight, agent-agnostic **Memory Policy Layer** that can work across different Agents and different memory storage implementations.
The memory storage does not belong to this project.
The project focuses on the **policy and feedback loop above the storage layer**.
---
## Core Hypothesis
Traditional memory retrieval often looks like:
```text
User Task
   ↓
Semantic Search
   ↓
Top-K Memories
   ↓
Agent
```
We propose an adaptive approach:
```text
                         ┌──────────────┐
                         │ Historical    │
                         │ Experience    │
                         └───────┬───────┘
                                 ↓
Task → Candidate Memories → Memory Policy
                                 ↓
                              Top-K
                                 ↓
                               Agent
                                 ↓
                              Outcome
                                 ↓
                              Trace
                                 ↓
                         Policy Update
                                 │
                                 └──────────→ next task
```
The system continuously learns which memories are actually useful.

────────

## Product Architecture

The project has two related but independently installable product directions:

1. **Agent Memory Skill** — a memory-management capability installed inside a single Agent/Harness.
2. **Agent Memory Hub** — a standalone application that discovers and aggregates memories from multiple Agents/Harnesses.

They share a common memory model and public integration boundary, but they are not required to be installed together.

The first product is the current priority. The second is a later product track.

See [Product Architecture](docs/PRODUCT_ARCHITECTURE.md) for the detailed boundary and evolution plan.

```text
                 Agent Memory Ecosystem
                         │
             ┌───────────┤           ├───────────┐
             │                       │
             ▼                       ▼
      Agent Memory Skill       Agent Memory Hub
        Single Agent             Multi Agent
             │                       │
       Own memory/policy       Discovery/Aggregation
             │                       │
             └───────────┬───────────┘
                         ▼
               Common Memory Contract
```

────────

## First-run journey

`examples/first_run_journey.py` is the minimal single-Agent Skill path: discovery, explicit `--consent` / `--select`, read-only graph, and a second session loaded through the file-backend packaging handoff. The [quick start](#quick-start-personal-skill) is the command to run, including the expected line counts. `--redact` stays off unless you pass it. See the script and `tests/test_first_run_journey.py`.

────────

## Local SQLite and JSONL sources

Discovery also recognizes `*.sqlite`, `*.sqlite3`, and `*.jsonl`. Import stays explicit, does not rewrite the file, and leaves redaction and item dedup off unless you opt in.

After the quick-start install, scan a directory outside this repo with:

```bash
python3 examples/local_source_import.py --root /path/to/local/copy --consent --select agent/openclaw-agent.sqlite
```

The default root is `tests/fixtures/synthetic/`. See [Local sources](docs/LOCAL_SOURCES.md).

────────

## Design Principles

1. Storage-Agnostic

Agents may store memories as:

* Markdown
* JSON
* SQL
* Vector databases
* Knowledge graphs
* Agent-specific memory systems
* Other custom formats

The Memory Policy Layer should not depend on any particular storage technology.

2. Agent-Agnostic

The same memory policy should be usable by different Agents.

The Agent only needs to provide a minimal adapter interface.

Agent
  ↓
Memory Adapter
  ↓
Memory Policy
  ↓
Memory Store

This allows the system to become a reusable Skill rather than a memory implementation tied to one Agent.

3. Feedback Driven

A memory should not become important simply because it is semantically similar to the current task.

Its historical usefulness should also matter.

For example:

Memory A
similarity = 0.82
historical usefulness = high
Memory B
similarity = 0.90
historical usefulness = low

The policy may decide that Memory A is more valuable.

4. Outcome-Oriented

The system should evaluate memory based on what happened after it was retrieved.

Possible signals include:

* task success
* user feedback
* correction rate
* execution efficiency
* repeated reuse
* whether the Agent ignored the memory
* whether the memory caused an incorrect decision

The goal is not simply to measure whether a memory was retrieved.

The goal is to measure whether the memory helped.

────────

## Memory Lifecycle

The long-term goal is to learn four related policies:

                 ┌─────────────┐
                 │ Memory Policy│
                 └──────┬──────┘
                        │
          ┌────────────┤───────────┐
          ↓             ↓             ↓
       Write        Retrieve       Retain
          │             │             │
          └───────────┤───────────┘
                        ↓
                     Forget

Write Policy

Should this information become a memory?

Retrieval Policy

Should this memory be retrieved for the current task?

Retention Policy

Should this memory remain important over time?

Forgetting Policy

Should this memory be downgraded, archived, or removed?

────────

## Historical Memory and Memory Graph

The long-term Agent Memory Skill is not limited to discovering old memory files.

The intended progression is:

```text
Existing Agent Memory
        ↓
Discovery
        ↓
Explicit / controlled structuring
        ↓
New Memory Structure
        ├── Event Instance
        ├── Event Thread
        ├── Relations
        ├── Evidence
        ├── Context
        └── Dynamic State
        ↓
Memory Graph
        ↓
Visual Memory Explorer
```

The Memory Graph represents the project's memory semantics. It is not a requirement to adopt a particular graph database.

The graph should support visual inspection of relationships, timelines, evidence/source provenance, memory state, and retrieval/use history.

Discovery must not silently rewrite or migrate user memory. Historical-memory import or structuring is an explicit later capability.

────────

## V0.1

The first version deliberately avoids:

* Large Language Models
* Vector databases
* Complex reinforcement learning
* Distributed infrastructure

Instead, V0.1 uses a simple and explainable policy.

The first experiment compares:

Baseline

retrieval_score = semantic_relevance

with:

Adaptive Policy

retrieval_score =
    relevance
    + historical_utility
    + reliability
    + context_fit

The weights are updated using historical task outcomes.

────────

## Trace

Every memory interaction should generate a lightweight trace.

Example:

{
  "task_id": "task_001",
  "memory_id": "memory_123",
  "retrieved": true,
  "used": true,
  "task_success": true,
  "user_feedback": 1
}

The trace should describe the interaction and outcome, rather than requiring storage of the user’s raw conversation.

This allows the system to evaluate whether the memory policy is actually improving performance.

────────

## Evaluation

The primary research question is:

Does historical feedback improve memory retrieval compared with relevance-only retrieval?

Initial metrics may include:

* Task success rate
* Memory usefulness
* Retrieval precision
* Retrieval waste
* User correction rate
* Repeat usefulness
* Policy convergence

The first experiment should run controlled simulations before connecting to real Agents.

────────

## Agent Skill

Once the Memory Policy is validated, it will be packaged as an Agent Skill.

The Skill will provide Agents with a standard method to:

1. Inspect available memory
2. Select relevant memories
3. Record memory usage
4. Report task outcome
5. Update memory utility

Different Agents can therefore use different memory stores while sharing the same policy methodology.

              Memory Policy Skill
                       │
        ┌────────────┤────────────┐
        ↓              ↓              ↓
     Agent A         Agent B        Agent C
        │              │              │
    Store A         Store B        Store C

────────

## Agent Memory Hub

The multi-Agent product is a later, standalone application.

Its first role is discovery and aggregation, not immediate shared-memory synchronization:

```text
Agent Discovery
      ↓
Memory Discovery
      ↓
Memory Aggregation
      ↓
Unified Search / Unified Graph
      ↓
Cross-Agent Relationship Discovery
      ↓
Memory Bridge
      ↓
Controlled Cross-Agent Sharing
```

The Hub may interoperate with an already-installed Agent Memory Skill through the common public boundary, while still representing heterogeneous legacy memory sources.

────────

## Privacy

The project should not require users to upload or expose their raw memories.

Where possible, the evaluation layer should operate on:

* memory identifiers
* abstract features
* retrieval events
* outcome signals
* aggregated statistics

The actual memory content should remain inside the user’s Agent environment.

────────

## Research Roadmap

The personal path you can run today is the [quick start](#quick-start-personal-skill): local Skill, explicit import, synthetic fixtures. Checked items below are in `main`. Unchecked items are still open or explicitly deferred.

Phase 1 — Policy Prototype (research Stage 1, frozen)

* [x] Define memory protocol
* [x] Define adapter interface
* [x] Implement baseline retrieval
* [x] Implement adaptive scoring
* [x] Implement trace format
* [x] Implement online policy update
* [x] Build simulation

Phase 2 — Evaluation

* [x] Compare baseline vs adaptive policy (controlled experiments under `experiments/`)
* [x] Run controlled experiments (V0.1 and later frozen Phase G/H runs)
* [ ] Analyze learning curves beyond the recorded windows (deferred to research Stage 3; needs real usage data)
* [x] Identify an initial feedback-signal contract ([evaluation signals](docs/EVALUATION_SIGNAL_CONTRACT.md)); expansion past that contract is still follow-up
* [x] Test controlled memory distributions in the simulator (noise and feedback-rate matrix in `experiments/stage1_robustness.py`)

Phase 3 — Agent Skill

* [x] Define the Skill specification ([Skill API](docs/SKILL_API.md))
* [x] Build the file store backend and source adapters for Markdown, JSON, read-only SQLite, and JSONL (`backend="sqlite"` remains rejected; SQLite here is a source file, not the mechanism store)
* [ ] Package a drop-in Skill for an external agent host (the editable install and in-process `SkillEntrypoint` are the supported entry)
* [x] Exercise two in-process Agent shapes on the memory and file backends (`tests/test_stage2_heterogeneous_integrations.py`)
* [ ] Collect anonymous evaluation signals (deferred with telemetry)

Phase 4 — Real-World Learning (deferred)

* [ ] Real Agent integration beyond the in-process Skill
* [ ] User feedback loop on a live agent
* [ ] Policy versioning
* [ ] Cross-Agent evaluation
* [ ] Continuous policy improvement

Product tracks:

* Personal Agent Memory Skill (current): discovery → explicit import → Memory Graph → read-only visual inspection → policy retrieval. Start at the quick start.
* Agent Memory Hub (deferred): Agent discovery → memory aggregation → unified graph/search → later Memory Bridge.

Hub, Memory Bridge, MCP/HTTP, a vector database, and anonymous telemetry are out of scope for the personal Skill path.

────────

## Long-Term Vision

The long-term goal is not to build another vector database or another memory store.

It is to build a learning layer for Agent memory.

                 Agent Memory Infrastructure
                         ┌─────────┐
                         │ Agents  │
                         └────┬────┘
                              ↓
                     ┌───────────────┐
                     │ Memory Policy  │
                     │     Layer      │
                     └───────┬────────┘
                             ↓
                  ┌────────────────────┐
                  │ Memory Adapter API │
                  └─────────┬──────────┘
                            ↓
              ┌────────────┤───────────┐
              ↓             ↓             ↓
          Markdown        Vector         SQL
          Memory          Store         Store

The central idea is simple:

Memory should not only store experience.
Memory should learn from experience.

────────

## Status

Research / experimental.

The supported entry is the personal in-process Skill in the [quick start](#quick-start-personal-skill). Research Stage 1 (controlled policy experiments) is frozen. Explicit import, the Skill API, opt-in redaction, opt-in item dedup, synthetic fixtures, and read-only SQLite/JSONL source adapters are on `main`. The Hub remains a later product track.

## Stage 1 Design

Stage 1 remains the controlled-simulation record of the Memory Policy Layer. The in-process Skill sits on top of that layer. Anonymous telemetry has not started.

- [Architecture](docs/ARCHITECTURE.md)
- [Product Architecture](docs/PRODUCT_ARCHITECTURE.md)
- [Protocols](docs/PROTOCOLS.md)
- [Experiment Plan](docs/EXPERIMENT_PLAN.md)
- [Roadmap](docs/ROADMAP.md)
- [Project status](docs/PROJECT_STATUS.md)
