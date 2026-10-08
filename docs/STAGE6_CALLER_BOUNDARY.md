# Stage 6 caller isolation boundary

Stage 6 defines the smallest agent-facing attribution seam. It does not change V0.2 transitions, snapshot fields, or locked Phase H configuration.

## Caller identity

A caller is an agent-agnostic string `caller_id`. `CallerSession` binds that identity at the service boundary and injects it on each request. A payload `caller_id` that differs from the bound session is rejected as impersonation. No agent framework, MCP server, or model provider is required.

Requests without a session use `caller_id="anonymous"`. That default keeps the Stage 5 request contract usable.

## Observational metadata vs mechanism-owned state

Observational request metadata:

- `caller_id`
- optional `note`
- observation `content` and `source` (source defaults to the bound `caller_id` when omitted)
- existing signal arguments and retrieval queries

Caller-scoped context is the in-service map of notes and observation attributions for that `caller_id`. It is not a snapshot field, not a graph object, and is not restored by `load`.

Mechanism-owned durable state remains unchanged: IDs, lifecycle, thread membership, relation endpoints, trace, attention, integrity, and the restart seal. Callers still cannot set `assign_ids`, `rewrite_lifecycle`, `rewrite_threads`, `rewrite_relations`, `caller_lifecycle`, `overwrite`, `delete`, or signal-owned lifecycle fields.

`target_caller_id`, `all_caller_contexts`, `caller_contexts`, and `impersonate` are rejected. There is no operation that reads or writes another caller's notes.

## Isolation

Two `CallerSession` objects on one `MemoryService` do not share caller-scoped notes or attributions. A note or observation recorded for caller A is absent from caller B's `read_caller_context`. Shared mechanism reads remain shared storage: both sessions can read an event created through the same service. That is not caller-context isolation.

`InMemoryDurableStore` and `FileDurableStore` keep the same request operations. Save/load round-trips mechanism state only. Caller-scoped notes do not enter the file snapshot.

This stage does not claim production multi-agent readiness, authentication, or concurrent isolation.
