# Stage 8 Skill/API packaging seam

Stage 8 packages the validated `CallerSession` boundary as the smallest explicit Skill/API surface. It does not add a web server, authentication system, MCP dependency, agent framework, or orchestrator. It does not change V0.2 transitions or locked Phase H configuration.

## Public boundary

`SkillApi` is the externally consumable in-process seam. Callers use `invoke(caller_id, op, payload)` or `open_caller(caller_id).invoke(op, payload)`. There is no second transport. The seam is framework-neutral: any caller that can call a Python function can use it.

`SkillApi` and `SkillCaller` hold no graph, IDs, lifecycle, thread membership, relation endpoints, trace, attention, or durable transition state. Those remain owned by the mechanism behind `MemoryService`.

## Supported operations

| op | request payload | response |
| --- | --- | --- |
| `observe` | `content`, optional `note`, optional `source` | service result including mechanism-assigned `point_id` |
| `signal` | `name` plus signal fields such as `point_id`, `reason` | service result; mechanism assigns event/thread/relation ids |
| `retrieve` | `query` | ranked mechanism read |
| `read_lifecycle` | `target_id` | lifecycle record |
| `read_event` | `event_id` | event record |
| `read_relations` | none | relation records |
| `read_graph` | none | read-only projection of mechanism-owned nodes and edges |
| `inspect_trace` | none | trace records |
| `read_caller_context` | none | caller-scoped notes and attributions |
| `save` | none | mechanism snapshot write |
| `load` | none | mechanism snapshot read |

Unknown operations are rejected as `unsupported skill operation` before the service.

## Caller identity

`caller_id` is bound by the seam on every call. It is request metadata, not a mechanism-owned durable field. A payload `caller_id` that differs from the bound identity is impersonation and is rejected. `target_caller_id`, `all_caller_contexts`, `caller_contexts`, and `impersonate` remain rejected.

## Observation versus mechanism-owned outputs

Callers may supply observations, signals, retrieval queries, and optional notes. Mechanism-owned outputs include ids, lifecycle, thread membership, relation endpoints, trace, and attention. Injecting mechanism-owned fields such as `assign_ids` is rejected. The seam does not allocate those fields.

## Shared reads and isolated context

Mechanism reads (events, lifecycle, relations, trace) are shared across callers of the same service. Caller notes and attributions are isolated to the bound `caller_id`.

## Save/load

`save`/`load` round-trip mechanism state only. Caller-scoped notes and attributions are not restored.

## Storage and transport

`InMemoryDurableStore` and `FileDurableStore` accept the same operations through `SkillApi`. Substituting the store does not change the operation names or ownership rules. No HTTP, MCP, or agent SDK is required.

## Public packaging surface

Black-box consumers import `SkillApi`, `SkillCaller`, `SUPPORTED_OPS`, and `SnapshotError` from `memory_infra.skill`. They do not import store internals or the mechanism seal.

`SkillApi.open_memory()` and `SkillApi.open_file(path)` construct the seam over `InMemoryDurableStore` and `FileDurableStore`. Substituting the store does not change operation names or ownership rules.

`reopen()` is the process-restart handoff. It builds a new `SkillApi` and `MemoryService` over the saved store and supplies the mechanism-owned seal out of band. It does not return the seal, does not allocate ids, and does not own lifecycle, thread, relation, trace, or attention transitions. Caller notes are not restored. `save` returns an integrity digest; `load` after `reopen()` must return the same digest.

`inspect_trace` returns mechanism transition records. A substantive trace has `ok`, `op == inspect_trace`, and a non-empty sequence of records with `target_id`, `kind`, `reason`, and `evidence_refs`. Trace records do not carry caller notes.
