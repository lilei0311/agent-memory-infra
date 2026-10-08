# Stage 2 integration boundary

Status: storage-agnostic adapter over the frozen V0.2 mechanism. This document does not change `docs/V02_DYNAMICS_CONTRACT.md`, Phase H seeds, Phase G attention, or V0.1 A/B/C/D/E.

Adapter: `memory_infra.adapter.MemoryAdapter`.
Mechanism: `memory_infra.graph.GraphMemory` (private to the adapter).

## Ownership

Caller or LLM may supply only:

- observation `content` and `source` via `submit_observation`
- allowed signal name and signal payload via `submit_signal`
- retrieval `query` via `retrieve`

Allowed signals: `promote`, `open_thread`, `extend`, `split`, `merge`, `reopen`, `link_causal`, `contradict`, `begin_reconsolidation`, `resolve_reconsolidation`, `consolidate`, `decay`, `retrieve`.

Mechanism-owned, not settable by the caller:

- identifier allocation
- `lifecycle_state`, `candidate_status`, `accessibility`
- thread `status` and `member_event_ids`
- relation ids and `evidence_ref` writes
- trace records

Rejected payload fields: `lifecycle_state`, `candidate_status`, `status`, `member_event_ids`, `accessibility`, `evidence_ref`, `relation_id`, `trace`, `overwrite`, `delete`. Unknown signal names raise `BoundaryError`.

Read APIs return frozen mappings or tuples: `read_lifecycle`, `read_event`, `read_relations`, `inspect_trace`. Caller mutation of those views does not write durable state.

## Inputs and outputs

| call | input | output |
| --- | --- | --- |
| `submit_observation` | content, source | mechanism-allocated point id |
| `submit_signal` | allowed name plus signal fields | frozen signal result; ids only |
| `retrieve` | query | retrieval id, query, selected refs, timestamp |
| `read_lifecycle` | target id | lifecycle, accessibility, recency, histories |
| `read_event` | event id | observation and evidence ref |
| `read_relations` | none | relation type, endpoints, evidence ref, inferred |
| `inspect_trace` / `trace_digest` | none | review trace or sha256 |

## Invariants preserved

Event identity, thread create/extend/split/merge/reopen, memory lifecycle, relation provenance, non-destructive forgetting, and deterministic replay stay inside the Phase H mechanism. The adapter does not add transitions or attention behavior.

## Future storage seam

`DurableStorePort.load_snapshot` / `save_snapshot` is the only documented persistence seam. Stage 2 does not implement it and does not add a database, GraphRAG, vector store, Graphiti, or Mem0 dependency. A later store may persist an inspectable snapshot only. It must not assign identifiers or lifecycle/relation state.
