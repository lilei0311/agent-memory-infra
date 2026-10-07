# Phase G attention comparison

Issue #7 required direct execution evidence at final HEAD `500eb01223ec112ec5d4cffc043069bcbd62c3ca`. Tests and the locked attention experiment were executed at that SHA. Seeds, stream, budget, policies, and scoring weights were not changed. No attention retune. V0.1 scripts and historical results were not edited. Reopen and causal relation are not used by this runner.

## Git

- experiment and tests executed at code HEAD: 500eb01223ec112ec5d4cffc043069bcbd62c3ca
- parent of that HEAD: d2faa8e1709b7cc5ecd58048807c4422a689f36a (prior evidence record of the locked run at d2faa8e; scoring code unchanged)
- scoring code: `src/memory_infra/graph.py` `_distribution` and `_allocate_with_attention`
- 500eb01223ec112ec5d4cffc043069bcbd62c3ca itself only recorded the parent-HEAD run; `src/` and `tests/` match d2faa8e1709b7cc5ecd58048807c4422a689f36a
- this results file is the only change after the executed HEAD

## Command

```text
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_g_attention.py
```

Executed 2026-10-07T18:36:27Z, Python 3.10.21, at 500eb01223ec112ec5d4cffc043069bcbd62c3ca.

Pytest stdout:

```text
......................                                                   [100%]
22 passed in 0.06s
```

Experiment stdout:

```text
locked {'seeds': [7, 11, 19, 23, 42], 'budget': 4, 'stream': 10}
none {'target_thread_precision': 0.425, 'irrelevant_context_ratio': 0.575, 'cross_thread_contamination': 1.0, 'topic_switch_recovery': 0.625, 'context_budget_utilization': 1.0, 'divergent_active_thread_count': 2.0, 'diversity': 0.5, 'cross_thread_retrieval_rate': 1.0, 'useful_cross_thread_association': 0.4783, 'related_cross_thread_count': 11.0, 'unrelated_cross_thread_count': 12.0}
focus {'target_thread_precision': 0.75, 'irrelevant_context_ratio': 0.25, 'cross_thread_contamination': 1.0, 'topic_switch_recovery': 1.0, 'context_budget_utilization': 1.0, 'divergent_active_thread_count': 2.0, 'diversity': 0.5, 'cross_thread_retrieval_rate': 1.0, 'useful_cross_thread_association': 0.7, 'related_cross_thread_count': 7.0, 'unrelated_cross_thread_count': 3.0}
divergent {'target_thread_precision': 0.275, 'irrelevant_context_ratio': 0.725, 'cross_thread_contamination': 1.0, 'topic_switch_recovery': 0.625, 'context_budget_utilization': 1.0, 'divergent_active_thread_count': 2.0, 'diversity': 0.5, 'cross_thread_retrieval_rate': 1.0, 'useful_cross_thread_association': 0.5862, 'related_cross_thread_count': 17.0, 'unrelated_cross_thread_count': 12.0}
automatic {'target_thread_precision': 0.675, 'irrelevant_context_ratio': 0.325, 'cross_thread_contamination': 1.0, 'topic_switch_recovery': 0.875, 'context_budget_utilization': 1.0, 'divergent_active_thread_count': 2.0, 'diversity': 0.5, 'cross_thread_retrieval_rate': 1.0, 'useful_cross_thread_association': 0.5385, 'related_cross_thread_count': 7.0, 'unrelated_cross_thread_count': 6.0}
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

Counts are seed-means of the per-seed counts. Ratios are seed-means. No retune. V0.1 experiment scripts, seeds, and historical result files were not edited. Phase G PASS is not declared here.
