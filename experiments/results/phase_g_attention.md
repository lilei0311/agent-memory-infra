# Phase G attention comparison

Locked before the run. Not retuned after results.

- seeds: 7, 11, 19, 23, 42
- context budget: 4
- stream: T1 T1 T2 T3 T1 T2 T3 T1 T4 T1
- each thread has 3 events
- divergence signal only on the marked T2, T3, T4 turns
- policies: none, focus, divergent, automatic
- same stream, candidate pool, seed, and budget

| policy | target precision | irrelevant ratio | contamination | switch recovery | budget use | active threads | diversity | cross-thread rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | 0.425 | 0.575 | 1.000 | 0.625 | 1.000 | 2.000 | 0.500 | 1.000 |
| focus | 0.750 | 0.250 | 1.000 | 1.000 | 1.000 | 2.000 | 0.500 | 1.000 |
| divergent | 0.275 | 0.725 | 1.000 | 0.625 | 1.000 | 2.000 | 0.500 | 1.000 |
| automatic | 0.675 | 0.325 | 1.000 | 0.875 | 1.000 | 2.000 | 0.500 | 1.000 |

Reading: focus has the highest target-thread precision. Automatic sits between focus and no-attention. Divergent has the lowest precision and the highest irrelevant ratio. Contamination stays 1.0 because the budget is larger than one thread's exclusive share, so every condition still pulls another thread. That is a limitation of this locked setup, not a tuned result.
