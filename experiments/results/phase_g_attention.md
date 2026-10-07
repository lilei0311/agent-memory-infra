# Phase G attention comparison

Re-run at the current code HEAD requested by Issue #6 review comment 6043207209. Attention rules and locked comparison inputs were not changed. Reopen and causal relation are not used by this runner.

## Git

- experiment and tests executed at code HEAD: e19b5308368f66981e740da6038d20227cde5633
- parent of that HEAD: 5fe08282d5a492d462e72daf68446a05a7f70e4e (float-assertion fix; scoring code unchanged)
- scoring code: `src/memory_infra/graph.py` `_distribution` and `_allocate_with_attention`
- this results file is the only change after the executed HEAD; `src/` and `tests/` match e19b5308368f66981e740da6038d20227cde5633

## Command

```text
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_g_attention.py
```

Pytest on e19b5308368f66981e740da6038d20227cde5633: 22 passed in 0.07s.

## Locked config

- seeds: 7, 11, 19, 23, 42
- context budget: 4
- stream: T1 T1 T2 T3 T1 T2 T3 T1 T4 T1
- diverge flags: F F F F F T T F T F
- each thread has 3 events
- related ground truth, locked: T1-T2 and T3-T4
- policies: none / focus / divergent / automatic
- useful_cross_thread_association = related cross-thread items / all cross-thread items

## Allocation parameters that affect this run

- none: candidates ranked by recency descending, take budget 4; no attention weight
- focus distribution: anchor 0.8, remaining active threads share 0.2
- divergent distribution: equal share across active threads
- combined (automatic only, when continuity and divergence): anchor 0.5, remaining active threads share 0.5
- attention score: thread weight + 0.01 * recency + 0.01 * contextual_fit; tie-break event id ascending
- no parameter was changed to favor automatic

## Results

| policy | target precision | irrelevant | contamination | switch recovery | useful cross-thread | related count | unrelated count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| none | 0.425 | 0.575 | 1.000 | 0.625 | 0.4783 | 11 | 12 |
| focus | 0.750 | 0.250 | 1.000 | 1.000 | 0.700 | 7 | 3 |
| divergent | 0.275 | 0.725 | 1.000 | 1.000 | 0.625 | 0.5862 | 17 | 12 |
| automatic | 0.675 | 0.325 | 1.000 | 0.875 | 0.5385 | 7 | 6 |

Counts are seed-means of the per-seed counts. Ratios are seed-means. No retune. V0.1 experiment scripts, seeds, and historical result files were not edited.
