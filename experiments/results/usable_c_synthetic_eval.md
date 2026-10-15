# Synthetic use-case eval

Labels in this file are invented fixture text. This run did not read a home directory, a personal database, or a private export.

Command: `python3 experiments/synthetic_usecase_eval.py`

Pass condition: the script finishes and writes this file. Adaptive hit@k is not required to exceed baseline.

Policy layer: baseline = cosine, adaptive = cosine + 0.5 * utility, k=3. Alpha is fixed; the online learner is not updated. The scored store is the near-deduped corpus (`skip`, normalized text) unless a row says raw.

Skill API: every import in this run used `redact=False`. `SkillEntrypoint` still defaults to `redact=False`; this eval does not change that. `context_budget=3`. `policy="none"` is recency order. `policy="automatic"` adds attention weight. With no threads every attention weight is 0, so tied scores break on event-id text order. That tie break is not a query match. The query string is not a similarity feature (`query_used_for_ranking` is false).

## Corpus

| id | utility | text |
| --- | --- | --- |
| pref-confirm | 0.889 | The workspace prefers explicit confirmation before import. |
| pref-distractor | -0.857 | The workspace prefers posting standup notes in the team channel. |
| decision-backup | 0.833 | 2026-03-18: Decision: copy a quiescent snapshot with sqlite3 .backup before a read-only import. |
| decision-direct | -0.800 | 2026-01-04: Decision: open the live database file directly when importing messages. |
| theme-stale | 0.000 | 2026-01-02: The workspace prefers a dark editor theme. |
| theme-current | 0.000 | 2026-06-18: The workspace prefers a light editor theme. The January dark-theme note is stale. |
| unique-fact | 0.500 | Unique markdown fact: fixtures are checked in on purpose. |
| pref-confirm-dup | 0.667 | the workspace prefers explicit confirmation before import. |

Raw store size 8. Deduped store size 7. `pref-confirm-dup` is the near-copy that dedup removes.

## Policy hit@k (deduped store)

| task | expected | baseline top | adaptive top | baseline hit@1 | adaptive hit@1 | baseline hit@3 | adaptive hit@3 | hit@1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preference_recall | pref-confirm | pref-distractor, pref-confirm, unique-fact | pref-confirm, pref-distractor, decision-backup | 0 | 1 | 1 | 1 | adaptive higher |
| prior_decision | decision-backup | decision-direct, decision-backup, unique-fact | decision-backup, decision-direct, pref-confirm | 0 | 1 | 1 | 1 | adaptive higher |
| duplicate_suppression | unique-fact | pref-distractor, pref-confirm, unique-fact | pref-confirm, pref-distractor, decision-backup | 0 | 0 | 1 | 0 | tie |
| stale_contradiction | theme-current | theme-stale, theme-current, unique-fact | theme-stale, theme-current, pref-confirm | 0 | 0 | 1 | 1 | tie |

Mean hit@1 baseline 0.00, adaptive 0.50. Mean hit@3 baseline 1.00, adaptive 0.75.
hit@1 counts on the four tasks: adaptive higher 2, baseline higher 0, tie 2.
hit@3 counts on the four tasks: adaptive higher 0, baseline higher 1, tie 3.

Reading, from this seed and these vectors:

- Preference recall: the nearer distractor has a failing history. Baseline hit@1 stays on that distractor. Adaptive hit@1 moves to `pref-confirm`.
- Prior decision: baseline hit@1 stays on the older direct-open decision (higher cosine, failing history). Adaptive hit@1 moves to `decision-backup`.
- Duplicate suppression: expected id is `unique-fact` under the preference probe, after near-dup collapse. Baseline hit@3 includes it. Adaptive hit@3 does not, because the backup decision's utility outranks that fact. Adaptive does not win this task.
- Stale/contradiction: both dated theme bullets have utility 0, so the adaptive term does not reorder them. Top-1 is `theme-stale` for both policies, so expected `theme-current` is hit@1 = 0 and hit@3 = 1. Dated text alone does not demote the stale bullet.

Adaptive does not beat baseline on every task. That is the result.

## Duplicate counts

Raw preference-family ids in the top 3: baseline 2, adaptive 2.
Deduped preference-family ids in the top 3: baseline 1, adaptive 1.
Raw `unique-fact` hit@3: baseline 0, adaptive 0. Both miss while the near-copy occupies a slot.
Item dedup is what removes the extra copy. The adaptive score does not.

## Skill API retrieve

Fixtures: `tests/fixtures/synthetic/MEMORY.md` and `dated-notes.md`. Import redaction stayed off on every row.

| scenario | policy | created | skipped | selected labels | unique-fact | theme-stale | theme-current | decision-backup |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| memory-dedup-off | none | 6 | 0 | pref-confirm, pref-near, pref-near-ws | 0 | 0 | 0 | 0 |
| memory-dedup-off | automatic | 6 | 0 | standup, unique-fact, pref-confirm | 1 | 0 | 0 | 0 |
| memory-dedup-on | none | 3 | 3 | pref-confirm, standup, unique-fact | 1 | 0 | 0 | 0 |
| memory-dedup-on | automatic | 3 | 3 | pref-confirm, standup, unique-fact | 1 | 0 | 0 | 0 |
| dated-notes | none | 4 | 0 | theme-stale, theme-current, decision-direct | 0 | 1 | 1 | 0 |
| dated-notes | automatic | 4 | 0 | theme-stale, theme-current, decision-direct | 0 | 1 | 1 | 0 |
| dated-notes-after-decay | none | 4 | 0 | theme-current, decision-direct, decision-backup | 0 | 0 | 1 | 1 |
| dated-notes-after-decay | automatic | 4 | 0 | theme-current, decision-direct, decision-backup | 0 | 0 | 1 | 1 |

On `memory-dedup-off`, recency order keeps the first three confirmation lines and drops `unique-fact`. `automatic` selects a different trio because tied attention scores sort by event id, which is not chronological once ids pass 9. That is why `automatic` can list `unique-fact` without dedup. It did not match the query.

On `memory-dedup-on`, near-duplicate confirmation and standup lines collapse (`skip`). Three observations fit in the budget, including `unique-fact`, for both policies.

On `dated-notes`, both policies keep the first three bullets and drop `decision-backup`. The stale theme stays. After `contradict` (both observations kept) and one `decay` on the stale theme event, both policies drop `theme-stale` and include `decision-backup`. The date string did not do that. The decay signal did. The two policies still agree.

Skill retrieve does not implement the cosine-plus-utility score. Use the policy-layer table for that comparison.
