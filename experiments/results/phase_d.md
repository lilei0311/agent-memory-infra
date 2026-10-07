# Issue #1 Phase D

A/B/C results were not modified. Alpha cap was not raised.

Locked config: seeds 7/11/19/23/42, tasks 500, K=3, alpha0=0.5, step=0.05, cap=2.0, window=50.
Success probability is continuous in [0.3, 0.9], independent of cosine. Initial counts are 0.
Baseline and adaptive share the candidate set, seed, and Bernoulli table. Baseline store is not updated.
D1/D2 pool is 50. D2 flips p to 1.2-p at task 250. D3 uses the stationary D1 rule.

## D1 continuous utility

mean baseline 0.6148 adaptive 0.7812
mean final alpha 1.0800

| seed | baseline | adaptive | final alpha | sat task | learn window | degrade window |
| --- | --- | --- | --- | --- | --- | --- |
| 7 | 0.4180 | 0.8140 | 1.9500 | 44 | 50 | 350 |
| 11 | 0.6340 | 0.6340 | 0.5000 | None | None | 150 |
| 19 | 0.7980 | 0.7980 | 0.5000 | None | None | 100 |
| 23 | 0.8780 | 0.8780 | 0.5000 | None | None | 300 |
| 42 | 0.3460 | 0.7820 | 1.9500 | 40 | 50 | 100 |

Seed 7 windows:

| window | baseline | adaptive | selected | utility | score | alpha |
| --- | --- | --- | --- | --- | --- | --- |
| 50 | 0.4600 | 0.8400 | m0048 | 0.6046 | 1.7132 | 2.0000 |
| 100 | 0.3400 | 0.8600 | m0048 | 0.7973 | 2.5540 | 2.0000 |
| 150 | 0.4200 | 0.8600 | m0048 | 0.7672 | 2.4925 | 2.0000 |
| 200 | 0.3200 | 0.8600 | m0048 | 0.7505 | 2.4615 | 1.9500 |
| 250 | 0.4600 | 0.8200 | m0048 | 0.7201 | 2.3951 | 2.0000 |
| 300 | 0.4000 | 0.8000 | m0048 | 0.7133 | 2.3837 | 1.9500 |
| 350 | 0.5200 | 0.7200 | m0048 | 0.6725 | 2.2951 | 1.9500 |
| 400 | 0.4600 | 0.7600 | m0048 | 0.6641 | 2.2599 | 2.0000 |
| 450 | 0.3400 | 0.7800 | m0048 | 0.6446 | 2.2465 | 1.9500 |
| 500 | 0.4600 | 0.8400 | m0048 | 0.6394 | 2.2387 | 1.9500 |

## D2 non-stationary

mean baseline 0.6244 adaptive 0.6592
pre switch baseline/adaptive 0.6128 / 0.7920
post switch baseline/adaptive 0.6360 / 0.5264

| seed | baseline | adaptive | pre a | post a | sat task | learn window | degrade window |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 7 | 0.6320 | 0.7140 | 0.8480 | 0.5800 | 44 | 50 | 300 |
| 11 | 0.6000 | 0.6000 | 0.6440 | 0.5560 | None | None | 150 |
| 19 | 0.6520 | 0.6520 | 0.7960 | 0.5080 | None | None | 100 |
| 23 | 0.6300 | 0.6300 | 0.8800 | 0.3800 | None | None | 300 |
| 42 | 0.6080 | 0.7000 | 0.7920 | 0.6080 | 40 | 50 | 100 |

Seed 7 windows:

| window | baseline | adaptive | selected | utility | score | alpha |
| --- | --- | --- | --- | --- | --- | --- |
| 50 | 0.4600 | 0.8400 | m0048 | 0.6046 | 1.7132 | 2.0000 |
| 100 | 0.3400 | 0.8600 | m0048 | 0.7973 | 2.5540 | 2.0000 |
| 150 | 0.4200 | 0.8600 | m0048 | 0.7672 | 2.4925 | 2.0000 |
| 200 | 0.3200 | 0.8600 | m0048 | 0.7505 | 2.4615 | 1.9500 |
| 250 | 0.4600 | 0.8200 | m0048 | 0.7201 | 2.3951 | 2.0000 |
| 300 | 0.8000 | 0.3400 | m0048 | 0.6159 | 1.8540 | 1.2000 |
| 350 | 0.8600 | 0.3200 | m0048 | 0.4754 | 1.3138 | 0.3000 |
| 400 | 0.9400 | 0.5200 | m0048 | 0.3785 | 1.1312 | 0.0000 |
| 450 | 0.8800 | 0.8800 | m0000 | 0.5836 | 0.9998 | 0.0000 |
| 500 | 0.8400 | 0.8400 | m0000 | 0.7364 | 0.9998 | 0.0000 |

## D3 pool sweep

| pool | baseline | adaptive | delta | mean sat task | seeds saturated |
| --- | --- | --- | --- | --- | --- |
| 10 | 0.6012 | 0.6008 | -0.0004 | nan | 0/5 |
| 50 | 0.6148 | 0.7812 | 0.1664 | 42.0000 | 2/5 |
| 100 | 0.5884 | 0.7604 | 0.1720 | 52.0000 | 2/5 |
| 500 | 0.6028 | 0.7360 | 0.1332 | 88.6667 | 3/5 |
| 1000 | 0.5912 | 0.7552 | 0.1640 | 95.3333 | 3/5 |

## Reading

Discrimination is whether adaptive success separates from baseline on the same Bernoulli table, not whether alpha moves.
Alpha saturation remains a limitation of the current rule. Cap was not raised.
D2 post-switch drop, if present, is historical utility becoming stale. Cumulative counts do not forget.
D3 delta versus pool size is the distractor degradation curve.
Do not start cold-start, distribution-shift, or Stage 2 from this run.

## Analysis

Learning is not uniform. Under the current rule alpha moves only when the policy top-1 differs from the relevance top-1. Seeds 11/19/23 stay at alpha 0.5 and adaptive success equals baseline: the relevance winner was already a high-p item, so the rule never received a disagreement to learn from. Seeds 7 and 42 separate in the first window (end 50) and alpha hits the cap at tasks 44 and 40. That is the same saturation limitation as A/B/C, now on a continuous band. Cap was not raised.

D1 seed-7 curve stays on m0048 after the first window. Later window drops of about 0.08-0.14 are inside Bernoulli noise of a p around 0.8, not a clear policy collapse. Mean D1 gap is +0.1664, carried by 2/5 seeds.

D2 pre-switch adaptive mean 0.7920 falls to 0.5264 after the flip, below the post-switch baseline 0.6360. Cumulative utility keeps the stale winner. Seed 7 alpha falls from 2.0 to 0.0 across windows 300-400, still selecting m0048 while it fails, then switches to m0000 only at window 450 once alpha is 0. The rule can unlearn, but only after a long failure streak, and it does not recover above baseline in the second half.

D3 is not a monotone distractor collapse. Pool 10 delta is -0.0004 (0/5 saturated). Pools 50/100/500/1000 deltas are +0.1664/+0.1720/+0.1332/+0.1640. Larger pools delay saturation (mean sat task 42 to 95) but do not remove the two-seed split. Distractors did not erase the gap in this locked setup; they also did not create a gap where relevance was already good.

Window curves: experiments/results/phase_d_curves.csv.
