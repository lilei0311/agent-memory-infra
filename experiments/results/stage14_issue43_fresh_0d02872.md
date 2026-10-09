# Issue #43 fresh run at implementation SHA 0d02872

Executed SHA: `0d0287207b94288cb10543df223fb90dd561dad6` (detached worktree `/tmp/ami-impl`). Not current main HEAD.
Observed main HEAD before this record: `14e23b04082dbab1f927bf7f8ab689fbfb59d7f8`.
This file is evidence-only. It was not part of the executed tree. Stage 14 is not marked PASS. Issues were not closed. No next-stage issue was opened.
Execution note: this agent does not issue the acceptance verdict. Status left CONDITIONAL for the review gate.

## Ancestry inspected

`git rev-parse HEAD` on clone: `14e23b04082dbab1f927bf7f8ab689fbfb59d7f8`

`git diff --name-only 0d0287207b94288cb10543df223fb90dd561dad6..14e23b04082dbab1f927bf7f8ab689fbfb59d7f8`:
- docs/PROJECT_STATUS.md
- experiments/results/stage14_issue43_independent_0d02872.md
- experiments/results/stage14_issue43_independent_0d02872_rerun.md
- experiments/results/stage14_issue43_independent_0d02872_review.md
- experiments/results/stage14_issue44_search.md

No source, test, Phase H config, or frozen V0.1/Phase G path is in that diff. Descendants after `0d02872` are documentation/evidence only.

## Commands and outputs

```
git worktree add --detach /tmp/ami-impl 0d0287207b94288cb10543df223fb90dd561dad6
git rev-parse HEAD
0d0287207b94288cb10543df223fb90dd561dad6

PYTHONPATH=src python3 -m pytest -q tests
114 passed in 0.71s
exit 0

PYTHONPATH=src python3 experiments/phase_h_dynamics.py
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
deterministic_replay.match true
trace_artifact experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
exit 0
```

114 vs earlier 113: this run is at `0d02872`, which adds the Issue #44 relation/evidence search test. The 113 count belongs to earlier implementation `670e4d2`, not this SHA.

Phase H rewrote local trace artifacts; they hashed to the historical trace SHA-256 and are not part of this commit. Seeds, budget, and policy were not edited.

## Chromium input/change probe

Generated explorer HTML from `render_explorer` at the implementation SHA. Chromium headless `--dump-dom` after dispatching `change` on view radios and `input` on `input[name=q]`. No new dependency.

Fixture: threads `th-1`/`th-2`, same-id event `th-1`, events `e1`/`e2`, same-id state and point `e1`, edges `referential.same_thread` (`rel-merge`, evidence `same-goal`, thread/thread) and `evidential.contradicts` (`rel-con`, evidence `both-seen`, event/event).

Literal probe text:

```
all-empty edges=rel-con:S,rel-merge:S labels=rel-con:S,rel-merge:S inspectors=rel-con:S,rel-merge:S
all-same-goal edges=rel-con:H,rel-merge:S labels=rel-con:H,rel-merge:S inspectors=rel-con:H,rel-merge:S
thread-same-goal edges=rel-con:H,rel-merge:S labels=rel-con:H,rel-merge:S inspectors=rel-con:H,rel-merge:S
thread-empty edges=rel-con:H,rel-merge:S labels=rel-con:H,rel-merge:S inspectors=rel-con:H,rel-merge:S
event-empty edges=rel-con:S,rel-merge:H labels=rel-con:S,rel-merge:H inspectors=rel-con:S,rel-merge:H
contradiction-empty edges=rel-con:S,rel-merge:H labels=rel-con:S,rel-merge:H inspectors=rel-con:S,rel-merge:H
nomatch edges=rel-con:H,rel-merge:H labels=rel-con:H,rel-merge:H inspectors=rel-con:H,rel-merge:H
```

S = shown, H = `is-hidden`. All-view `same-goal` kept rel-merge edge/label/inspector and hid rel-con. Thread view kept the same-thread edge. Event and contradiction views, with search cleared, showed only the contradiction edge. Nomatch hid both. Inspector visibility tracked edge visibility. No orphan inspector.

## Evidence table

| criterion | tested SHA | command or artifact | result |
| --- | --- | --- | --- |
| descendants evidence-only | 0d02872..14e23b0 | git diff --name-only | docs and evidence only |
| pytest | 0d02872 | PYTHONPATH=src python3 -m pytest -q tests | 114 passed, exit 0 |
| locked Phase H | 0d02872 | experiments/phase_h_dynamics.py | exit 0, seeds 7/11/19, budget 4, policy none, replay match true, trace 5ba3af8f... |
| relation/evidence search | 0d02872 | Chromium input dispatch | all+same-goal keeps rel-merge, hides rel-con |
| view transitions | 0d02872 | Chromium change dispatch | thread keeps same_thread; event/contradiction keep contradiction only |
| inspector tracks edge | 0d02872 | Chromium dump | labels and inspectors match edge S/H |
| frozen V0.1/Phase G | 0d02872..HEAD | changed-file list | no frozen path changed |

## Boundary note

This record does not mark Stage 14 PASS and does not close Issue #43. Acceptance remains with the independent review gate.
