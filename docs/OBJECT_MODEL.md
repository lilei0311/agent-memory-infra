# Object Model: Memory Point, Event, Thread, Block, State, Retrieval

## Status

Research design for the V0.2 memory-dynamics simulator. This document freezes the object boundaries and invariants before transition equations or storage integration are implemented.

The model is deliberately inspectable: durable content, evidence, derived state, and runtime attention are separate objects.

## 1. Object hierarchy

```
Conversation / environment stream
        |
        v
   Memory Point (candidate)
        |
        +----> Event Instance(s)
                    |
                    v
               Event Thread
                    |
                    +----> Memory Block / abstraction
                    |
                    +----> Relations
                              |
                              v
                       Memory Dynamic State
                              |
                              v
                       Attention State
                              |
                              v
                     Retrieval / Context
```

A Memory Point is not automatically a durable memory. It is a candidate signal that may later be promoted, linked, revised, or discarded.

## 2. MemoryPoint

A MemoryPoint represents a potentially meaningful observation from an interaction stream.

Required:
- `point_id`
- `created_at`
- `source`
- `content`
- `evidence_ref`
- `candidate_status`

Optional:
- `context_ref`
- `participants`
- `topic_hints`
- `related_points`

Candidate statuses:
- `CANDIDATE`
- `PROMOTED`
- `LINKED`
- `DISCARDED`

Invariants:
1. A point preserves the original observation; later inference must not overwrite it.
2. A point may exist without becoming an Event.
3. Promotion requires explicit evidence from the dynamics layer, not merely semantic similarity.
4. Discarded means not currently promoted to durable experience; it does not erase source evidence.

## 3. Event Instance

An Event is one occurrence/episode.

Required:
- `event_id`
- `timestamp`
- `source`
- `observation/action`
- `evidence_ref`

Optional:
- `context`
- `participants`
- `goal`
- `feedback`
- `outcome`
- `state_change`

Invariants:
1. One Event has one occurrence identity.
2. Repeated occurrences are separate Events.
3. Evidence is immutable after ingestion; corrections create a new evidence/revision record.
4. Action, feedback and outcome stay linked when they belong to the same episode.
5. Derived confidence/strength/accessibility is never stored as intrinsic event content.

## 4. EventThread

A Thread is a temporally connected sequence/set of related Events.

Required:
- `thread_id`
- `created_at`
- `member_event_ids`

Optional:
- `topic_anchor`
- `goal`
- `status`
- `parent_thread_id`

Invariants:
1. Thread membership does not merge or overwrite Events.
2. A Thread must be explainable by at least one explicit relation, shared unresolved goal, recurring topic, or other inspectable linkage signal.
3. Threads may split when one sequence develops independent goals/context.
4. Threads may merge only when their relationship is supported; merging is a graph operation, not destructive data replacement.
5. A Thread may temporarily have one Event.

## 5. Relation

Relations are first-class graph edges.

Types:
- temporal: `before`, `after`, `overlaps`, `recurs_with`
- causal: `caused_by`, `caused`, `enabled`, `prevented`
- referential: `refers_to`, `same_thread`, `revisits`
- evidential: `confirms`, `contradicts`, `strengthens`, `weakens`
- contextual: `same_context`, `changed_context`, `related_context`

Required:
- `relation_id`
- `source_id`
- `target_id`
- `relation_type`
- `created_at`
- `evidence_ref`

Invariants:
1. Relations are directed unless the type is explicitly defined as symmetric.
2. A relation is evidence-backed or marked as an inference; inferred relations must remain distinguishable from observations.
3. Contradiction does not delete either side.
4. Relation revision creates history rather than silently mutating the past.

## 6. MemoryBlock

A MemoryBlock is a higher-level reusable representation derived from one or more Events/Threads.

Examples:
- repeated behavioral pattern
- learned rule
- recurring mistake
- stable preference
- task-specific procedure

Required:
- `block_id`
- `created_at`
- `source_refs`
- `representation`
- `derivation_status`

Invariants:
1. Every Block must point to supporting source Events/Threads.
2. A Block is an abstraction, not replacement evidence.
3. If supporting evidence conflicts, the Block must expose that conflict rather than hiding it.
4. Updating a Block must not rewrite source Events.

## 7. MemoryState

MemoryState is derived dynamic state associated with an Event/Block/Thread.

Keep these dimensions separate initially:
- `accessibility`
- `confidence`
- `contextual_fit`
- `recency`
- `reinforcement_history`
- `contradiction_history`
- `retrieval_history`
- `usefulness_history`
- `lifecycle_state`

Lifecycle states:
- `FORMING`
- `LABILE`
- `STABLE`
- `REACTIVATED`
- `RECONSOLIDATING`
- `UPDATED`
- `DORMANT`
- `WEAKENED`
- `INACCESSIBLE`

These are computational states, not claims about literal neural states.

Invariant: no single scalar may be treated as the authoritative representation of all dimensions during V0.2 research.

## 8. RetrievalEvent

Retrieval is a runtime event and part of the history.

Required:
- `retrieval_id`
- `timestamp`
- `query_context`
- `candidate_refs`
- `selected_refs`

Optional:
- `used_refs`
- `outcome`
- `feedback`
- `contradiction`
- `revision`

A retrieval may:
- retrieve and be ignored;
- retrieve and be used successfully;
- retrieve and expose contradiction;
- retrieve and cause revision.

Retrieval alone is not evidence of successful reinforcement.

## 9. Promotion: Memory Point -> Event

A Memory Point can be promoted when one or more inspectable signals accumulate:
- repeated reference;
- meaningful consequence;
- explicit user/environment feedback;
- linkage to an existing active Thread;
- later confirmation or contradiction;
- demonstrated task relevance.

The exact threshold is not frozen. V0.2 should log the reason for every promotion so alternative promotion policies can be compared.

## 10. Thread lifecycle

Initial graph operations:
- CREATE: first coherent Event cluster;
- EXTEND: add an Event supported by continuity evidence;
- SPLIT: separate divergent goals/context;
- MERGE: connect previously separate threads when evidence supports common continuity;
- REOPEN: reactivate a dormant thread after relevant evidence;
- ARCHIVE: remove from active attention without deleting history.

CREATE/EXTEND/SPLIT/MERGE decisions must be inspectable and reproducible from recorded signals.

## 11. State transition ownership

The mechanism layer owns durable state transitions.

The Agent/LLM may emit observations or signals such as topic continuity, explicit feedback, or candidate relations. It must not directly set:
- lifecycle state;
- accessibility;
- confidence;
- attention allocation;
- forgetting/deletion.

This preserves model independence and makes weak and strong Agents subject to the same memory mechanism.

## 12. Context assembly boundary

Attention State decides the active allocation across Threads/Blocks.

Retrieval Policy then chooses evidence within that allocation.

The final context should retain provenance:
`context item -> source Event/Block -> supporting evidence`.

This prevents an abstraction from silently becoming indistinguishable from the underlying experience.

## 13. V0.2 simulator contract

The first implementation should simulate only:
1. MemoryPoint creation/promotion;
2. Event creation and immutable history;
3. Thread creation/extension/split/merge/reopen;
4. Relations;
5. MemoryState transitions;
6. RetrievalEvent logging;
7. Attention State updates;
8. deterministic context-budget allocation.

It should not yet require:
- a vector database;
- GraphRAG;
- Graphiti/Mem0 integration;
- production Agent runtime;
- learned neural memory controller.

## 14. Acceptance criteria

The graph-only simulator is ready for dynamics experiments when:
- every object has stable identity;
- every derived transition has a recorded cause/signal;
- repeated Events remain individually inspectable;
- contradictions coexist without destructive overwrite;
- retrieval can reactivate a dormant item;
- attention can focus and diverge without LLM state management;
- context assembly can be reproduced from the same event stream and seed;
- V0.1 experiments A/B/C/D/E remain untouched.
