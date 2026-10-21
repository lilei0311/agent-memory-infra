# Project Status — Agent Memory Infra

Observation date: 2026-10-21. This is a coordination map, not a substitute for issue-level acceptance evidence.

## Current main

HEAD is around the experiment-design commit `a8912d8` ("Draft minimal experiment design for task continuity across topic switches", #62). That commit is `docs/TASK_CONTINUITY_EXPERIMENT.md` only. It does not add a runner and does not change retrieve. Issue #62 stays open. Issue #61 (shared Memory Core / cross-harness adapter RFC) stays open. This path does not implement either one. They are the only open issues in the tracker.

Issue #46 (public Skill API contract) is closed. It is historical. Sections below that still describe #46 as current work are the 2026-10-10 record. The 2026-10-15 triage note already marked that line historical.

Personal usable slices (a)–(e) are on main. The pulls that use those letters are usable(c) #58 (synthetic hit@k and `docs/LOCAL_EVAL.md`), usable(d) #57 (README quick start), and usable(e) #59 (in-process `AgentMemoryTools`, `src/memory_infra/SKILL.md`, `docs/AGENT_INSTALL.md`). No merged pull is titled usable(a) or usable(b). This map does not assign those letters. The slices those pulls sit on are also merged: first-run consent journey (#52), redaction off by default (#54), opt-in item dedup and synthetic fixtures (#55), read-only SQLite and JSONL adapters (#56), local-eval extra and dated markdown flags (#60), Tier A `--hits` aggregate round-trip (#63), and query-text ranking on Skill retrieve (#64).

usable(f), this change: `AgentMemoryTools.open` defaults discovery and import to `SourceConfig.extended()`. Persona markdown names are visible on the personal agent path. `SkillEntrypoint()` with no `sources` argument stays bare `SourceConfig()`. Stage and conformance tests keep that default. Dated `YYYY-MM-DD.md` names and item dedup stay opt-in. OpenClaw import hygiene for a frozen copy under `$HOME/agent-memory-infra-eval/` is the short section in `docs/AGENT_INSTALL.md`.

The recorded Tier A line is unchanged and was not re-scored here: preference=0 prior-decision=0 stale-note=0; recognized=47 created=4630 (2026-10-16, before query ranking). Re-score stays off this repository. Hub, Memory Bridge, MCP, telemetry, and a vector database stay out.

## Immutable product goal
The core hypothesis in README is that historical task feedback should improve what an agent remembers, retrieves, retains, or forgets beyond relevance-only retrieval. Product priority remains Agent Memory Skill for a single agent. Agent Memory Hub, Memory Bridge, telemetry, and external usage learning remain deferred. Storage remains outside this project.

V0.1 A/B/C/D/E, Phase G assets/config/results, V0.2 semantics, and Phase H configuration/results are frozen.

## Stage terminology
The research roadmap stages in `docs/ROADMAP.md` are not the numbered implementation stages. Research Stage 1 is the frozen controlled-policy experiment; research Stage 2 is Skill packaging; research Stage 3 is real-world learning and has not started. Numbered Stages 12–14 are the Skill path: explicit import seam, Memory Graph projection, and read-only visual explorer.

## Current implementation and evidence (historical, 2026-10-10)
- Default-branch HEAD before the Skill API contract commit: `fc443b86feea38fa1216c16f9c34d99c6028067a` (evidence-only Stage 14 Chromium probe record). The contract commit adds `docs/SKILL_API.md`, `tests/test_skill_api_contract.py`, and this map only.
- Stage 14 implementation under review: `e6b97ffb47b3d33fa5f36d18cf01234052741e5e`.
- Exact-SHA evidence: `experiments/results/stage14_issue43_e6b97ff.md`.
- The evidence record reports `PYTHONPATH=src python3 -m pytest -q tests` → 114 passed, exit 0; locked Phase H exit 0, seeds 7/11/19, budget 4, policy none, deterministic replay true, trace SHA-256 `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`; and Chromium input/change checks for views and relation/evidence search.
- Diff from prior implementation `0d02872` to `e6b97ff` includes the Stage 14 source/test fix plus historical evidence/status documents. The recorded run says no V0.1, Phase G, or Phase H configuration/trace artifact changed.

## Stage 14 verdict
**Owner closed Issue #43 as completed and opened Issue #46.** This map does not re-execute Stage 14 checks and does not replace that closure. Prior recorded verdict was conditional until the Chromium probe script and exit code existed; those files are on `fc443b86`.

Source and evidence review supports the search fix, kind-qualified endpoint handling, same-thread thread endpoints, synchronized edge/label/inspector visibility, deterministic rendering, read-only projection boundary, and frozen Phase H result.

The named browser-evidence gap is closed by `experiments/stage14_issue43_chromium_probe.py` and `experiments/results/stage14_issue43_e6b97ff_chromium.md`. The probe ran at implementation SHA `e6b97ffb47b3d33fa5f36d18cf01234052741e5e`: Chromium exit 0, probe assert exit 0. It covers All/Threads/Events/Contradictions, relation id/type, evidence, endpoint-only, no-match, and edge/label/inspector visibility. Pytest and Phase H were not repeated.

## Canonical open work (historical, 2026-10-10)
- Issue #43 was closed completed by the owner on 2026-10-09. This map does not re-open Stage 14 and does not claim a fresh independent execution in this commit.
- Issue #46 is the active work unit: public Skill API contract in `docs/SKILL_API.md`. Contract revision `skill-api-2026-10-10.6`. Pinning tests: `tests/test_skill_api_contract.py` (ops, envelopes, missing fields, invalid signal, exact multi-key scope/ownership suffixes, impersonation-before-ownership, scope-before-graph-write, read_graph write-key suffixes, signal BoundaryError distinct from SnapshotError ownership, entrypoint backend errors, exact lifecycle/relation keys, note-on-any-op, note kept after failed dispatch, ownership rejection does not append note, whitespace caller id, import rejection, rejected import still enables memory). Issue #46 stays open pending independent review.
- Do not create a duplicate Stage 14 issue or a second API-contract issue.

## Next-stage boundary (historical, 2026-10-10)
Issue #46 is design/contract only. Do not implement adapters, packaging, Hub, Memory Bridge, telemetry, UI, server, MCP, GraphRAG, or vector DB under that issue. After the contract is independently accepted, open one implementation issue from the approved contract.

## Triage update (2026-10-15)
- Issue #46 is closed (API contract accepted); the 'stays open pending review' line above is historical.
- Issue #52 acceptance verified locally: `python examples/first_run_journey.py --consent` exits 0 (import 2, graph 6 nodes, 2nd-session retrieval 2, sources unchanged); decline path exits 0 with no import. Suite: `python -m pytest -q tests` -> 163 passed. Note bare `pytest` fails collection (tests.skill_conformance import); use `python -m pytest`.
- Open issues #1-#38 were completed stage/acceptance items at this triage. They are closed. As of 2026-10-21 the only open issues are #61 and #62.

## Phase 2 slice (2026-10-15)
- No open issue named dedup or synthetic fixtures. This slice follows the Stage 12 import seam: source-snapshot idempotency stays the default, and item dedup is opt-in (`docs/DEDUP.md`).
- `MemoryStore.add` does not collapse equal text. `MemoryStore.add_deduped` applies `skip`, `merge`, or `keep_latest`.
- Synthetic fixtures live in `tests/fixtures/synthetic/`. They are invented notes and contain no secrets.
- Import redaction is off by default (`redact=False`), matching main after #54. Opt in with `redact=True` or `--redact`. Item dedup stays opt-in.
- This slice stopped at opt-in item dedup and synthetic fixtures. Read-only SQLite and JSONL source adapters landed in the following section. Synthetic use-case hit@k is the section after the personal quick start.

## Local source adapters (2026-10-15)
- Read-only SQLite (`memory_index_chunks` / `memory_index_sources`) and JSONL adapters are wired through `SourceConfig` and `SkillEntrypoint` discovery plus `import_selected`. `backend="sqlite"` is still rejected.
- Synthetic fixtures: `tests/fixtures/synthetic/openclaw-agent.sqlite`, `session.jsonl`, `memory.jsonl`. No real agent database is in the repo.
- How to point `root` at a local copy, including a quiescent SQLite backup, is `docs/LOCAL_SOURCES.md`. Redaction and item dedup stay opt-in.

## Personal quick start (2026-10-15)
- Clean-clone entry is the README section “Quick start (personal Skill)”: `python3 -m venv .venv`, `python3 -m pip install -e ".[dev]"`, `python3 -m pytest`, `python3 examples/first_run_journey.py --consent`, and `python3 examples/local_source_import.py --consent` on `tests/fixtures/synthetic/`. The editable install exposes `memory_infra`, which is what the examples import.
- `--consent` calls `import_selected`. `--redact` stays off unless passed. Real memory stays outside the repo.
- Agent Memory Hub, Memory Bridge, MCP/HTTP, a vector database, and anonymous telemetry stay out of scope for this path.

## Synthetic use-case eval (2026-10-15)

- `experiments/synthetic_usecase_eval.py` scores hit@k on synthetic tasks (preference recall, prior decision, duplicate suppression, stale/contradiction) for cosine baseline vs adaptive utility, and records what Skill API `retrieve` returns (`policy="none"` vs `automatic`).
- Results: `experiments/results/usable_c_synthetic_eval.md` (synthetic labels only). Adaptive is not required to beat baseline.
- Local dry-run playbook: `docs/LOCAL_EVAL.md`. Real memory stays outside the repo. Redaction remains off by default.

## Local hit@k gate (2026-10-16)

- Synthetic hit@k is already in `experiments/results/usable_c_synthetic_eval.md` (invented labels). Adaptive is not required to beat baseline.
- Local hand-score procedure: after a Tier A import, record `preference`, `prior-decision`, and `stale-note` as 0 or 1 with `experiments/synthetic_usecase_eval.py --local-root ... --output ... --hits ...`. The steps are `docs/LOCAL_EVAL.md`. The command writes the aggregate markdown and a sibling JSON outside the repository. A pull request may quote that one aggregate line. The aggregate holds counts and those 0/1 scores. Observation text stays out of the aggregate and out of the pull request.
- Query-aware Skill `retrieve` has landed. A non-empty query ranks by bag-of-words cosine (`query_relevance`) against observation text, using the existing cosine helper. `policy="none"` orders by `query_relevance`, then recency, then earlier candidates. `policy="automatic"` uses `attention_weight + query_relevance + 0.01 * recency + 0.01 * contextual_fit` when the query is non-empty, and the previous attention formula when the query is empty. `query_used_for_ranking=true` is on the retrieve result and the retrieval trace when that ranking runs. An empty query with `policy="none"` stays recency order. The V0.1 cosine-plus-utility policy-layer table is unchanged.
- Local hit@k (Tier A, 2026-10-16): preference=0 prior-decision=0 stale-note=0; recognized=47 created=4630. That line was scored before query ranking, when `policy="none"` filled the budget with the earliest ids. Re-score stays on the Mac. This file does not invent a new hit line.

## Agent Skill packaging (2026-10-15)
- In-process tools: `memory_infra.agent_tools.AgentMemoryTools` maps discover, preview, import, retrieve, and record_outcome onto `start`, `preview_import`, `import_selected`, `invoke("retrieve")`, and `invoke("signal")`. No MCP server.
- Instruction file: `src/memory_infra/SKILL.md`. Personal Mac install (editable install, copy or link into `~/.cursor/skills/agent-memory/SKILL.md`, store at `~/.agent-memory-infra/store`) is `docs/AGENT_INSTALL.md`.
- Scripted session: `examples/agent_session.py` and `tests/test_agent_session.py` import a synthetic `MEMORY.md`, retrieve, and optionally signal. Import runs only when consent is exactly true. Redaction stays off unless requested.
- This slice does not reopen the synthetic eval above and does not add a marketplace package or an MCP/HTTP service.
- usable(f): `AgentMemoryTools.open` defaults to `SourceConfig.extended()` (persona markdown names and the v2 parser). `SkillEntrypoint()` stays on bare `SourceConfig()`. Dated markdown names and item dedup stay opt-in. Hygiene for a frozen OpenClaw markdown copy is in `docs/AGENT_INSTALL.md`.
