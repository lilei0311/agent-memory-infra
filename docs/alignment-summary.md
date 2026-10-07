# Alignment Summary (fix/align-code-with-protocols)

## Changes

1. **RetrievalTrace** (trace.py) — now one record per retrieved memory:
   `trace_id`, `task_id`, `memory_id`, `retrieved`, `rank`, `mode`,
   `policy_version`, plus optional `used` / `task_success` / `user_feedback`.
   Missing signals stay `None`, never guessed. Append-only; no raw conversation.

2. **FeedbackLearner** (learner.py) — alpha nudges only when the policy's
   top pick differs from the baseline's: raised on success, lowered on
   failure. Same pick leaves alpha unchanged.

3. **MemoryItem.utility** (memory.py) — Laplace smoothing:
   `(success - failure) / (success + failure + 1)`.
   A single failure can no longer erase a long success history.

4. **LearnedPolicy** (policy.py) — v0.1 is the two-term form
   `similarity + alpha * utility`. The four-weight target
   (relevance + utility + reliability + context_fit) remains documented.

5. **retrieve()** (retrieval.py) — returns `list[RetrievalTrace]` with
   `task_id` and `policy_version`.

6. **Tests** — learner condition, unchanged-on-same-pick, failure lowers
   alpha, smoothed utility.

## Expected experiment output

```
baseline ['near-fail'] [0.995]
policy   ['far-ok']    [1.3]
alpha    0.85
```
