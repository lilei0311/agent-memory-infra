# Phase G attention comparison

Locked before the run. Attention rules were not changed after seeing results.

- seeds: 7, 11, 19, 23, 42
- context budget: 4
- stream: T1 T1 T2 T3 T1 T2 T3 T1 T4 T1
- each thread has 3 events
- related ground truth, locked: T1-T2 and T3-T4
- useful_cross_thread_association = related cross-thread items / all cross-thread items

| policy | target precision | irrelevant | contamination | switch recovery | useful cross-thread | related count | unrelated count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| none | 0.425 | 0.575 | 1.000 | 0.625 | 0.478 | 11 | 12 |
| focus | 0.750 | 0.250 | 1.000 | 1.000 | 0.700 | 7 | 3 |
| divergent | 0.275 | 0.725 | 1.000 | 0.625 | 0.586 | 17 | 12 |
| automatic | 0.675 | 0.325 | 1.000 | 0.875 | 0.538 | 7 | 6 |

Divergent retrieves more related cross-thread items (17 vs focus 7) but a lower share of those items are related (0.586 vs 0.700). That is the exploration tradeoff in this locked world. Attention scoring was not changed to make automatic beat focus.
