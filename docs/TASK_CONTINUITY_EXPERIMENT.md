# Task Continuity Experiment Design

Observation date: 2026-10-18. Research note for Issue #62. No production behavior change. Frozen V0.1 / Phase G / Phase H assets untouched.

## Problem

During a multi-step task the user may switch to an unrelated topic. The Agent can still retrieve the original unfinished work from memory or conversation history, but does not proactively resume it after the interrupting topic ends.

Ordinary retrieval and conversation history are insufficient for reliable resumption. An explicit task-state record (progress, interruption reason, blocker, resumption condition, validity) may be needed.

## Hypothesis

- **Baseline:** Skill retrieve + conversation history only. No persisted task state beyond ordinary memory events.
- **Intervention:** Persist a minimal task record (status, progress, interruption, blocker, resumption condition) via existing Thread / Event mechanisms or a thin wrapper, then let attention/Harness decide resumption.

Responsibility split remains open; this experiment only measures whether an explicit record improves recovery metrics.

## Scenarios (minimal, synthetic)

All scenarios use invented fixture text. No real user data.

1. **Simple switch and return**
   - Start multi-step task A (e.g., "write report outline").
   - User switches to unrelated topic B.
   - After B ends, measure whether A is resumed without an explicit user request.

2. **Temporary blocker**
   - Task A blocked on external input.
   - Switch to B; later unblock A.
   - Measure recovery after blocker removal.

3. **Priority change / cancellation**
   - User explicitly cancels or deprioritizes A during the switch.
   - Measure inappropriate-resumption rate (must stay low).

4. **Duplicate execution**
   - Same task partially completed; switch and return.
   - Measure repeated work.

## Metrics

- Correct task recovery rate (resumed the right unfinished task).
- Resumption precision / inappropriate-resumption rate.
- Recovery after blocker removal.
- Duplicate / repeated execution rate.
- End-to-end task completion rate.

Acceptance thresholds (initial, subject to revision):

- Recovery rate > baseline by at least 20 percentage points on the simple-switch scenario.
- Inappropriate-resumption rate ≤ 5% on cancellation scenarios.
- No increase in duplicate execution.

## Implementation notes

- Use existing SkillEntrypoint, Thread, Event, and retrieve APIs.
- Do not modify V0.1 A/B/C/D/E, Phase G, or locked Phase H parameters.
- Keep the experiment in `experiments/` and results under `experiments/results/`.
- A skeleton runner can be added later; this document is the design only.

## Next step

Implement the smallest reproducible runner that scores the four scenarios for baseline vs a thin task-state wrapper, using only public Skill and graph surfaces. Record exact SHA and literal outputs. Do not claim improvement until numbers exist.
