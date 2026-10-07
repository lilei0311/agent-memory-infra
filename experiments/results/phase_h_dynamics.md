# Phase H locked dynamics evidence

Code under test: `65b793cbe55fedc9f2043935090f7270b24916cf`

This file is an evidence record only. It does not change the harness, tests, V0.1 scripts, or Phase G attention configuration.

## Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## Locked configuration

- seeds: `7, 11, 19`
- context budget: `4`
- policy: `none` (baseline allocation; attention `observe()` is not called)
- conditions, isolated one at a time: `event_identity`, `thread_lifecycle`, `memory_lifecycle`, `evidence_integrity`, `deterministic_replay`
- no seed change, no attention retune, no V0.1 A/B/C/D/E edit

Relation coverage by condition:

- `thread_lifecycle`: create / extend / split / merge / reopen; split writes `contextual.changed_context`; merge writes `referential.same_thread`; reopen writes `referential.revisits` and does not rewrite members
- `evidence_integrity`: `temporal.before`, `evidential.contradicts`, `causal.caused_by`; both event observations and evidence refs kept
- `memory_lifecycle`: confirm -> STABLE, revise -> UPDATED, weaken -> WEAKENED, decay STABLE -> DORMANT, retrieval DORMANT -> REACTIVATED, separate decay path DORMANT -> INACCESSIBLE; evidence refs kept

## pytest output

```
............................                                             [100%]
28 passed in 0.04s
```

## experiment output

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
{"deterministic_replay": {"digests": ["3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1", "8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405", "3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9", "e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "trace_digest": "e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9", "weaken": true}, "seed": 7, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "reopened": true, "split": true, "trace_digest": "8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405"}}
{"deterministic_replay": {"digests": ["01413a56769a6cb917b0786b2ec846601ad53867c5c495effcaa797c1168abf0", "de5398c779421fe66e123af08db10cf11871c2a54c3f1d4ac2dc5b2c010296b3", "0808c67e8643d072ca216bb2d71220a80a3ece65131070997ceb5e866dc6dbf4", "0232fa7946341225313a32bfeaee020635457a2c9f140ce46bef8cfba9a2a038"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "01413a56769a6cb917b0786b2ec846601ad53867c5c495effcaa797c1168abf0"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "trace_digest": "0232fa7946341225313a32bfeaee020635457a2c9f140ce46bef8cfba9a2a038"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "0808c67e8643d072ca216bb2d71220a80a3ece65131070997ceb5e866dc6dbf4", "weaken": true}, "seed": 11, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "reopened": true, "split": true, "trace_digest": "de5398c779421fe66e123af08db10cf11871c2a54c3f1d4ac2dc5b2c010296b3"}}
{"deterministic_replay": {"digests": ["a722e372b110c746b829f878c08fef136cac99367bcd639c5fb41e9918d8a4ea", "6f49834c699e9d7ff149b614f82e9bca726e58095085fd52470bcdc96a3ba51c", "a8147a9e1b08ebeccafc588c51543debeafb119a089ee6420365abb7bda061b5", "01562d0a40ae43b5de969e2aa59c3c469af615f6381ba0bd6274b59ea75f6773"], "match": true}, "event_identity": {"distinct_events": true, "distinct_evidence": true, "event_count": 2, "trace_digest": "a722e372b110c746b829f878c08fef136cac99367bcd639c5fb41e9918d8a4ea"}, "evidence_integrity": {"both_events_present": true, "causal": "causal.caused_by", "contradiction": "evidential.contradicts", "distinct_evidence": true, "endpoints_unchanged": true, "relation_types": ["causal.caused_by", "evidential.contradicts", "temporal.before"], "trace_digest": "01562d0a40ae43b5de969e2aa59c3c469af615f6381ba0bd6274b59ea75f6773"}, "memory_lifecycle": {"confirm": true, "dormant_before_retrieval": "DORMANT", "evidence_kept": true, "inaccessible": "INACCESSIBLE", "pairs": [["DORMANT", "INACCESSIBLE"], ["DORMANT", "REACTIVATED"], ["FORMING", "LABILE"], ["LABILE", "STABLE"], ["REACTIVATED", "RECONSOLIDATING"], ["RECONSOLIDATING", "STABLE"], ["RECONSOLIDATING", "UPDATED"], ["RECONSOLIDATING", "WEAKENED"], ["STABLE", "DORMANT"], ["STABLE", "REACTIVATED"]], "reactivated": "REACTIVATED", "revise": true, "trace_digest": "a8147a9e1b08ebeccafc588c51543debeafb119a089ee6420365abb7bda061b5", "weaken": true}, "seed": 19, "thread_lifecycle": {"child_topic": "beta", "created": true, "extended": true, "members_unchanged_on_reopen": true, "merged_status": true, "not_topic_return": true, "reopened": true, "split": true, "trace_digest": "6f49834c699e9d7ff149b614f82e9bca726e58095085fd52470bcdc96a3ba51c"}}
```

## Reproducibility

Same seed plus the locked condition functions produced identical trace digests on a second run (`deterministic_replay.match` is true for seeds 7, 11, and 19). Digests differ across seeds because event ids include the seed. No parameter was changed after seeing the output.
