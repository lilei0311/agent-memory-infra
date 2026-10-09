# Issue #43 independent run at implementation SHA 0d02872

Executed SHA: `0d0287207b94288cb10543df223fb90dd561dad6` (detached checkout). Not current main HEAD.
Observed main HEAD before this record: `ab8176355f0a1f2cb539ec05eccd43f379ffa04a`.
This file is evidence-only. It was not part of the executed tree. Stage 14 is not marked PASS. Issues were not closed. No next-stage issue was opened.

## Ancestry inspected

`git diff --name-only 670e4d2a0457823d2206cdd57a873e383c01ccd9..0d0287207b94288cb10543df223fb90dd561dad6`:
- experiments/results/stage14_issue39_670e4d2_check.md
- experiments/results/stage14_issue43_670e4d2_check.md
- experiments/results/stage14_issue43_independent_670e4d2.md
- experiments/results/stage14_issue43_rerun_670e4d2.md
- experiments/results/stage14_visual_explorer.md
- src/memory_infra/explorer.py
- tests/test_stage14_explorer.py

`git diff --name-only 0d0287207b94288cb10543df223fb90dd561dad6..ab8176355f0a1f2cb539ec05eccd43f379ffa04a`:
- docs/PROJECT_STATUS.md
- experiments/results/stage14_issue43_independent_0d02872.md
- experiments/results/stage14_issue44_search.md

Descendants of the implementation SHA through `ab81763` are documentation/evidence only. No V0.1 A/B/C/D/E or Phase G path was in those diffs. Phase H seeds/budget/policy were not edited.

## Commands and outputs

```
git checkout --detach 0d0287207b94288cb10543df223fb90dd561dad6
git rev-parse HEAD
0d0287207b94288cb10543df223fb90dd561dad6

PYTHONPATH=src python -m pytest -q tests
114 passed in 0.75s
exit 0

PYTHONPATH=src python experiments/phase_h_dynamics.py
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
deterministic_replay.match true
trace_artifact experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
exit 0
```

Phase H rewritten artifacts were restored and are not part of this commit.

## Chromium input/change probe

Generated explorer HTML from `render_explorer` at the implementation SHA. Served over HTTP. Dispatched `change` on view radios and `input` on search. No new dependency.

Fixture: threads `th-1`/`th-2`, same-id event `th-1`, events `e1`/`e2`, same-id state and point `e1`, edges `referential.same_thread` (`rel-merge`, evidence `same-goal`, thread/thread) and `evidential.contradicts` (`rel-con`, evidence `both-seen`, event/event`).

- all + empty query: both edges, labels, inspectors shown
- all + `same-goal`: rel-merge edge/label/inspector shown; rel-con hidden
- thread: rel-merge shown; rel-con hidden; inspector matched edge
- event: rel-con shown; rel-merge hidden; inspector matched edge
- contradiction: rel-con shown; rel-merge hidden; inspector matched edge
- all + `zzzz-no-match`: both edges, labels, inspectors hidden (no orphan inspector)

## Boundary note

This record does not mark Stage 14 PASS and does not close Issue #43. Acceptance remains with the independent review gate.
