# Issue #43 Chromium probe at implementation e6b97ff

This file closes the auditable-browser gap named in Issue #43. It is evidence-only. It does not change explorer behavior, tests, Phase H config, or frozen V0.1/Phase G artifacts.

## Code under test

`git rev-parse HEAD` at execution: `e6b97ffb47b3d33fa5f36d18cf01234052741e5e`

The probe script was untracked during that run, so HEAD stayed on the implementation SHA. `src/memory_infra/explorer.py` at that SHA is the Issue #44 search fix. Pytest and locked Phase H were not rerun; their prior exact-SHA record remains `experiments/results/stage14_issue43_e6b97ff.md`.

## Complete command

Script: `experiments/stage14_issue43_chromium_probe.py`

```
PYTHONPATH=src python3 experiments/stage14_issue43_chromium_probe.py
```

The script generates the page with `render_explorer`, injects an input/change dispatch probe, and runs:

```
/usr/bin/chromium --headless --no-sandbox --disable-gpu --virtual-time-budget=5000 --dump-dom file://<temp>/explorer.html
```

Fixture: threads `th-1`/`th-2`, same-id event `th-1`, events `e1`/`e2`, same-id state/point `e1`, `referential.same_thread` `rel-merge` evidence `same-goal`, `evidential.contradicts` `rel-con` evidence `both-seen`.

## Literal result

```
HEAD e6b97ffb47b3d33fa5f36d18cf01234052741e5e
CHROMIUM_EXIT 0
PROBE_ASSERT_EXIT 0
wrapper exit 0
```

`1` means visible, `0` means `is-hidden`. Edge, label, and inspector stay together.

```
all-empty	rel-merge-edge=1 rel-merge-label=1 rel-merge-inspector=1 rel-con-edge=1 rel-con-label=1 rel-con-inspector=1 thread:th-1=1 thread:th-2=1 event:th-1=1 event:e1=1 event:e2=1 state:e1=1 point:e1=1
all+same-goal	rel-merge-edge=1 rel-merge-label=1 rel-merge-inspector=1 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0
all+referential.same_thread	rel-merge-edge=1 rel-merge-label=1 rel-merge-inspector=1 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0
all+rel-merge	rel-merge-edge=1 rel-merge-label=1 rel-merge-inspector=1 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0
all+both-seen	rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=1 rel-con-label=1 rel-con-inspector=1 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0
all+left claim	rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=1 event:e2=0 state:e1=0 point:e1=0
all+e1	rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=1 event:e2=0 state:e1=1 point:e1=1
all+not-a-match	rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0
thread-empty	rel-merge-edge=1 rel-merge-label=1 rel-merge-inspector=1 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=1 thread:th-2=1 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0
thread+same-goal	rel-merge-edge=1 rel-merge-label=1 rel-merge-inspector=1 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0
event-empty	rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=1 rel-con-label=1 rel-con-inspector=1 thread:th-1=0 thread:th-2=0 event:th-1=1 event:e1=1 event:e2=1 state:e1=0 point:e1=0
event+both-seen	rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=1 rel-con-label=1 rel-con-inspector=1 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0
contradiction-empty	rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=1 rel-con-label=1 rel-con-inspector=1 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=1 event:e2=1 state:e1=0 point:e1=0
contradiction+both-seen	rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=1 rel-con-label=1 rel-con-inspector=1 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=1 event:e2=1 state:e1=0 point:e1=0
contradiction+same-goal	rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0
```

Covered: All/Threads/Events/Contradictions; relation id `rel-merge`; relation type `referential.same_thread`; evidence `same-goal` and `both-seen`; endpoint-only `e1` and `left claim` hide `rel-con` because `e2` does not match; no-match hides both edges, labels, and inspectors. Same-id state/point `e1` stay hidden in Contradictions.

No implementation defect reproduced. Stage 14 is not marked PASS. Issue #43 remains the acceptance gate.
