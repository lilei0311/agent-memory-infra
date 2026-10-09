# Issue #43 playbook run at implementation 0d02872

This file records a fresh execution. It is not an acceptance verdict. Stage 14 is not marked PASS. Issues were not closed. No next-stage issue was opened.

Review HEAD at execution: `f339e71a0ce8b1998d73e70ba29d523bf092d0cf` (evidence-only parent of this commit).
Implementation-under-test SHA: `0d0287207b94288cb10543df223fb90dd561dad6`.
This evidence commit was not the executed tree.

## Ancestry

`git diff --name-only 0d0287207b94288cb10543df223fb90dd561dad6..f339e71a0ce8b1998d73e70ba29d523bf092d0cf`:

- docs/PROJECT_STATUS.md
- experiments/results/stage14_issue43_fresh_0d02872.md
- experiments/results/stage14_issue43_independent_0d02872.md
- experiments/results/stage14_issue43_independent_0d02872_rerun.md
- experiments/results/stage14_issue43_independent_0d02872_review.md
- experiments/results/stage14_issue44_search.md

No source, test, config, or frozen path after `0d02872`. Implementation commit `0d02872` changed `src/memory_infra/explorer.py` and `tests/test_stage14_explorer.py` only.

Worktree: `git worktree add --detach` at `0d0287207b94288cb10543df223fb90dd561dad6`. `git rev-parse HEAD` printed that SHA. Status was clean before tests.

## Commands at tested SHA 0d02872

```
PYTHONPATH=src python3 -m pytest -q tests
114 passed in 0.75s
PYTEST_EXIT=0
```

```
PYTHONPATH=src python3 experiments/phase_h_dynamics.py
PHASE_H_EXIT=0
```

Locked config printed by the experiment:

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
```

`deterministic_replay.match` true. Trace artifact SHA-256 `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Seeds, budget, and policy were not changed. The worktree trace file was not copied back.

## Explorer checks

Rendered from `render_explorer` at SHA `0d02872` using the Issue #44 node/edge fixture (`rel-merge` / `rel-con`). Chromium page load, then `change` on the view radio and `input` on the search field. S=shown, H=is-hidden.

```
all-empty edges=rel-con:S,rel-merge:S labels=rel-con:S,rel-merge:S inspectors=rel-con:S,rel-merge:S
all-same-goal edges=rel-con:H,rel-merge:S labels=rel-con:H,rel-merge:S inspectors=rel-con:H,rel-merge:S
thread-same-goal edges=rel-con:H,rel-merge:S labels=rel-con:H,rel-merge:S inspectors=rel-con:H,rel-merge:S
thread-empty edges=rel-con:H,rel-merge:S labels=rel-con:H,rel-merge:S inspectors=rel-con:H,rel-merge:S
event-empty edges=rel-con:S,rel-merge:H labels=rel-con:S,rel-merge:H inspectors=rel-con:S,rel-merge:H
contradiction-empty edges=rel-con:S,rel-merge:H labels=rel-con:S,rel-merge:H inspectors=rel-con:S,rel-merge:H
nomatch edges=rel-con:H,rel-merge:H labels=rel-con:H,rel-merge:H inspectors=rel-con:H,rel-merge:H
merge-kinds=thread/thread
con-kinds=event/event
readonly=true owner=mechanism
```

1. Four views: all shows both edges; thread shows only rel-merge; event and contradiction show only rel-con.
2. Search updates on input: all+same-goal keeps rel-merge (evidence text) and hides rel-con. View radios update on change.
3. Contradiction endpoints stay event/event. Same raw id `e1` state/point is not the contradiction endpoint in `test_relation_and_evidence_search_keeps_edge_visible`.
4. `referential.same_thread` endpoints are thread/thread (`rel-merge`).
5. Labels and inspectors match edge S/H on every transition. No orphan inspector.
6. nomatch-zzz hides both edges, labels, and inspectors.
7. `test_render_is_deterministic_and_does_not_mutate_input` is in the 114 passed. Fixture relation ids stable.
8. Body `data-read-only=true` `data-owner=mechanism`. Renderer refuses a projection that is not mechanism-owned read-only (`render_explorer`). No second graph owner added in the `0d02872` diff.

## Frozen boundary

`0d02872..f339e71` does not touch V0.1 A/B/C/D/E, Phase G artifacts, Phase H config, or expected values. This run did not edit them.

## Verdict recorded by executor

CONDITIONAL. This executor does not issue Stage 14 PASS and does not close Issue #43. Independent review still owns acceptance.
