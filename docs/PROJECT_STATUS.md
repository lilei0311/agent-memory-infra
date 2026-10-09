# Project status map

Observation date: 2026-10-09. This file is a coordination map, not an acceptance verdict.

Default-branch HEAD at this commit's parent: `8564d18b24fa1e886838ab93cc084b8bbde7ed9a` (evidence-only).

## Immutable product goal

Core hypothesis (`README.md`): historical task feedback should improve what an agent remembers, retrieves, retains, or forgets, beyond relevance-only retrieval.

Product priority: Agent Memory Skill (single agent). Agent Memory Hub and Memory Bridge are deferred. Storage stays outside this project. V0.1 A/B/C/D/E parameters, results, and acceptance criteria are frozen. V0.2 transition semantics and locked Phase H configuration are frozen.

## Stage numbers are not the research phases

`docs/ROADMAP.md` research stages are not the numbered implementation stages:

| Research roadmap | Meaning | Relation to numbered stages |
| --- | --- | --- |
| Stage 1 | Validate memory policy in controlled simulation | V0.1 A/B/C/D/E. Frozen. Not Stage 14. |
| Stage 2 | Package as a Skill | Numbered Stages 2 and 6–11 are packaging seams, not this research stage. |
| Stage 3 | Real-world learning | Not started. Telemetry and external usage stay out. |

Numbered Stages 12–14 are the Skill path in `docs/PRODUCT_ARCHITECTURE.md`: explicit import seam, Memory Graph projection, read-only visual explorer. They are not policy-learning acceptance.

## SHA split for Stage 14

| Role | SHA | What changed |
| --- | --- | --- |
| Latest implementation under test | `0d0287207b94288cb10543df223fb90dd561dad6` | Issue #44 search match on relation id, relation type, and evidence text. Files: `src/memory_infra/explorer.py`, `tests/test_stage14_explorer.py`, `docs/STAGE14_VISUAL_EXPLORER.md`. |
| Evidence-only child | `707d33b972744b646f88f4b1fe28a14f86fdc6fb` | Records the Issue #44 run at `0d02872`. Not the executed tree. |
| Evidence-only HEAD | `8564d18b24fa1e886838ab93cc084b8bbde7ed9a` | Records the Issue #43 run at `0d02872`. Not the executed tree. |
| Prior implementation | `670e4d2a0457823d2206cdd57a873e383c01ccd9` | Issue #42 inspector visibility bound to edge visibility. Superseded for search scope by `0d02872`. |

Do not treat `8564d18` as the code-under-test.

## Stage 14 position

Status: **CONDITIONAL, not PASS**.

Implemented, not independently accepted: read-only explorer; kind-qualified contradiction endpoints (Issue #40); `referential.same_thread` thread endpoints (Issue #41); inspector visibility tracks edge visibility (Issue #42); All-view search can keep an in-view edge when the query matches relation id, type, or evidence text (Issue #44).

Recorded evidence, not re-executed for this status commit:

- `experiments/results/stage14_visual_explorer.md` records pytest, locked Phase H, and Chromium input/change dispatch at `0d02872` (Issue #43 record in commit `8564d18`, Issue #44 record in commit `707d33b`).
- Locked Phase H configuration cited by those records: seeds 7, 11, 19; budget 4; policy none; historical trace SHA-256 `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
- This status commit does not claim a new pytest, Phase H, or browser run.

Issue #44 remains open: the fix commit exists; independent acceptance has not closed it.
Issue #43 remains open and is the independent Stage 14 acceptance gate. Its body still names older HEAD `b36aabb1823f7e2e197d8eacc3b79261469ee56c`; the current baseline is implementation `0d02872` and evidence HEAD `8564d18`.
Issues #39–#42 remain open. They are the prior acceptance and defect chain. Open state is not proof the later fix is missing.

Exit condition for Stage 14: an independent acceptance run at implementation SHA `0d02872` (not an evidence-only HEAD) satisfies the Issue #43 checklist, including relation/evidence search, kind-qualified endpoints, inspector/label visibility, read-only `read_graph`, unchanged Phase H digest, and untouched V0.1 / Phase G artifacts. Only that gate may mark PASS. This map does not.

## Single next action

Owner: Issue #43.

Action: independently accept or fail Stage 14 at implementation SHA `0d0287207b94288cb10543df223fb90dd561dad6`, using the recorded `0d02872` evidence only as a baseline. Do not open a duplicate Stage 14 implementation issue. Do not start a next product stage from this map.

## Numbered stage crosswalk

Acceptance below is not re-decided here. Open issues are left open.

| Stage | Status used here | Notes |
| --- | --- | --- |
| V0.1 policy experiments | FROZEN | A/B/C/D/E. Do not retune or rewrite results. |
| V0.2 / Phase H dynamics | FROZEN config | Locked seeds 7/11/19, budget 4, policy none. |
| 2–13 product seams | IMPLEMENTED IN TREE / NOT RE-ACCEPTED HERE | Specs exist under `docs/STAGE2_` through `docs/STAGE13_`. Matching issues remain open. Do not mass-close from this map. |
| 14 visual explorer | CONDITIONAL | Implementation `0d02872`. Gate: Issue #43. |
| Hub / Memory Bridge / telemetry | NOT STARTED | Deferred. |

## Closing rules

Close a stage issue only with evidence that its own acceptance checklist passed at a named implementation SHA, and say so in the closing comment. Do not close Issue #43 or mark Stage 14 PASS from this document. Do not close older stage issues solely because later stages exist.
