# Stage 5 integration evidence

Executed in a worktree based on `99903ce3e0cfde5bbcfe4c6638ffa1d694d1a9b8` with the Stage 5 contract and tests present and uncommitted. Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H results were not edited.

Changed-file scope of this commit:

- `docs/STAGE5_INTEGRATION_BOUNDARY.md`
- `tests/test_stage5_integration.py`
- `experiments/results/stage5_integration.md`

No V0.2 transition, store, or adapter code change. Phase H config was not retuned.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
................................................................         [100%]
64 passed in 0.35s
```

Baseline before this commit was 61 passed. The three added tests are the Stage 5 matrix.

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

## Stage 5 acceptance repair

Parent HEAD at execution: `0b609c0a6169e02585615a1c555fa9eda4b06ec8`.

The caller-boundary test was repaired in the worktree before these commands. Each forbidden field was sent on an otherwise valid `promote` request that used a point created by `observe`. Service-owned fields must raise `SnapshotError` matching `caller cannot own mechanism fields` and name the field. Signal-owned fields must raise `BoundaryError` matching `caller cannot set mechanism-owned fields` and name the field. Any rejection is no longer accepted.

Changed-file scope of this commit:

- `tests/test_stage5_integration.py`
- `experiments/results/stage5_integration.md`

No V0.2 transition, store, or adapter code change. Phase H config was not retuned. V0.1 scripts and historical Phase H results were not edited.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
................................................................         [100%]
64 passed in 0.41s
```

### experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

## Stage 5 exact-HEAD acceptance rerun

Executed at exact HEAD `58309209637147b4c7507c3fb9dcee94e492e0f6` (clean checkout of that commit). Commands were run against this commit, not against parent `0b609c0a6169e02585615a1c555fa9eda4b06ec8`. No source, test, V0.1, Phase G, or locked Phase H config/result files were edited before the run. Seeds, budget, and policy were not changed.

Changed-file scope of this commit:

- `experiments/results/stage5_integration.md`

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
................................................................         [100%]
64 passed in 0.36s
```

pytest exit code: 0

### experiment output

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
{"deterministic_replay": {"digests": ["3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1", "8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405", "3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9", "e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-2", "target_id": "ev-7-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-7-2", "target_id": "ev-7-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-7-4", "target_id": "ev-7-2"}], "trace_digest": "e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9", "weaken": true}, "seed": 7, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-2", "target_id": "ev-7-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-5", "target_id": "ev-7-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-7-3", "target_id": "th-7-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-7-3", "target_id": "th-7-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-7-14", "target_id": "ev-7-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405"}}
{"deterministic_replay": {"digests": ["01413a56769a6cb917b0786b2ec846601ad53867c5c495effcaa797c1168abf0", "de5398c779421fe66e123af08db10cf11871c2a54c3f1d4ac2dc5b2c010296b3", "0808c67e8643d072ca216bb2d71220a80a3ece65131070997ceb5e866dc6dbf4", "0232fa7946341225313a32bfeaee020635457a2c9f140ce46bef8cfba9a2a038"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "01413a56769a6cb917b0786b2ec846601ad53867c5c495effcaa797c1168abf0"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-2", "target_id": "ev-11-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-11-2", "target_id": "ev-11-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-11-4", "target_id": "ev-11-2"}], "trace_digest": "0232fa7946341225313a32bfeaee020635457a2c9f140ce46bef8cfba9a2a038"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "0808c67e8643d072ca216bb2d71220a80a3ece65131070997ceb5e866dc6dbf4", "weaken": true}, "seed": 11, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-2", "target_id": "ev-11-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-5", "target_id": "ev-11-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-11-3", "target_id": "th-11-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-11-3", "target_id": "th-11-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-11-14", "target_id": "ev-11-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "de5398c779421fe66e123af08db10cf11871c2a54c3f1d4ac2dc5b2c010296b3"}}
{"deterministic_replay": {"digests": ["a722e372b110c746b829f878c08fef136cac99367bcd639c5fb41e9918d8a4ea", "6f49834c699e9d7ff149b614f82e9bca726e58095085fd52470bcdc96a3ba51c", "a8147a9e1b08ebeccafc588c51543debeafb119a089ee6420365abb7bda061b5", "01562d0a40ae43b5de969e2aa59c3c469af615f6381ba0bd6274b59ea75f6773"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "a722e372b110c746b829f878c08fef136cac99367bcd639c5fb41e9918d8a4ea"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-2", "target_id": "ev-19-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-19-2", "target_id": "ev-19-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-19-4", "target_id": "ev-19-2"}], "trace_digest": "01562d0a40ae43b5de969e2aa59c3c469af615f6381ba0bd6274b59ea75f6773"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "a8147a9e1b08ebeccafc588c51543debeafb119a089ee6420365abb7bda061b5", "weaken": true}, "seed": 19, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-2", "target_id": "ev-19-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-5", "target_id": "ev-19-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-19-3", "target_id": "th-19-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-19-3", "target_id": "th-19-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-19-14", "target_id": "ev-19-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "6f49834c699e9d7ff149b614f82e9bca726e58095085fd52470bcdc96a3ba51c"}}
trace_artifact /tmp/agent-memory-infra/experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
```

experiment exit code: 0

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

## Stage 5 escalation exact-HEAD execution

Issue #20 required a fresh execution at exact HEAD `58309209637147b4c7507c3fb9dcee94e492e0f6`. This section records that run. It does not copy or relabel the parent-HEAD output from `0b609c0a6169e02585615a1c555fa9eda4b06ec8`, and it does not treat commit `742a8fa` as the execution record.

Verified execution HEAD before commands: `58309209637147b4c7507c3fb9dcee94e492e0f6`.
Checkout was clean except for test bytecode created by the run. No source, test, V0.1, Phase G, or locked Phase H config/result files were edited before the run. Seeds, budget, and policy were not changed.

Changed-file scope of this commit:

- `experiments/results/stage5_integration.md`

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
................................................................         [100%]
64 passed in 0.28s
```

pytest exit code: 0

### experiment output

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
{"deterministic_replay": {"digests": ["3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1", "8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405", "3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9", "e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-2", "target_id": "ev-7-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-7-2", "target_id": "ev-7-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-7-4", "target_id": "ev-7-2"}], "trace_digest": "e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9", "weaken": true}, "seed": 7, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-2", "target_id": "ev-7-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-5", "target_id": "ev-7-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-7-3", "target_id": "th-7-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-7-3", "target_id": "th-7-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-7-14", "target_id": "ev-7-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405"}}
{"deterministic_replay": {"digests": ["01413a56769a6cb917b0786b2ec846601ad53867c5c495effcaa797c1168abf0", "de5398c779421fe66e123af08db10cf11871c2a54c3f1d4ac2dc5b2c010296b3", "0808c67e8643d072ca216bb2d71220a80a3ece65131070997ceb5e866dc6dbf4", "0232fa7946341225313a32bfeaee020635457a2c9f140ce46bef8cfba9a2a038"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "01413a56769a6cb917b0786b2ec846601ad53867c5c495effcaa797c1168abf0"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-2", "target_id": "ev-11-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-11-2", "target_id": "ev-11-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-11-4", "target_id": "ev-11-2"}], "trace_digest": "0232fa7946341225313a32bfeaee020635457a2c9f140ce46bef8cfba9a2a038"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "0808c67e8643d072ca216bb2d71220a80a3ece65131070997ceb5e866dc6dbf4", "weaken": true}, "seed": 11, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-2", "target_id": "ev-11-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-5", "target_id": "ev-11-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-11-3", "target_id": "th-11-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-11-3", "target_id": "th-11-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-11-14", "target_id": "ev-11-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "de5398c779421fe66e123af08db10cf11871c2a54c3f1d4ac2dc5b2c010296b3"}}
{"deterministic_replay": {"digests": ["a722e372b110c746b829f878c08fef136cac99367bcd639c5fb41e9918d8a4ea", "6f49834c699e9d7ff149b614f82e9bca726e58095085fd52470bcdc96a3ba51c", "a8147a9e1b08ebeccafc588c51543debeafb119a089ee6420365abb7bda061b5", "01562d0a40ae43b5de969e2aa59c3c469af615f6381ba0bd6274b59ea75f6773"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "a722e372b110c746b829f878c08fef136cac99367bcd639c5fb41e9918d8a4ea"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-2", "target_id": "ev-19-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-19-2", "target_id": "ev-19-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-19-4", "target_id": "ev-19-2"}], "trace_digest": "01562d0a40ae43b5de969e2aa59c3c469af615f6381ba0bd6274b59ea75f6773"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "a8147a9e1b08ebeccafc588c51543debeafb119a089ee6420365abb7bda061b5", "weaken": true}, "seed": 19, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-2", "target_id": "ev-19-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-5", "target_id": "ev-19-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-19-3", "target_id": "th-19-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-19-3", "target_id": "th-19-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-19-14", "target_id": "ev-19-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "6f49834c699e9d7ff149b614f82e9bca726e58095085fd52470bcdc96a3ba51c"}}
trace_artifact /tmp/agent-memory-infra/experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
```

experiment exit code: 0

sha256sum of experiments/results/phase_h_trace.json after this run: `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c  experiments/results/phase_h_trace.json`

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

Stage 5 is not declared PASS. Issues #18 and #20 remain open.

## Stage 5 exact-HEAD acceptance rerun at 5413dc1

Executed at exact HEAD `5413dc1498d99c2a437ac1476a89b05b032344cc` (clean checkout of that commit). Commands were run against this commit, not against parent `58309209637147b4c7507c3fb9dcee94e492e0f6`. No source, test, V0.1, Phase G, or locked Phase H config/result files were edited before the run. Seeds, budget, and policy were not changed. This record does not declare Stage 5 PASS.

Changed-file scope of this commit:

- `experiments/results/stage5_integration.md`

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
................................................................         [100%]
64 passed in 0.38s
```

pytest exit code: 0

### experiment output

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
{"deterministic_replay": {"digests": ["3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1", "8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405", "3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9", "e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-2", "target_id": "ev-7-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-7-2", "target_id": "ev-7-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-7-4", "target_id": "ev-7-2"}], "trace_digest": "e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9", "weaken": true}, "seed": 7, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-2", "target_id": "ev-7-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-5", "target_id": "ev-7-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-7-3", "target_id": "th-7-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-7-3", "target_id": "th-7-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-7-14", "target_id": "ev-7-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405"}}
{"deterministic_replay": {"digests": ["01413a56769a6cb917b0786b2ec846601ad53867c5c495effcaa797c1168abf0", "de5398c779421fe66e123af08db10cf11871c2a54c3f1d4ac2dc5b2c010296b3", "0808c67e8643d072ca216bb2d71220a80a3ece65131070997ceb5e866dc6dbf4", "0232fa7946341225313a32bfeaee020635457a2c9f140ce46bef8cfba9a2a038"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "01413a56769a6cb917b0786b2ec846601ad53867c5c495effcaa797c1168abf0"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-2", "target_id": "ev-11-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-11-2", "target_id": "ev-11-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-11-4", "target_id": "ev-11-2"}], "trace_digest": "0232fa7946341225313a32bfeaee020635457a2c9f140ce46bef8cfba9a2a038"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "0808c67e8643d072ca216bb2d71220a80a3ece65131070997ceb5e866dc6dbf4", "weaken": true}, "seed": 11, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-2", "target_id": "ev-11-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-5", "target_id": "ev-11-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-11-3", "target_id": "th-11-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-11-3", "target_id": "th-11-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-11-14", "target_id": "ev-11-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "de5398c779421fe66e123af08db10cf11871c2a54c3f1d4ac2dc5b2c010296b3"}}
{"deterministic_replay": {"digests": ["a722e372b110c746b829f878c08fef136cac99367bcd639c5fb41e9918d8a4ea", "6f49834c699e9d7ff149b614f82e9bca726e58095085fd52470bcdc96a3ba51c", "a8147a9e1b08ebeccafc588c51543debeafb119a089ee6420365abb7bda061b5", "01562d0a40ae43b5de969e2aa59c3c469af615f6381ba0bd6274b59ea75f6773"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "a722e372b110c746b829f878c08fef136cac99367bcd639c5fb41e9918d8a4ea"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-2", "target_id": "ev-19-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-19-2", "target_id": "ev-19-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-19-4", "target_id": "ev-19-2"}], "trace_digest": "01562d0a40ae43b5de969e2aa59c3c469af615f6381ba0bd6274b59ea75f6773"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "a8147a9e1b08ebeccafc588c51543debeafb119a089ee6420365abb7bda061b5", "weaken": true}, "seed": 19, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-2", "target_id": "ev-19-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-5", "target_id": "ev-19-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-19-3", "target_id": "th-19-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-19-3", "target_id": "th-19-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-19-14", "target_id": "ev-19-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "6f49834c699e9d7ff149b614f82e9bca726e58095085fd52470bcdc96a3ba51c"}}
trace_artifact /tmp/agent-memory-infra/experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
```

experiment exit code: 0

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
