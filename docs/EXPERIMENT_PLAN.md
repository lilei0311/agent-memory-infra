# Stage 1 Experiment Plan

## Hypothesis

Historical feedback can improve retrieval quality compared with relevance-only ranking.

## Experiment A — Baseline vs Adaptive

Baseline: score = relevance.

Adaptive: score = w_r*relevance + w_u*utility + w_rel*reliability + w_c*context_fit.

Start with transparent weights rather than learned neural parameters.

## Simulation world

Create synthetic tasks with task type, required memory IDs, distractor memories, relevance scores, context-fit scores, reliability, and historical utility. The simulator knows ground-truth useful memories so retrieval quality can be measured without an LLM.

## Controlled variables

Keep identical between baseline and adaptive runs: task sequence, candidate memory set, random seed, K, and simulator rules. Only ranking policy differs.

## Metrics

Primary: task success rate, useful retrieval precision, retrieval waste.

Secondary: memory usefulness rate, correction rate, cumulative reward, policy convergence, and variance across seeds.

## First target

Run 500–1000 simulated tasks per policy and repeat with multiple seeds. Do not optimize for a target percentage before understanding the baseline distribution.

## Failure cases

1. Highly relevant but historically harmful memory.
2. Weakly relevant but repeatedly useful memory.
3. Reliability changing over time.
4. Sparse feedback.
5. Noisy or contradictory feedback.
6. New memories with no history.
7. Distribution shift.
8. Too many retrieved memories causing distraction.

## Acceptance gate

Adaptive policy must show reproducible improvement over relevance-only retrieval on at least one primary metric without unacceptable regression on the others. Negative results are valid and should drive diagnosis rather than selective tuning.

## Stage 1 -> Stage 2 gate

Only after the controlled experiment is understood should we freeze the public Skill interface, add real storage adapters, integrate real Agents, and introduce anonymous evaluation signals. External adoption is not a Stage 1 success criterion.
