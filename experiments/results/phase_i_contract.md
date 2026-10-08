# Phase I contract evidence

Code under test: `34a7c2aff3d5b0c91547486a9954b38d7d9addb6`

This file records execution only. It does not change the harness, V0.1 scripts, or Phase G attention configuration.

## Changed files in the contract commit

- `docs/V02_DYNAMICS_CONTRACT.md`
- `tests/test_v02_contract.py`

No mechanism code changed. Locked Phase H seeds, budget, and policy were not changed.

## Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Executed at HEAD `34a7c2aff3d5b0c91547486a9954b38d7d9addb6`.

## pytest output

```
...................................                                      [100%]
35 passed in 0.07s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`.

Replay match true. Seed 7 digests unchanged from the Phase H record:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Trace artifact `experiments/results/phase_h_trace.json` sha256 remained `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.


## Re-execution after relation provenance tests

Code under test: `b2d74e5944feaa19f49e4cc07acdce79c806a1c3`

Parent evidence HEAD was `9b4aae833b9c0a40c55e3294b26f228aff87277b`. The only code change since that HEAD is `tests/test_v02_contract.py`, which now asserts:

- split creates `contextual.changed_context` with provenance `new-context`
- merge creates `referential.same_thread` with provenance `same-goal`
- reopen creates `referential.revisits` with provenance `later-reference`

Mechanism code, Phase H harness, seeds, budget, and policy were not changed. V0.1 A/B/C/D/E scripts and historical results were not edited. Phase G locked attention config and results were not edited.

### Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Executed at HEAD `b2d74e5944feaa19f49e4cc07acdce79c806a1c3`.

### pytest output

```
....................................                                     [100%]
36 passed in 0.07s
```

### experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`.

Replay match true. Seed 7 digests unchanged from the locked Phase H record:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Trace artifact `experiments/results/phase_h_trace.json` sha256 remained `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.


## Final-HEAD re-execution

Execution HEAD: `7a50b4c52e7cea96e3ebde5f3e5e20404d0923ed`

This section records commands run at that exact HEAD. No mechanism, test, seed, budget, policy, stream, or scoring change was made. V0.1 A/B/C/D/E scripts and historical results were not edited. Phase G locked attention config and results were not edited. Historical Phase H evidence above was not rewritten.

### Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
....................................                                     [100%]
36 passed in 0.15s
```

### experiment output

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
{"deterministic_replay": {"digests": ["3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1", "8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405", "3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9", "e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-2", "target_id": "ev-7-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-7-2", "target_id": "ev-7-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-7-4", "target_id": "ev-7-2"}], "trace_digest": "e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9", "weaken": true}, "seed": 7, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-2", "target_id": "ev-7-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-5", "target_id": "ev-7-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-7-3", "target_id": "th-7-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-7-3", "target_id": "th-7-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-7-14", "target_id": "ev-7-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405"}}
{"deterministic_replay": {"digests": ["01413a56769a6cb917b0786b2ec846601ad53867c5c495effcaa797c1168abf0", "de5398c779421fe66e123af08db10cf11871c2a54c3f1d4ac2dc5b2c010296b3", "0808c67e8643d072ca216bb2d71220a80a3ece65131070997ceb5e866dc6dbf4", "0232fa7946341225313a32bfeaee020635457a2c9f140ce46bef8cfba9a2a038"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "01413a56769a6cb917b0786b2ec846601ad53867c5c495effcaa797c1168abf0"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-2", "target_id": "ev-11-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-11-2", "target_id": "ev-11-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-11-4", "target_id": "ev-11-2"}], "trace_digest": "0232fa7946341225313a32bfeaee020635457a2c9f140ce46bef8cfba9a2a038"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "0808c67e8643d072ca216bb2d71220a80a3ece65131070997ceb5e866dc6dbf4", "weaken": true}, "seed": 11, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-2", "target_id": "ev-11-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-5", "target_id": "ev-11-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-11-3", "target_id": "th-11-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-11-3", "target_id": "th-11-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-11-14", "target_id": "ev-11-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "de5398c779421fe66e123af08db10cf11871c2a54c3f1d4ac2dc5b2c010296b3"}}
{"deterministic_replay": {"digests": ["a722e372b110c746b829f878c08fef136cac99367bcd639c5fb41e9918d8a4ea", "6f49834c699e9d7ff149b614f82e9bca726e58095085fd52470bcdc96a3ba51c", "a8147a9e1b08ebeccafc588c51543debeafb119a089ee6420365abb7bda061b5", "01562d0a40ae43b5de969e2aa59c3c469af615f6381ba0bd6274b59ea75f6773"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "a722e372b110c746b829f878c08fef136cac99367bcd639c5fb41e9918d8a4ea"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-2", "target_id": "ev-19-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-19-2", "target_id": "ev-19-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-19-4", "target_id": "ev-19-2"}], "trace_digest": "01562d0a40ae43b5de969e2aa59c3c469af615f6381ba0bd6274b59ea75f6773"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "a8147a9e1b08ebeccafc588c51543debeafb119a089ee6420365abb7bda061b5", "weaken": true}, "seed": 19, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-2", "target_id": "ev-19-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-5", "target_id": "ev-19-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-19-3", "target_id": "th-19-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-19-3", "target_id": "th-19-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-19-14", "target_id": "ev-19-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "6f49834c699e9d7ff149b614f82e9bca726e58095085fd52470bcdc96a3ba51c"}}
trace_artifact /tmp/agent-memory-infra/experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
```

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Trace artifact `experiments/results/phase_h_trace.json` sha256 remained `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Working tree after the run had no tracked-file diff other than this evidence append.


## Exact-HEAD re-execution for Issue #11

Execution HEAD: `7db0faee48897474dae19537fc992eae6875b5a2`

This section records commands run at that exact HEAD. The parent evidence commit recorded execution at `7a50b4c52e7cea96e3ebde5f3e5e20404d0923ed`. No mechanism, test, seed, budget, policy, stream, or scoring change was made. `docs/V02_DYNAMICS_CONTRACT.md` was not modified. V0.1 A/B/C/D/E scripts and historical results were not edited. Phase G locked attention config and results were not edited. Historical Phase H evidence above was not rewritten. Working tree after the run had no tracked-file diff other than this evidence append.

Locked configuration verified unchanged:
- seeds: `7, 11, 19`
- budget: `4`
- policy: `none`
- conditions: event_identity, thread_lifecycle, memory_lifecycle, evidence_integrity, deterministic_replay

### Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
....................................                                     [100%]
36 passed in 0.15s
```

### experiment output

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
{"deterministic_replay": {"digests": ["3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1", "8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405", "3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9", "e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-2", "target_id": "ev-7-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-7-2", "target_id": "ev-7-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-7-4", "target_id": "ev-7-2"}], "trace_digest": "e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9", "weaken": true}, "seed": 7, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-2", "target_id": "ev-7-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-7-5", "target_id": "ev-7-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-7-3", "target_id": "th-7-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-7-3", "target_id": "th-7-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-7-14", "target_id": "ev-7-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405"}}
{"deterministic_replay": {"digests": ["01413a56769a6cb917b0786b2ec846601ad53867c5c495effcaa797c1168abf0", "de5398c779421fe66e123af08db10cf11871c2a54c3f1d4ac2dc5b2c010296b3", "0808c67e8643d072ca216bb2d71220a80a3ece65131070997ceb5e866dc6dbf4", "0232fa7946341225313a32bfeaee020635457a2c9f140ce46bef8cfba9a2a038"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "01413a56769a6cb917b0786b2ec846601ad53867c5c495effcaa797c1168abf0"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-2", "target_id": "ev-11-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-11-2", "target_id": "ev-11-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-11-4", "target_id": "ev-11-2"}], "trace_digest": "0232fa7946341225313a32bfeaee020635457a2c9f140ce46bef8cfba9a2a038"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "0808c67e8643d072ca216bb2d71220a80a3ece65131070997ceb5e866dc6dbf4", "weaken": true}, "seed": 11, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-2", "target_id": "ev-11-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-11-5", "target_id": "ev-11-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-11-3", "target_id": "th-11-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-11-3", "target_id": "th-11-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-11-14", "target_id": "ev-11-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "de5398c779421fe66e123af08db10cf11871c2a54c3f1d4ac2dc5b2c010296b3"}}
{"deterministic_replay": {"digests": ["a722e372b110c746b829f878c08fef136cac99367bcd639c5fb41e9918d8a4ea", "6f49834c699e9d7ff149b614f82e9bca726e58095085fd52470bcdc96a3ba51c", "a8147a9e1b08ebeccafc588c51543debeafb119a089ee6420365abb7bda061b5", "01562d0a40ae43b5de969e2aa59c3c469af615f6381ba0bd6274b59ea75f6773"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "a722e372b110c746b829f878c08fef136cac99367bcd639c5fb41e9918d8a4ea"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-2", "target_id": "ev-19-4"}, {"evidence_ref": "both-observed", "relation_type": "evidential.contradicts", "source_id": "ev-19-2", "target_id": "ev-19-4"}, {"evidence_ref": "observed-order", "relation_type": "causal.caused_by", "source_id": "ev-19-4", "target_id": "ev-19-2"}], "trace_digest": "01562d0a40ae43b5de969e2aa59c3c469af615f6381ba0bd6274b59ea75f6773"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "a8147a9e1b08ebeccafc588c51543debeafb119a089ee6420365abb7bda061b5", "weaken": true}, "seed": 19, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "left_absorbed_right_member": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "relations": [{"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-2", "target_id": "ev-19-5"}, {"evidence_ref": "same-topic", "relation_type": "temporal.before", "source_id": "ev-19-5", "target_id": "ev-19-8"}, {"evidence_ref": "beta", "relation_type": "contextual.changed_context", "source_id": "th-19-3", "target_id": "th-19-10"}, {"evidence_ref": "same-goal", "relation_type": "referential.same_thread", "source_id": "th-19-3", "target_id": "th-19-14"}, {"evidence_ref": "later-reference", "relation_type": "referential.revisits", "source_id": "th-19-14", "target_id": "ev-19-13"}], "reopened": true, "right_status_after_merge": "merged", "split": true, "trace_digest": "6f49834c699e9d7ff149b614f82e9bca726e58095085fd52470bcdc96a3ba51c"}}
trace_artifact /tmp/agent-memory-infra/experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
```

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true for seeds 7, 11, and 19. Trace artifact `experiments/results/phase_h_trace.json` sha256 remained `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
