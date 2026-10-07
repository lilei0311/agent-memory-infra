# Phase G attention comparison

Re-run for Issue #6 review. Attention rules and locked comparison inputs were not changed after seeing results. Reopen and causal relation are not used by this runner.

## Git

- parent HEAD before this evidence commit: daae8779d9ad44788210f66ed297bdf538d4f4d4
- scoring code: `src/memory_infra/graph.py` `_distribution` and `_allocate_with_attention` (unchanged by the reopen/causal patch)

## Command

```text
PYTHONPATH=src python experiments/phase_g_attention.py
```

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
| divergent | 0.275 | 0.725 | 1.000 | 0.625 | 0.5862 | 17 | 12 |
| automatic | 0.675 | 0.325 | 1.000 | 0.875 | 0.5385 | 7 | 6 |

Counts are seed-means of the per-seed counts, so they match the earlier table's integer counts. Ratios are seed-means. No retune.
