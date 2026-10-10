# Agent-agnostic evaluation-signal contract

Revision: evaluation-signals-2026-10-10.1  
Baseline: HEAD `01060ef249112e8731016dedc8fa5833b447c037`  
Status: Stage 2 inventory and minimal stable contract. Does not add a new operation, change policy semantics, or touch frozen assets.

This document inventories signals currently produced or consumed by the repository and defines the smallest stable, agent-agnostic contract for evaluation signals. It is distinct from the public Skill API (`docs/SKILL_API.md`) and from policy-learning feedback.

## Inventory (actual code paths)

### Policy-learning feedback (updates mechanism or policy state)

| Signal | Type / range | Meaning | Source / provenance | Missing / invalid | Code path |
| --- | --- | --- | --- | --- | --- |
| `success` (observe) | `bool \| None` | Binary outcome of the chosen memory on the task | Caller or simulator ground-truth | `None` = unknown; no update to counts or alpha | `src/memory_infra/learner.py:FeedbackLearner.observe` |
| `MemoryItem.success` / `.failure` | non-negative int | Cumulative counts used to compute utility | Updated only by non-None `success` | Unchanged when `success is None` | `src/memory_infra/memory.py:MemoryItem` |
| `utility` | float in [-1, 1] | Laplace-smoothed historical usefulness | Derived from counts | N/A (always defined) | `MemoryItem.utility` |
| `alpha` | float in [0.0, 2.0] | Learned weight on utility | Updated only when policy top differs from baseline and success is not None | Unchanged on None or same-top | `learner.py` + `policy.py:LearnedPolicy` |
| Episode `feedback` / `outcome` | `str \| None` | Optional observation text supplied by caller | Caller on promote | Omitted if absent | `src/memory_infra/graph.py` Episode fields |
| `usefulness_history` | `list[str]` | Mechanism-owned history list | Written by mechanism | Empty until written | `graph.py` MemoryState |

### Evaluation metrics (measurements of outcome; do not update policy)

| Signal / metric | Type / range | Meaning | Source / provenance | Missing / invalid | Code path |
| --- | --- | --- | --- | --- | --- |
| `task_success` | `bool \| None` | Whether the task succeeded | Simulator or future explicit feedback | `None` = unknown; never guessed | `src/memory_infra/trace.py:RetrievalTrace` |
| `user_feedback` | `float \| None` | Optional numeric feedback | Caller | `None` = unknown | `trace.py` |
| `used` | `bool \| None` | Whether the retrieved memory was used | Caller | `None` = unknown | `trace.py` |
| success rate | float [0, 1] | Fraction of tasks with true success | Computed in experiment scripts | N/A | `experiments/baseline_vs_policy.py`, `phase_d.py`, `phase_e.py`, `stage1_robustness.py` |
| useful retrieval precision | float [0, 1] | Fraction of top-K that are useful | Computed in experiments | N/A | `stage1_robustness.py` |
| `target_thread_precision` | float [0, 1] | Attention hit rate | Phase G only | N/A | `experiments/phase_g_attention.py` |
| Outcome fields (`correction_count`, `execution_cost`, `memory_helpful`) | documented only | Protocol shapes | `docs/PROTOCOLS.md` Outcome | Not implemented as live signals | Protocol only |

No standalone evaluator module exists. Metrics are computed inside experiment scripts (see `docs/ROADMAP.md`).

## Contract rules

1. **Separation**  
   Policy-learning feedback (`success` consumed by `FeedbackLearner`, counts, utility, alpha) updates mechanism or policy state.  
   Evaluation metrics (`task_success`, `user_feedback`, `used`, derived rates/precision) measure outcomes and must not be written back into policy or lifecycle state by the evaluation path.

2. **Missing signals**  
   Aligned with `docs/PROTOCOLS.md` and `docs/SKILL_API.md`: a missing signal is unknown (`None`), never guessed or defaulted to success/failure. `FeedbackLearner.observe(..., success=None)` is a no-op for counts and alpha. Skill API does not invent `user_feedback` or `task_success`.

3. **Provenance**  
   - Learning feedback: explicit caller/simulator argument to `observe`.  
   - Evaluation signals: recorded on `RetrievalTrace` when supplied; otherwise absent.  
   - Derived metrics: produced only by experiment runners; not part of the public Skill surface.

4. **Types and ranges**  
   - Binary outcomes: `bool | None`.  
   - Counts: non-negative integers.  
   - Utility: float in [-1, 1].  
   - Alpha: float in [0.0, 2.0] (current bounds).  
   - Rates / precision: float in [0, 1].  
   - Numeric feedback: `float | None`.

5. **Compatibility**  
   Additive optional fields on traces or result documents are compatible. Removing, renaming, or redefining an existing learning-feedback or evaluation signal, or changing the None-is-unknown rule, is breaking and out of scope for this contract. No change to V0.1 policy scoring, Phase H parameters, or frozen assets.

6. **Non-goals**  
   No new Skill operation for feedback. No UI, server, MCP, GraphRAG, vector DB, or telemetry. No modification of frozen V0.1 A/B/C/D/E, Phase G, V0.2 semantics, or locked Phase H results.

## Validation boundary

Existing executable boundaries already cover the critical missing-feedback rule (`tests/test_stage1_feedback.py`). This contract adds a focused assertion that the separation and None-handling remain intact without altering policy or frozen paths.
