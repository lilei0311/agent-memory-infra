# Issue #43 independent execution at implementation 670e4d2

Executed code-under-test: `670e4d2a0457823d2206cdd57a873e383c01ccd9` (detached worktree).
Repository HEAD before this record: `ca2a3140962624f289c7d16e4b112549d8ac8bdf`.
This commit is evidence-only and was not the executed HEAD. Stage 14 is not marked PASS. Issues #39–#43 remain open. No next-stage issue was opened. Executor does not self-declare stage acceptance.

## Ancestry

```
git rev-parse HEAD
ca2a3140962624f289c7d16e4b112549d8ac8bdf

git diff --name-only 670e4d2a0457823d2206cdd57a873e383c01ccd9..HEAD
experiments/results/stage14_issue39_670e4d2_check.md
experiments/results/stage14_issue43_670e4d2_check.md
experiments/results/stage14_visual_explorer.md
```

Descendants of implementation `670e4d2` are evidence-only. They do not modify `src/`, `tests/`, experiment parameters, or frozen artifacts. Implementation commit changes only `docs/STAGE14_VISUAL_EXPLORER.md`, `src/memory_infra/explorer.py`, `tests/test_stage14_explorer.py`.

## Commands at implementation SHA

```
git rev-parse HEAD
670e4d2a0457823d2206cdd57a873e383c01ccd9

PYTHONPATH=src python3.11 -m pytest -q tests
........................................................................ [ 63%]
.........................................                                [100%]
113 passed in 0.58s
PYTEST_EXIT:0

PYTHONPATH=src python3.11 experiments/phase_h_dynamics.py
PHASEH_EXIT:0
```

Locked first line: `locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}`.

`deterministic_replay.match` true for seeds 7, 11, and 19. Historical trace SHA-256 unchanged: `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

Last line: `trace_artifact /tmp/ami-impl/experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

Working tree did not modify tracked Phase H or V0.1/Phase G artifacts. Seeds, budget, and policy were not changed.

## Static checks at 670e4d2

`src/memory_infra/explorer.py` does not import `memory_infra.store`. `read_only` projection guard is present. Fallback `referential.same_thread` maps to thread/thread.

## Browser input/change dispatch

Existing Chromium loaded generated explorer HTML from the implementation renderer. View radios and the search field received `change`/`input`. No new dependency. Fixture: threads `th-1`/`th-2`, same-id event `th-1`, events `e1`/`e2`, same-id state and point `e1`, edges `referential.same_thread` (`rel-merge`, evidence `same-goal`) and `evidential.contradicts` (`rel-con`, evidence `both-seen`).

Edge kinds observed: `evidential.contradicts:event/event`, `referential.same_thread:thread/thread`.

```
threads | rel-merge:edge=visible,label=visible,inspector=visible | rel-con:edge=hidden,label=hidden,inspector=hidden | state-e1=hidden | point-e1=hidden | event-e1=hidden | event-e2=hidden | thread-th1=visible | event-th1=hidden
events | rel-merge:edge=hidden,label=hidden,inspector=hidden | rel-con:edge=visible,label=visible,inspector=visible | state-e1=hidden | point-e1=hidden | event-e1=visible | event-e2=visible | thread-th1=hidden | event-th1=visible
contradictions | rel-merge:edge=hidden,label=hidden,inspector=hidden | rel-con:edge=visible,label=visible,inspector=visible | state-e1=hidden | point-e1=hidden | event-e1=visible | event-e2=visible | thread-th1=hidden | event-th1=hidden
con+both-seen | rel-merge:edge=hidden,label=hidden,inspector=hidden | rel-con:edge=visible,label=visible,inspector=visible | state-e1=hidden | point-e1=hidden | event-e1=visible | event-e2=visible | thread-th1=hidden | event-th1=hidden
con+e1 | rel-merge:edge=hidden,label=hidden,inspector=hidden | rel-con:edge=visible,label=visible,inspector=visible | state-e1=hidden | point-e1=hidden | event-e1=visible | event-e2=visible | thread-th1=hidden | event-th1=hidden
con+left-claim | rel-merge:edge=hidden,label=hidden,inspector=hidden | rel-con:edge=visible,label=visible,inspector=visible | state-e1=hidden | point-e1=hidden | event-e1=visible | event-e2=visible | thread-th1=hidden | event-th1=hidden
all+same-goal | rel-merge:edge=hidden,label=hidden,inspector=hidden | rel-con:edge=hidden,label=hidden,inspector=hidden | state-e1=hidden | point-e1=hidden | event-e1=hidden | event-e2=hidden | thread-th1=hidden | event-th1=hidden
all+thread-alpha | rel-merge:edge=hidden,label=hidden,inspector=hidden | rel-con:edge=hidden,label=hidden,inspector=hidden | state-e1=hidden | point-e1=hidden | event-e1=hidden | event-e2=hidden | thread-th1=visible | event-th1=hidden
all-clear | rel-merge:edge=visible,label=visible,inspector=visible | rel-con:edge=visible,label=visible,inspector=visible | state-e1=visible | point-e1=visible | event-e1=visible | event-e2=visible | thread-th1=visible | event-th1=visible
threads-again | rel-merge:edge=visible,label=visible,inspector=visible | rel-con:edge=hidden,label=hidden,inspector=hidden | state-e1=hidden | point-e1=hidden | event-e1=hidden | event-e2=hidden | thread-th1=visible | event-th1=hidden
```

No new concrete defect recorded in this run. Headless `--dump-dom` did not execute the appended probe script; the interaction above was dispatched in an existing Chromium session against the same generated HTML.
