# V0.2 dynamics contract

Status: contract freeze of behavior implemented and evidence-backed at Phase H HEAD `d36183eb0a20a531d8105bae23d84eca2459f1de`, recorded in `experiments/results/phase_h_dynamics.md` and `experiments/results/phase_h_trace.json`.

This document is the canonical lower-layer contract. It does not add a mechanism, retune Phase G attention, or change V0.1 A/B/C/D/E. Biological terms are modeling labels only.

Adapter: `memory_infra.graph.GraphMemory`.

## Ownership boundary

Mechanism-owned durable state:

- identifier allocation (`pt-`, `ev-`, `ep-`, `th-`, `rel-`, `ret-` plus seed and counter)
- `MemoryPoint.candidate_status` and `promotion_reason`
- `Event` records after creation
- `Thread.status` and `member_event_ids`
- `Relation` records
- `MemoryState` lifecycle, accessibility, recency, and history lists
- `RetrievalEvent` log
- `Transition` log
- attention mode, anchor, and distribution when `observe()` runs

Caller or LLM may supply only observations and signals:

- point `content` and `source`
- promotion `reason` and optional episode fields (`action`, `feedback`, `outcome`, `context`, `goal`, `state_change`)
- thread `topic`, `goal`, extend/split/merge/reopen signal strings
- relation evidence strings and causal `inferred` flag
- reconsolidation `decision` (`confirm`, `revise`, `weaken`, `unresolved`)
- retrieval query string
- `Signals` for attention (`topic`, continuity/switch/divergence/goal flags, `thread_reference`)

Callers must not write lifecycle, thread status, or relation endpoints except through these methods. `set_attention()` is debug-only and is not a production transition.

## Identity

Implemented and evidence-backed:

- each `add_point` allocates a new point and evidence ref `ev-{point_id}`
- each `promote` allocates a new Event; repeated identical observations stay distinct Events with distinct evidence refs
- Event observation, evidence ref, and timestamp are not rewritten by decay, retrieval, contradiction, or thread merge
- thread reopen does not rewrite `member_event_ids`
- merge moves membership and sets the right thread status to `merged`; it does not delete Events

Not implemented: point status `LINKED` and `DISCARDED` have enum values only. There is no discard or link writer.

## Thread lifecycle

Implemented statuses: `active` (create/split/reopen), `merged` (merge of the right thread).

| method | transition | evidence |
| --- | --- | --- |
| `open_thread` | none -> `active` | source Event evidence ref |
| `extend` | `active` -> `active`; appends member; writes `temporal.before` | signal string |
| `split` | child created `active` with `parent_thread_id`; writes `contextual.changed_context` | child Event evidence ref |
| `merge` | right status `separate` -> `merged`; left absorbs members; writes `referential.same_thread` | signal string |
| `reopen` | non-active -> `active`; members unchanged; writes `referential.revisits`; thread state to `REACTIVATED` if present | member evidence refs plus relation evidence |

`reopen` raises if the thread is already `active` or the signal is empty. It is not attention topic-return (`topic-return-restore` is only written by `observe`).

Not implemented: explicit close, archive, or delete.

## Memory lifecycle

States present on `Lifecycle`: `FORMING`, `LABILE`, `STABLE`, `REACTIVATED`, `RECONSOLIDATING`, `UPDATED`, `DORMANT`, `WEAKENED`, `INACCESSIBLE`.

Implemented transitions (Phase H pairs):

| source | target | trigger | method |
| --- | --- | --- | --- |
| `FORMING` | `LABILE` | `promote` | `promote` (state is created `FORMING`, then moved) |
| `LABILE` | `STABLE` | `consolidation` | `consolidate` when reinforcement history is non-empty |
| `STABLE` | `REACTIVATED` | `retrieval` | `retrieve` |
| `REACTIVATED` | `RECONSOLIDATING` | `retrieval-followup` | `begin_reconsolidation` |
| `RECONSOLIDATING` | `STABLE` | `reconsolidation-decision` / `confirm` | `resolve_reconsolidation` |
| `RECONSOLIDATING` | `UPDATED` | `revise` | `resolve_reconsolidation` |
| `RECONSOLIDATING` | `WEAKENED` | `weaken` or `unresolved` | `resolve_reconsolidation` |
| `STABLE` | `DORMANT` | `time` / `low-accessibility` | `decay` when accessibility <= 0.5 |
| `DORMANT` | `REACTIVATED` | `retrieval` | `retrieve` |
| `DORMANT` | `INACCESSIBLE` | `time` / `zero-accessibility` | second `decay` from dormant |
| `STABLE` | `RECONSOLIDATING` | `contradiction` | `contradict` |

`decay` subtracts 0.5 accessibility and 0.25 recency, floored at 0. It does not delete the Event or evidence ref. `INACCESSIBLE` targets are excluded from retrieval candidates. Retrieval of `DORMANT` or `STABLE` sets accessibility back to 1.0 and appends retrieval history.

Not implemented as automatic transitions: paths out of `UPDATED` or `WEAKENED`; confidence updates; destructive deletion.

## Relations

Implemented writers and required provenance:

| type | writer | provenance |
| --- | --- | --- |
| `temporal.before` | `extend` | signal stored as `evidence_ref` |
| `contextual.changed_context` | `split` | new topic string |
| `referential.same_thread` | `merge` | signal string |
| `referential.revisits` | `reopen` | signal string |
| `causal.caused_by`, `causal.caused`, `causal.enabled`, `causal.prevented` | `link_causal` | non-empty evidence; `inferred` flag stored; endpoints unchanged |
| `evidential.contradicts` | `contradict` | evidence string; both Events remain; both states enter `RECONSOLIDATING` |

Contradiction does not overwrite either observation. Causal linking rejects an empty evidence string.

Not implemented: support/entail relations, automatic inference, or relation deletion.

## Trace and replay

`snapshot()["trace"]` is the review trace. Each entry has `tick`, `kind`, `target_id`, `source_state`, `target_state`, `trigger`, `signals`, `reason`, `evidence_refs`.

Phase H locked replay: seeds `7, 11, 19`, budget `4`, policy `none`, conditions `event_identity`, `thread_lifecycle`, `memory_lifecycle`, `evidence_integrity`, `deterministic_replay`. Same seed and stream yield the same trace digest. Digests recorded in `experiments/results/phase_h_dynamics.md` are historical evidence and must not be edited to match a new run.

Attention comparison remains Phase G only. Phase H policy `none` does not call `observe()`.

## Out of scope

No GraphRAG, vector database, Graphiti, or Mem0 integration. No LLM-owned durable transition. No new attention mechanism in this contract.
