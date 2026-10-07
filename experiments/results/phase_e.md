# Issue #1 Phase E

Diagnostic only. A/B/C/D were not modified. Alpha cap was not raised. No new exploration rule.

Locked: seeds 7/11/19/23/42, tasks 500, pool 50, K=3, alpha0=0.5, step=0.05, cap=2.0, window=50.
World matches Phase D2: p in [0.3, 0.9], late p = 1.2 - p. V0.1 is infinite half-life.
Decay recomputes utility from event weights 0.5 ** ((t - t_obs) / half_life). Alpha rule is unchanged.
Reach/exceed use post-switch windows only. Locked means post-switch top-1 mode share >= 0.8.

## E1 staleness severity

| switch | pre baseline | pre adaptive | post baseline | post adaptive | post delta |
| --- | --- | --- | --- | --- | --- |
| 100 | 0.6340 | 0.8000 | 0.6160 | 0.5840 | -0.0320 |
| 200 | 0.6110 | 0.7900 | 0.6280 | 0.5307 | -0.0973 |
| 250 | 0.6128 | 0.7920 | 0.6360 | 0.5264 | -0.1096 |
| 300 | 0.6073 | 0.7840 | 0.6490 | 0.5030 | -0.1460 |
| 400 | 0.6180 | 0.7870 | 0.6280 | 0.4440 | -0.1840 |

## E2 recovery

| switch | min post adaptive | mean reach window | mean exceed window | mean alpha drop tasks | seeds alpha to 0 | final recovered | post-mean recovered |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 100 | 0.3120 | 230.0000 | 350.0000 | 217.0000 | 1/5 | 5/5 | 3/5 |
| 200 | 0.3040 | 320.0000 | none | 311.0000 | 2/5 | 5/5 | 3/5 |
| 250 | 0.3240 | 360.0000 | none | 338.5000 | 2/5 | 5/5 | 3/5 |
| 300 | 0.3840 | 410.0000 | none | 399.5000 | 2/5 | 5/5 | 3/5 |
| 400 | 0.4080 | 450.0000 | none | none | 0/5 | 3/5 | 3/5 |

Switch 250 per seed, V0.1:

| seed | pre a | post a | post b | min post | reach | exceed | peak alpha | drop tasks | final recovered | lock share | post changes | post unique | post disagree |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7 | 0.8480 | 0.5800 | 0.8640 | 0.3200 | 450 | None | 2.0000 | 343 | True | 0.5520 | 1 | 2 | 0.5520 |
| 11 | 0.6440 | 0.5560 | 0.5560 | 0.3600 | 300 | None | 0.5000 | None | True | 1.0000 | 0 | 1 | 0.0000 |
| 19 | 0.7960 | 0.5080 | 0.5080 | 0.4200 | 300 | None | 0.5000 | None | True | 1.0000 | 0 | 1 | 0.0000 |
| 23 | 0.8800 | 0.3800 | 0.3800 | 0.2000 | 300 | None | 0.5000 | None | True | 1.0000 | 0 | 1 | 0.0000 |
| 42 | 0.7920 | 0.6080 | 0.8720 | 0.3200 | 450 | None | 2.0000 | 334 | True | 0.5000 | 1 | 2 | 0.5000 |

## E3 decay diagnostic, switch 250

| half-life | pre adaptive | post baseline | post adaptive | post delta | min post | seeds alpha to 0 | final recovered | post-mean recovered |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| infinite | 0.7920 | 0.6360 | 0.5264 | -0.1096 | 0.3240 | 2/5 | 5/5 | 3/5 |
| 500 | 0.7920 | 0.6360 | 0.5272 | -0.1088 | 0.3240 | 1/5 | 5/5 | 3/5 |
| 250 | 0.7920 | 0.6360 | 0.5272 | -0.1088 | 0.3240 | 1/5 | 5/5 | 3/5 |
| 100 | 0.7920 | 0.6360 | 0.5432 | -0.0928 | 0.3240 | 1/5 | 5/5 | 3/5 |
| 50 | 0.7904 | 0.6360 | 0.6136 | -0.0224 | 0.3240 | 0/5 | 3/5 | 2/5 |

Seed 7 recovery windows, switch 250:

| half-life | window | baseline | adaptive | selected | utility | score | alpha | disagree | unique |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| infinite | 250 | 0.4600 | 0.8200 | m0048 | 0.7201 | 2.3951 | 2.0000 | 1.0000 | 1 |
| infinite | 300 | 0.8000 | 0.3400 | m0048 | 0.6159 | 1.8540 | 1.2000 | 1.0000 | 1 |
| infinite | 350 | 0.8600 | 0.3200 | m0048 | 0.4754 | 1.3138 | 0.3000 | 1.0000 | 1 |
| infinite | 400 | 0.9400 | 0.5200 | m0048 | 0.3785 | 1.1312 | 0.0000 | 0.7600 | 2 |
| infinite | 450 | 0.8800 | 0.8800 | m0000 | 0.5836 | 0.9998 | 0.0000 | 0.0000 | 1 |
| infinite | 500 | 0.8400 | 0.8400 | m0000 | 0.7364 | 0.9998 | 0.0000 | 0.0000 | 1 |
| 500 | 250 | 0.4600 | 0.8200 | m0048 | 0.7139 | 2.3827 | 2.0000 | 1.0000 | 1 |
| 500 | 300 | 0.8000 | 0.3400 | m0048 | 0.5929 | 1.8229 | 1.2000 | 1.0000 | 1 |
| 500 | 350 | 0.8600 | 0.3200 | m0048 | 0.4292 | 1.2817 | 0.3000 | 1.0000 | 1 |
| 500 | 400 | 0.9400 | 0.5400 | m0048 | 0.3736 | 1.1166 | 0.0500 | 0.7400 | 2 |
| 500 | 450 | 0.8800 | 0.8800 | m0000 | 0.6176 | 1.0307 | 0.0500 | 0.0000 | 1 |
| 500 | 500 | 0.8400 | 0.8400 | m0000 | 0.7503 | 1.0374 | 0.0500 | 0.0000 | 1 |
| 250 | 250 | 0.4600 | 0.8200 | m0048 | 0.7075 | 2.3700 | 2.0000 | 1.0000 | 1 |
| 250 | 300 | 0.8000 | 0.3400 | m0048 | 0.5687 | 1.7902 | 1.2000 | 1.0000 | 1 |
| 250 | 350 | 0.8600 | 0.3200 | m0048 | 0.3813 | 1.2484 | 0.3000 | 1.0000 | 1 |
| 250 | 400 | 0.9400 | 0.5400 | m0048 | 0.3488 | 1.0969 | 0.0500 | 0.7400 | 2 |
| 250 | 450 | 0.8800 | 0.8800 | m0000 | 0.6298 | 1.0313 | 0.0500 | 0.0000 | 1 |
| 250 | 500 | 0.8400 | 0.8400 | m0000 | 0.7571 | 1.0377 | 0.0500 | 0.0000 | 1 |
| 100 | 250 | 0.4600 | 0.8200 | m0048 | 0.6879 | 2.3312 | 2.0000 | 1.0000 | 1 |
| 100 | 300 | 0.8000 | 0.3400 | m0048 | 0.4924 | 1.6872 | 1.2000 | 1.0000 | 1 |
| 100 | 350 | 0.8600 | 0.3200 | m0048 | 0.2378 | 1.1484 | 0.3000 | 1.0000 | 1 |
| 100 | 400 | 0.9400 | 0.6000 | m0048 | 0.3184 | 1.0797 | 0.2000 | 0.6800 | 2 |
| 100 | 450 | 0.8800 | 0.8800 | m0000 | 0.6724 | 1.1343 | 0.2000 | 0.0000 | 1 |
| 100 | 500 | 0.8400 | 0.8400 | m0000 | 0.7728 | 1.1544 | 0.2000 | 0.0000 | 1 |
| 50 | 250 | 0.4600 | 0.8200 | m0048 | 0.6571 | 2.2701 | 2.0000 | 1.0000 | 1 |
| 50 | 300 | 0.8000 | 0.3400 | m0048 | 0.3697 | 1.5219 | 1.2000 | 1.0000 | 1 |
| 50 | 350 | 0.8600 | 0.6000 | m0000 | 0.4097 | 1.2870 | 0.7000 | 0.3600 | 2 |
| 50 | 400 | 0.9400 | 0.9400 | m0000 | 0.7465 | 1.5224 | 0.7000 | 0.0000 | 1 |
| 50 | 450 | 0.8800 | 0.8800 | m0000 | 0.7503 | 1.5251 | 0.7000 | 0.0000 | 1 |
| 50 | 500 | 0.8400 | 0.8400 | m0000 | 0.7871 | 1.5508 | 0.7000 | 0.0000 | 1 |

## E4 exploration diagnosis, V0.1

| switch | seeds locked | mean lock share | mean post top1 changes | mean post unique | mean post disagree |
| --- | --- | --- | --- | --- | --- |
| 100 | 2/5 | 0.7500 | 1.0000 | 1.8000 | 0.2500 |
| 200 | 3/5 | 0.8053 | 0.4000 | 1.4000 | 0.2053 |
| 250 | 3/5 | 0.8104 | 0.4000 | 1.4000 | 0.2104 |
| 300 | 3/5 | 0.8850 | 0.4000 | 1.4000 | 0.2850 |
| 400 | 5/5 | 1.0000 | 0.0000 | 1.0000 | 0.4000 |

## Reading

E1 post delta is the staleness severity at each switch. A negative delta means historical utility hurt after the flip.
E2 recovery is a post-switch window at or above that window's baseline, not a claim that the old memory became valid again.
E3 infinite is V0.1. Shorter half-life is a diagnostic scan, not a selected algorithm.
E4 lock and low disagreement mean the current rule cannot leave a memory unless baseline disagreement and failures pull alpha down.
Do not start cold-start, distribution-shift, or Stage 2 from this run.

Switch 250 infinite matches Phase D2: pre adaptive 0.7920, post adaptive 0.5264, post baseline 0.6360.

Reach on seeds 11/19/23 is not recovery. Those seeds never disagree with relevance, so adaptive equals baseline and the first post window counts as reached. The seeds that actually locked a stale memory are 7 and 42. They return to baseline only at window 450, after alpha hits 0, and they do not exceed baseline.

E3 does not remove the stale-memory gap. Half-life 500/250/100 leave post delta at about -0.11 to -0.09. Half-life 50 reduces it to -0.0224 and moves seed 7 off m0048 at window 350 instead of 450, but post adaptive still does not beat post baseline. Decay alone is not a selected fix.
