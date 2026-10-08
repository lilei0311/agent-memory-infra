# Stage 7 heterogeneous agent-facing boundary

Stage 7 validates that two distinct caller wrappers can consume the Stage 6 `CallerSession` contract. It does not change V0.2 transitions, snapshot fields, or locked Phase H configuration. It does not package a Skill.

## Caller responsibilities

A caller wrapper binds one `caller_id` through `CallerSession`. It may submit observations, signals, retrieval queries, reads, and optional caller notes. It must not set mechanism-owned fields or address another caller scope.

Two wrappers are defined:

- `MethodCaller`: method-shaped (`observe`, `signal`, `retrieve`, reads). Keeps a local command log that is not sent to the service.
- `EnvelopeCaller`: envelope-shaped (`submit({"op", "payload", "client_meta"})`). Strips `client_meta` before the service boundary.

Neither wrapper is an agent framework, MCP server, model provider, or orchestrator.

## Supported operations

Both wrappers use the existing request contract:

- `observe`, `signal`, `retrieve`
- `read_lifecycle`, `read_event`, `read_relations`, `inspect_trace`, `read_caller_context`
- `save`, `load`

## Shared mechanism reads vs isolated caller context

Shared mechanism reads are storage-backed graph state: events, lifecycle, relations, and trace. A fact promoted through one wrapper is readable by the other wrapper on the same service.

Caller-scoped context is notes and observation attributions for that `caller_id` only. It is not a snapshot field. A note recorded by one wrapper is absent from the other wrapper's context.

## Storage substitution

`InMemoryDurableStore` and `FileDurableStore` accept the same request sequence through either wrapper. Substituting the store does not change operation names or mechanism-owned identity.

## Save/load

Save/load round-trips mechanism state only. Caller-scoped notes and attributions are not restored. That preserves the Stage 6 contract; this stage does not make caller context durable.

## Negative boundary

A payload `caller_id` that differs from the bound session is rejected as impersonation. `target_caller_id`, `all_caller_contexts`, `caller_contexts`, and `impersonate` are rejected. Mechanism-owned fields such as `assign_ids` remain rejected. Client-only metadata must not become mechanism state.

These tests do not claim production multi-agent readiness.
