# Issue #43 independent run at implementation SHA 0d02872

Executed SHA: `0d0287207b94288cb10543df223fb90dd561dad6` (detached checkout). Not current main HEAD.
Observed main HEAD before this record: `6cd9a0b669e7b136b816d514d45dba5de906c82c`.
This file is evidence-only. It was not part of the executed tree. Stage 14 is not marked PASS. Issues were not closed. No next-stage issue was opened.
Execution verdict recorded here: CONDITIONAL (evidence only; acceptance remains with the review gate).

## Ancestry inspected

`git rev-parse HEAD` on clone before detach: `6cd9a0b669e7b136b816d514d45dba5de906c82c`

`git diff --name-only 670e4d2a0457823d2206cdd57a873e383c01ccd9..0d0287207b94288cb10543df223fb90dd561dad6`:
- experiments/results/stage14_issue39_670e4d2_check.md
- experiments/results/stage14_issue43_670e4d2_check.md
- experiments/results/stage14_issue43_independent_670e4d2.md
- experiments/results/stage14_issue43_rerun_670e4d2.md
- experiments/results/stage14_visual_explorer.md
- src/memory_infra/explorer.py
- tests/test_stage14_explorer.py

`git diff --name-only 0d0287207b94288cb10543df223fb90dd561dad6..6cd9a0b669e7b136b816d514d45dba5de906c82c`:
- docs/PROJECT_STATUS.md
- experiments/results/stage14_issue43_independent_0d02872.md
- experiments/results/stage14_issue43_independent_0d02872_rerun.md
- experiments/results/stage14_issue44_search.md

Descendants of the implementation SHA through `6cd9a0b` are documentation/evidence only. No V0.1 A/B/C/D/E or Phase G path was in those diffs. Phase H seeds/budget/policy were not edited.

## Commands and outputs

```
git checkout --detach 0d0287207b94288cb10543df223fb90dd561dad6
git rev-parse HEAD
0d0287207b94288cb10543df223fb90dd561dad6

PYTHONPATH=src python -m pytest -q tests
114 passed in 0.61s
exit 0

PYTHONPATH=src python experiments/phase_h_dynamics.py
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
deterministic_replay.match true
trace_artifact experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
exit 0
```

Phase H rewritten artifacts hashed to the historical trace SHA-256 and were restored. They are not part of this commit.

## Chromium input/change probe

Generated explorer HTML from `render_explorer` at the implementation SHA. Chromium headless `--dump-dom` after dispatching `change` on view radios and `input` on search. No new dependency.

Fixture: threads `th-1`/`th-2`, same-id event `th-1`, events `e1`/`e2`, same-id state and point `e1`, edges `referential.same_thread` (`rel-merge`, evidence `same-goal`, thread/thread) and `evidential.contradicts` (`rel-con`, evidence `both-seen`, event/event).

Literal probe text:

```
all-empty edges=rel-con:S,rel-merge:S labels=rel-con:S,rel-merge:S inspectors=rel-con:S,rel-merge:S
all-same-goal edges=rel-con:H,rel-merge:S labels=rel-con:H,rel-merge:S inspectors=rel-con:H,rel-merge:S
thread edges=rel-con:H,rel-merge:S labels=rel-con:H,rel-merge:S inspectors=rel-con:H,rel-merge:S
event edges=rel-con:S,rel-merge:H labels=rel-con:S,rel-merge:H inspectors=rel-con:S,rel-merge:H
contradiction edges=rel-con:S,rel-merge:H labels=rel-con:S,rel-merge:H inspectors=rel-con:S,rel-merge:H
nomatch edges=rel-con:H,rel-merge:H labels=rel-con:H,rel-merge:H inspectors=rel-con:H,rel-merge:H
```

S = shown, H = `is-hidden`. same_thread endpoints thread/thread; contradiction endpoints event/event. All-view `same-goal` kept rel-merge edge/label/inspector and hid rel-con. Thread/event/contradiction inspector visibility tracked edges. No orphan inspector on nomatch search.

## Boundary note

This record does not mark Stage 14 PASS and does not close Issue #43. Acceptance remains with the independent review gate.
