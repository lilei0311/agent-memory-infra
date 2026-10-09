# Issue #43 / #44 check at implementation e6b97ff

Implementation SHA tested: `e6b97ffb47b3d33fa5f36d18cf01234052741e5e`

This file records that run. It is not a Stage 14 PASS. The evidence commit that adds this file was not the executed HEAD.

## Ancestry

`git rev-parse HEAD` at execution: `e6b97ffb47b3d33fa5f36d18cf01234052741e5e`

`git diff --name-only 0d0287207b94288cb10543df223fb90dd561dad6..e6b97ffb47b3d33fa5f36d18cf01234052741e5e`:

- `docs/PROJECT_STATUS.md`
- `experiments/results/stage14_issue43_fresh_0d02872.md`
- `experiments/results/stage14_issue43_independent_0d02872.md`
- `experiments/results/stage14_issue43_independent_0d02872_rerun.md`
- `experiments/results/stage14_issue43_independent_0d02872_review.md`
- `experiments/results/stage14_issue43_playbook_0d02872.md`
- `experiments/results/stage14_issue44_search.md`
- `src/memory_infra/explorer.py`
- `tests/test_stage14_explorer.py`

Source/test change since `0d02872` is only the Issue #44 narrowing in `explorer.py` and `tests/test_stage14_explorer.py`. No V0.1, Phase G, or Phase H config path is in that diff. `experiments/results/phase_h_trace.json` was not modified by this run (`git diff --stat` empty).

## Commands and results

```
PYTHONPATH=src python3 -m pytest -q tests
# 114 passed in 0.64s
# exit 0

PYTHONPATH=src python3 experiments/phase_h_dynamics.py
# exit 0
# locked seeds [7, 11, 19], budget 4, policy none
# deterministic_replay.match true
# trace artifact experiments/results/phase_h_trace.json
# SHA-256 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
```

Chromium: existing `/usr/bin/chromium --headless --no-sandbox --disable-gpu --virtual-time-budget=5000 --dump-dom`. No new dependency. Page from `render_explorer` on this tree. Fixture: threads `th-1`/`th-2`, same-id event `th-1`, events `e1`/`e2`, same-id state/point `e1`, `referential.same_thread` `rel-merge` evidence `same-goal`, `evidential.contradicts` `rel-con` evidence `both-seen`. Probe set view radios and dispatched `change`, set search and dispatched `input`.

- all-empty: both edges, labels, inspectors, nodes shown.
- all+same-goal: `rel-merge` edge/label/inspector shown; endpoints hidden; `rel-con` hidden.
- all+referential.same_thread: same as all+same-goal.
- all+rel-merge: same as all+same-goal.
- all+both-seen: `rel-con` edge/label/inspector shown; endpoints hidden; `rel-merge` hidden.
- all+left claim: event `e1` shown; `rel-con` edge/label/inspector hidden because `e2` did not match.
- all+e1: event/state/point `e1` shown; event `e2` hidden; `rel-con` edge/label/inspector hidden. Endpoint-only search requires both endpoints.
- all+not-a-match: both edges, labels, and inspectors hidden.
- contradiction-empty: `rel-con` edge/label/inspector and event endpoints `e1`/`e2` shown; same-id state/point `e1` hidden; `rel-merge` hidden.
- contradiction+both-seen: same as contradiction-empty.
- contradiction+same-goal: `rel-merge` stays hidden; `rel-con` hidden.
- thread+same-goal: `rel-merge` edge/label/inspector shown; `rel-con` hidden.
- event+both-seen: `rel-con` edge/label/inspector shown; `rel-merge` hidden; endpoints hidden.

Pytest at this SHA covers kind-qualified contradiction endpoints, same-thread thread endpoints, deterministic render, and read-only projection rejection. Stage 14 is not marked PASS. Issue #43 remains the acceptance gate.
