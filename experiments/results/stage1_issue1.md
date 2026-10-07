# Issue #1 Stage 1 results

Locked before the run. Not retuned after seeing numbers.

- experiment_id: stage1-robustness-v0.1
- tasks: 500
- K: 3
- seeds: 7, 11, 19, 23, 42
- query: [1.0, 0.0]
- alpha0: 0.5, step: 0.05, alpha range: [0, 2]
- world: current control (2 near-fail always fail, 2 far-ok always succeed, 6 neutral coin-flip)
- noise flips only the label the learner writes; metrics use the unflipped ground truth
- missing feedback skips observe; it is not success and not failure
- baseline and adaptive share the same seed, store init, candidate set, K, and outcome stream

Metrics:
- task success rate: top-1 true outcome is success
- useful retrieval precision: fraction of top-3 that are far-ok
- retrieval waste: fraction of top-3 that are near-fail
- error/correction rate: top-1 true outcome is failure

Numbers below are means over the 5 seeds.

## Phase A — ideal control

| policy | success | precision | waste | error | final alpha | last-100 stability |
| --- | --- | --- | --- | --- | --- | --- |
| baseline | 0.0992 | 0.0000 | 0.6667 | 0.9008 | n/a | 1.00 |
| adaptive | 0.9992 | 0.6667 | 0.0015 | 0.0008 | 2.00 | 1.00 |

Baseline per seed: 7/11/19/42 success 0.00 (top-1 near-fail-1); seed 23 success 0.496 because a neutral embedding outranked near-fail (top-1 neutral-4, coin-flip). Adaptive last-100 top-1 is far-ok-1 on every seed.

Learning curve (adaptive, mean success / alpha): window 50 = 0.992 / 2.00, then 1.00 / 2.00 through window 500. Alpha hits the pre-existing cap inside the first 50 tasks.

## Phase B — feedback noise

Baseline does not learn, so its metrics stay at the Phase A baseline row.

| noise | adaptive success | precision | waste | error | delta success vs 0% | final alpha | stability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0% | 0.9992 | 0.6667 | 0.0015 | 0.0008 | 0.0000 | 2.00 | 1.00 |
| 5% | 0.9988 | 0.6667 | 0.0015 | 0.0012 | -0.0004 | 2.00 | 1.00 |
| 10% | 0.9996 | 0.6667 | 0.0016 | 0.0004 | +0.0004 | 2.00 | 1.00 |
| 20% | 0.9996 | 0.6667 | 0.0024 | 0.0004 | +0.0004 | 1.98 | 1.00 |
| 30% | 0.9872 | 0.6667 | 0.0031 | 0.0128 | -0.0120 | 1.98 | 1.00 |

30% seed 11 is the weak cell: success 0.936, error 0.064, final alpha 1.95. Other seeds stay at 1.00. Waste rises slightly with noise. Success does not collapse.

## Phase C — sparse feedback

| feedback | adaptive success | precision | waste | error | delta success vs 100% | final alpha | stability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 100% | 0.9992 | 0.6667 | 0.0015 | 0.0008 | 0.0000 | 2.00 | 1.00 |
| 75% | 0.9984 | 0.6667 | 0.0017 | 0.0016 | -0.0008 | 2.00 | 1.00 |
| 50% | 0.9992 | 0.6667 | 0.0023 | 0.0008 | 0.0000 | 2.00 | 1.00 |
| 25% | 0.9992 | 0.6667 | 0.0051 | 0.0008 | 0.0000 | 2.00 | 1.00 |
| 10% | 0.9992 | 0.6667 | 0.0115 | 0.0008 | 0.0000 | 2.00 | 1.00 |

Success stays above baseline down to 10% feedback. Waste is the metric that moves: 0.0015 at 100% to 0.0115 at 10%. Seed 7 at 10% waste is 0.0573. Minimum availability where adaptive remains useful on success: 10% in this world. That is not a general threshold.

## Interpretation (not a win claim)

1. In this ideal control, adaptive beats relevance-only on success (0.9992 vs 0.0992), precision (0.6667 vs 0.0000), and waste (0.0015 vs 0.6667).
2. Noise through 30% does not remove the gap. The only clear regression is seed 11 at 30% (success 0.936).
3. Sparse feedback through 10% does not remove the success gap. Waste degrades as feedback gets rarer.
4. Instability regime: alpha saturates at the cap 2.0 inside 50 tasks, so later noise or missing labels cannot move the learning curve. This world is too easy to measure a robustness cliff. That is a limitation of the locked control, not a reason to retune it.

Do not start cold-start or distribution-shift until this file is reviewed.
