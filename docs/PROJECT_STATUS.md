# Project status map

Observation date: 2026-10-09. This file is a coordination map, not an acceptance verdict.

Default-branch implementation HEAD before this evidence commit: `e6b97ffb47b3d33fa5f36d18cf01234052741e5e`.

Supersedes the `0d02872` / `3ed4621` baseline below. That older baseline is historical only.

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
| Latest implementation under test | `e6b97ffb47b3d33fa5f36d18cf01234052741e5e` | Issue #44 relation-corpus hits limited to relation id, relation type, and `data-evidence`. Files: `src/memory_infra/explorer.py`, `tests/test_stage14_explorer.py`. Prior implementation `0d02872` is not the code under test. |
| Evidence-only child of implementation | `707d33b972744b646f88f4b1fe28a14f86fdc6fb` | Records the Issue #44 run at `0d02872`. Not the executed tree. |
| Earlier Issue #43 evidence | `8564d18b24fa1e886838ab93cc084b8bbde7ed9a` | Records an Issue #43 run at `0d02872`. Not the executed tree. |
| Evidence-only HEAD | `3ed462109041d2b76fb7dfc0a5363fac332d8674` | Records the Issue #43 playbook run at `0d02872`. Not the executed tree. Descendants of `0d02872` through this HEAD are evidence or this status map, not a new implementation. |
| Prior implementation | `670e4d2a0457823d2206cdd57a873e383c01ccd9` | Issue #42 inspector visibility bound to edge visibility. Superseded for search scope by `0d02872`. |

Do not treat `3ed4621` or `8564d18` as the code-under-test.

## Stage 14 position

Status: **CONDITIONAL, not PASS**.

Implemented, not independently accepted: read-only explorer; kind-qualified contradiction endpoints (Issue #40); `referential.same_thread` thread endpoints (Issue #41); inspector visibility tracks edge visibility (Issue #42); All-view search can keep an in-view edge when the query matches relation id, type, or evidence text (Issue #44).

Recorded evidence, not re-executed for this status commit:

- `experiments/results/stage14_visual_explorer.md` and `experiments/results/stage14_issue43_playbook_0d02872.md` record pytest, locked Phase H, and Chromium input/change dispatch at `0d02872`.
- Locked Phase H configuration cited by those records: seeds 7, 11, 19; budget 4; policy none; historical trace SHA-256 `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
- The new run is recorded in `experiments/results/stage14_issue43_e6b97ff.md` and was executed at `e6b97ff`, not at this evidence commit.

Issue #44 checks were executed at `e6b97ff`; close only if that evidence is accepted. Issue #43 remains the Stage 14 gate. Current code-under-test is `e6b97ff`, not `0d02872`.
Issues #39–#42 remain open. They are the prior acceptance and defect chain. Open state is not proof the later fix is missing.

Exit condition for Stage 14: independent acceptance of the Issue #43 checklist at implementation SHA `e6b97ffb47b3d33fa5f36d18cf01234052741e5e`, not at an evidence-only child and not from the older `0d02872` records. Only that gate may mark PASS. This map does not.

## Single next action

Owner: Issue #43.

Action: independently accept or fail Stage 14 against `experiments/results/stage14_issue43_e6b97ff.md`, which records pytest, locked Phase H, and Chromium input/change dispatch at `e6b97ff`. Do not reimplement the search fix unless that review reproduces a defect. Do not open a duplicate Stage 14 issue. Do not start a next product stage from this map.

## Numbered stage crosswalk

Acceptance below is not re-decided here. Open issues are left open.

| Stage | Status used here | Notes |
| --- | --- | --- |
| V0.1 policy experiments | FROZEN | A/B/C/D/E. Do not retune or rewrite results. |
| V0.2 / Phase H dynamics | FROZEN config | Locked seeds 7/11/19, budget 4, policy none. |
| 2–13 product seams | IMPLEMENTED IN TREE / NOT RE-ACCEPTED HERE | Specs exist under `docs/STAGE2_` through `docs/STAGE13_`. Matching issues remain open. Do not mass-close from this map. |
| 14 visual explorer | CONDITIONAL | Implementation `e6b97ff`. Gate: Issue #43. |
| Hub / Memory Bridge / telemetry | NOT STARTED | Deferred. |

## Closing rules

Close a stage issue only with evidence that its own acceptance checklist passed at a named implementation SHA, and say so in the closing comment. Do not close Issue #43 or mark Stage 14 PASS from this document. Do not close older stage issues solely because later stages exist.

## 2026-10-10 defect fix (this commit)

Live Chromium at `0d02872` showed All-view query `e1` kept `rel-con` visible while endpoint `e2` was hidden, because `relationCorpusHit` used `hit(edge)` and edge `data-text` includes source/target ids. Recorded evidence that claimed the edge was hidden did not match that run.

This commit limits relation-corpus hits to relation id, relation type, and `data-evidence`. Endpoint-only search again requires both endpoints. Stage 14 remains CONDITIONAL. Issue #43 stays the acceptance gate. Do not mark PASS from this map.



## 2026-10-10 exact-SHA check

Executed at `e6b97ffb47b3d33fa5f36d18cf01234052741e5e`, not at this evidence commit. Pytest exit 0, `114 passed in 0.64s`. Phase H exit 0; seeds 7, 11, 19; budget 4; policy none; deterministic replay true; trace SHA-256 `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Chromium input/change probe: All-view `e1` hides `rel-con`; All-view `same-goal` keeps `rel-merge`. Literal record: `experiments/results/stage14_issue43_e6b97ff.md`. Stage 14 remains CONDITIONAL. Do not mark PASS from this map.
