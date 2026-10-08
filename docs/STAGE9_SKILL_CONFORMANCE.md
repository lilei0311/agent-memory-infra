# Stage 9 Skill/API conformance contract

Stage 9 freezes the Stage 8 public Skill/API seam as a small conformance contract. It does not add a transport, agent framework, or second owner of mechanism state. It does not change V0.2 transitions or locked Phase H configuration.

Future callers may reuse `tests/skill_conformance.py` by supplying a factory that returns the public surface. The suite does not import `memory_infra.store`.

## Public import and entry points

Conformance consumers depend only on:

- `SkillApi`
- `SkillCaller`
- `SUPPORTED_OPS`
- `SnapshotError`

from `memory_infra.skill`.

Entry points are `SkillApi.open_memory()`, `SkillApi.open_file(path)`, `SkillApi.invoke(caller_id, op, payload)`, `SkillApi.open_caller(caller_id)`, and `SkillApi.reopen()`. `reopen()` is the restart handoff. It does not return the mechanism seal and does not allocate ids.

## Supported operations and response envelope

Supported operations are exactly `SUPPORTED_OPS`: `observe`, `signal`, `retrieve`, `read_lifecycle`, `read_event`, `read_relations`, `inspect_trace`, `read_caller_context`, `save`, `load`.

Every accepted response is a mapping with `ok: true` and `op` equal to the requested operation. `save` and `load` also return a non-empty `integrity` string. `observe` returns a mechanism-assigned `point_id`. `signal` returns a nested mechanism result that includes an `event_id` for `promote`. `inspect_trace` returns a non-empty sequence of records with `target_id`, `kind`, `reason`, and non-empty `evidence_refs`.

An operation outside `SUPPORTED_OPS` is rejected as `unsupported skill operation` before the service.

## Caller binding and isolation

`caller_id` is bound by the seam. A payload `caller_id` that differs from the bound identity is impersonation and is rejected. `target_caller_id`, `all_caller_contexts`, `caller_contexts`, and `impersonate` are rejected.

Mechanism reads (events, lifecycle, relations, trace) are shared across callers of the same service. Caller notes and attributions are isolated to the bound caller.

## Mechanism-owned versus caller-supplied fields

Callers may supply observations, signals, retrieval queries, and optional notes. Notes and other client metadata are request metadata. They are not mechanism-owned durable state. `save`/`load` does not restore caller notes or attributions.

Mechanism-generated identifiers, lifecycle, thread membership, relation endpoints, trace, attention, and persistence remain mechanism-owned. Injecting `assign_ids` or other ownership fields is rejected. A caller-supplied `point_id` on `observe` does not become the returned identifier.

## Error behavior

- unsupported operation: `unsupported skill operation`
- impersonation: `caller cannot impersonate another caller`
- other-caller scope: `caller cannot address another caller scope`
- ownership violation: `caller cannot own mechanism fields`

## Storage substitution

`open_memory()` and `open_file(path)` must satisfy the same operation names, envelope, isolation, ownership rejection, trace shape, and save/load integrity rules. Substituting storage does not change the contract.

## Save/load and integrity

`save` writes mechanism state and returns `integrity`. `reopen()` then `load` returns the same `integrity`. Restored mechanism reads remain available. Caller context is not restored.

## Compatibility expectations

A future transport or adapter may wrap this contract. It must not become a second owner of ids, lifecycle, threads, relations, trace, attention, or persistence. This stage does not claim authentication, concurrency, or deployment readiness.
