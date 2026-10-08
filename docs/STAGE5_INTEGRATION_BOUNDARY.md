# Stage 5 integration boundary

Stage 5 validates the existing agent-agnostic / storage-agnostic boundary. It does not add a second mechanism owner and does not change V0.2 transitions.

## Supported service operations

`MemoryService.request(op, payload)` is the caller contract:

- `observe`: content and optional source
- `signal`: name plus signal arguments from the Stage 2 allow-list
- `retrieve`: query
- `read_lifecycle`, `read_event`, `read_relations`, `inspect_trace`
- `save`, `load`

`InMemoryDurableStore` and `FileDurableStore` accept the same snapshot contract. Substituting the store does not change operation names, identity assignment, lifecycle transitions, thread membership, relation endpoints, trace order, or attention state.

## Caller / LLM inputs

Callers and an LLM may supply observations and signals only: content, source, signal name, and signal arguments such as reason, topic, query, and evidence text.

## Mechanism-owned outputs and state

The mechanism owns point/event/thread/relation IDs, lifecycle and candidate status, thread membership, relation endpoints and provenance, trace, attention state, integrity, and the restart seal. Reads return frozen views. Requests that include `assign_ids`, `rewrite_lifecycle`, `rewrite_threads`, `rewrite_relations`, `caller_lifecycle`, `overwrite`, `delete`, `lifecycle_state`, `candidate_status`, `status`, `member_event_ids`, `accessibility`, `evidence_ref`, `relation_id`, or `trace` are rejected.

## Storage substitution

The same request sequence on either store yields the same mechanism-owned identity and state. File save/load round-trips that state. A missing file loads as empty. Malformed or unauthentic files are rejected before restore.

## Independent-instance isolation

Two `MemoryService` instances with separate stores do not share mechanism-owned mutable state. A mutation through Service A does not change Service B. Sharing one store object or one file path is shared storage, not isolation.

## Restart semantics

Process restart loads a validated snapshot through `FileDurableStore` and restores events, threads, relations, states, and trace. The caller still has only observations, signals, and reads. The restart seal is not part of the public service contract and is not returned in snapshots.

These tests do not claim multi-agent production readiness.
