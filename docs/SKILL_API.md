# Agent Memory Skill public API contract

Revision: `skill-api-2026-10-10.2`. Code baseline: `src/memory_infra/skill.py` and `CallerSession.request` at `fc443b86feea38fa1216c16f9c34d99c6028067a` (unchanged by the contract commits). This document is the caller-facing contract. It does not add a transport, storage adapter, Agent integration, Hub, or Memory Bridge.

A harness installs one Skill for one Agent. It calls the in-process entry below. It does not import `memory_infra.store`, allocate mechanism ids, or write graph/lifecycle/thread/relation/trace/attention state.

## What is public

Stable public surface, already implemented:

- `memory_infra.skill.SkillApi`
- `memory_infra.skill.SkillCaller`
- `memory_infra.skill.SUPPORTED_OPS`
- `memory_infra.skill.SnapshotError`
- `memory_infra.entrypoint.SkillEntrypoint`
- `memory_infra.entrypoint.SkillHandle`

`SUPPORTED_OPS` is exactly:

`observe`, `signal`, `retrieve`, `read_lifecycle`, `read_event`, `read_relations`, `read_graph`, `inspect_trace`, `read_caller_context`, `save`, `load`.

Stage 9 prose omitted `read_graph`. Current code includes it. This contract follows the code. Stage 9 conformance tests remain valid for the older subset; they are not the full public list.

Not public. Callers must not depend on these:

- `MemoryService`, `CallerSession`, store classes, seal keys, and graph mutators
- `memory_infra.explorer.render_explorer` and other presentation helpers (Stage 14 visual explorer only)
- bootstrap scanners, importer parsers, and experiment runners

## Startup

Preferred install path:

1. `SkillEntrypoint(seed=7, context_budget=4, policy="none", backend="memory"|"file", path=...)`
2. `handle = entry.open(caller_id)` then `handle.start(root=..., artifacts=...)`, or `entry.start(caller_id, ...)`
3. Read inventory and diagnostics. Unknown or unreadable sources do not abort startup and are not ingested.
4. `handle.enable_memory()` after discovery.
5. `handle.invoke(op, payload)`
6. Optional `handle.import_selected(paths)` only after discovery. It does not rewrite caller files.

`backend` must be `memory` or `file`. File backend requires `path`. `SkillEntrypoint.open` rejects an empty `caller_id` with `ValueError`: `caller_id is required`. `SkillApi.invoke` rejects an empty bound `caller_id` with `SnapshotError`: `caller_id must be a non-empty string`.

`invoke` before discovery raises `RuntimeError`: `memory operations require completed discovery`. `enable_memory` before discovery raises `RuntimeError`: `discovery must complete before memory operations`.

Direct seam, for conformance and in-process tests only:

- `SkillApi.open_memory(seed=7, context_budget=4, policy="none")`
- `SkillApi.open_file(path, seed=7, context_budget=4, policy="none")`
- `api.invoke(caller_id, op, payload)` or `api.open_caller(caller_id).invoke(op, payload)`
- `api.reopen()` builds a new `SkillApi` over the saved store. It does not return the seal and does not allocate ids.

Defaults `seed=7`, `context_budget=4`, `policy="none"` match the locked Phase H configuration. This contract does not authorize changing those locked experiment parameters.

## Ownership

The Skill does not own memory contents. The mechanism owns ids, lifecycle, thread membership, relation endpoints, trace, attention, and durable transitions. The caller owns observations, signals, retrieval queries, and optional notes.

Shared across callers of the same Skill instance: events, lifecycle, relations, graph projection, trace.

Isolated to the bound `caller_id`: notes and attributions from `read_caller_context`. A second `open` cannot read another handle's discovery inventory.

`save` / `load` persist mechanism state only. Caller notes and discovery inventory are not restored.

Rejected payload fields. Scope and ownership errors append the sorted rejected keys:

- impersonation: payload `caller_id` different from the bound id → `caller cannot impersonate another caller`
- other-caller scope: `target_caller_id`, `all_caller_contexts`, `caller_contexts`, `impersonate` → `caller cannot address another caller scope: ['<field>', ...]`
- ownership: `assign_ids`, `rewrite_lifecycle`, `rewrite_threads`, `rewrite_relations`, `caller_lifecycle`, `overwrite`, `delete` → `caller cannot own mechanism fields: ['<field>', ...]`
- `read_graph` also rejects `nodes`, `edges`, `relations`, `relation_id`, `event_id`, `point_id`, `thread_id`, `graph` with the same ownership error and sorted keys

Empty or non-string `caller_id` → `caller_id must be a non-empty string`. Empty `note` → `caller note must be a non-empty string`.

## Operations

Every accepted `invoke` result is a mapping with `ok: true` and `op` equal to the requested name. Errors are exceptions, not `ok: false`.

| op | payload | return | side effect |
| --- | --- | --- | --- |
| `observe` | required `content`; optional `source`, `note` | top-level `point_id` and `caller_id`; no `result` | appends a candidate point; does not promote it |
| `signal` | required `name`; signal fields below | top-level `caller_id`; `result.signal`, `result.result` | mechanism transition only; caller does not set lifecycle |
| `retrieve` | required `query` | `result.retrieval_id`, `result.query`, `result.selected`, `result.timestamp` | retrieval event owned by the mechanism |
| `read_lifecycle` | required `target_id` | lifecycle mapping in `result` (`target_id`, `lifecycle_state`, `accessibility`, `recency`, histories) | none |
| `read_event` | required `event_id` | event mapping in `result` (`event_id`, `timestamp`, `source`, `observation`, `evidence_ref`, `thread_id`) | none |
| `read_relations` | none | tuple of relation records in `result` | none |
| `read_graph` | none | projection mapping in `result` | none; no ids, no trace append |
| `inspect_trace` | none | tuple of trace records in `result` | none |
| `read_caller_context` | none | mapping in `result`: `caller_id`, `notes`, `attributions` (notes and attributions are tuples) | none |
| `save` | none | top-level non-empty `integrity`; no `result` | writes mechanism snapshot |
| `load` | none | top-level `integrity` matching the saved snapshot; no `result` | restores mechanism snapshot; no caller context |

Unknown `op` raises `SnapshotError` `unsupported skill operation` before the service.

Missing required operation fields raise `KeyError` (`content`, `name`, `query`, `target_id`, `event_id`). Empty `content` raises `BoundaryError` `observation content is required`. Missing required signal fields raise `TypeError` from the signal handler. Unknown lifecycle target raises `BoundaryError` `unknown target: ...`. Unknown event raises `BoundaryError` `unknown event: ...`. `load` with no snapshot raises `SnapshotError` `no snapshot to load`. Callers must not treat these as success.

`read_graph` result includes `read_only: true`, `owner: "mechanism"`, `ordering: "kind,id"`, `node_kinds`, `edge_kinds`, `nodes`, and `edges`. Node order is kind then id. Edge order is relation type then relation id. The projection is not a write API.

Allowed `signal` names: `promote`, `open_thread`, `extend`, `split`, `merge`, `reopen`, `link_causal`, `contradict`, `begin_reconsolidation`, `resolve_reconsolidation`, `consolidate`, `decay`, `retrieve`. Any other name raises `BoundaryError` `unsupported signal: ...`.

Minimum signal fields and `result.result` keys. Optional fields are omitted from the required set. Return keys are the handler mapping, not mechanism ids allocated by the caller:

- `promote`: `point_id`, `reason` → `event_id`, `evidence_ref`
- `open_thread`: `event_id`, `topic`, optional `goal` → `thread_id`, `status`
- `extend`: `thread_id`, `event_id`, `signal` → `thread_id`, `members`
- `split`: `thread_id`, `event_id`, `new_topic` → `thread_id`, `parent_thread_id`
- `merge`: `left_id`, `right_id`, `signal` → `thread_id`, `status`
- `reopen`: `thread_id`, `signal` → `thread_id`, `status`
- `link_causal`: `source_id`, `target_id`, `kind`, `evidence`, optional `inferred` → `relation_id`, `relation_type`
- `contradict`: `left_event`, `right_event`, `evidence` → `relation_id`, `relation_type`
- `begin_reconsolidation`: `event_id`, `evidence` → `target_id`, `lifecycle_state`
- `resolve_reconsolidation`: `event_id`, `decision`, `evidence` → `target_id`, `lifecycle_state`
- `consolidate`: `event_id`, `evidence` → `target_id`, `lifecycle_state`
- `decay`: `target_id` → `target_id`, `lifecycle_state`
- `retrieve`: `query` → `retrieval_id`, `selected`

Signal payloads must not include mechanism-owned fields such as `lifecycle_state` or `candidate_status`. That rejection is `BoundaryError` `caller cannot set mechanism-owned fields: ...`, not the `SnapshotError` ownership rejection used for `assign_ids` and the other ownership keys above.

## Missing and unknown feedback

Aligned with `docs/PROTOCOLS.md`: a missing signal is unknown, not guessed. `user_feedback`, `task_success`, and `used` stay absent or `None` unless the caller supplied that signal through an explicit future feedback operation. This contract does not add that operation. `observe` and `signal` must not invent `user_feedback` or `task_success`.

Unknown discovery sources stay `unknown` or `unreadable` in inventory. `import_selected` rejects paths that were not recognized in that handle's discovery (`not_in_discovery` or the source status). It does not migrate or rewrite caller files.

## Compatibility

Stable, must not change without a new contract revision and conformance update:

- the eleven `SUPPORTED_OPS` names and the accepted envelope
- the error strings listed above
- caller isolation and mechanism ownership
- `read_graph` read-only projection
- `save` / `load` / `reopen` integrity behavior
- discovery-before-memory on `SkillEntrypoint`

Experimental, may change under a later implementation issue:

- discovery inventory field set beyond `sources`, `inventory`, and `diagnostics`
- import record field set beyond path, status, source digest, and mechanism ids
- explorer HTML (presentation only; not a Skill operation)

Versioning rule until a package exists: additive optional response fields are compatible; removing, renaming, or redefining an operation, error string, or ownership rule is breaking and out of scope here. No semver distribution is published by this contract.

## Non-goals

No new database, storage adapter, Agent/Harness SDK, UI, server, MCP, GraphRAG, vector DB, Hub, or Memory Bridge. No change to frozen V0.1 A/B/C/D/E, Phase G assets/config/results, V0.2 lifecycle/thread/relation semantics, or locked Phase H parameters/results.
