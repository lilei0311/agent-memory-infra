# Stage 10 Skill bootstrap and existing-memory discovery

Stage 10 adds the smallest installation seam. Bootstrap discovers an existing caller memory environment. It does not migrate it.

This stage does not add a transport, agent framework, database, or second owner of mechanism state. It does not change V0.2 transitions or locked Phase H configuration.

## Installation entry point

Public imports:

- `SkillBootstrap`
- `BootstrapSession`
- `discover_environment`
- `RECOGNIZED_NAMES`
- `DEFAULT_SCAN_LIMIT`
- `DEFAULT_MAX_DEPTH`

from `memory_infra.bootstrap`. `memory_infra.skill` re-exports `SkillBootstrap` and `BootstrapSession` so callers do not import `memory_infra.store`.

`SkillBootstrap.open(caller_id)` returns a caller-bound `BootstrapSession`. `session.install(root=..., artifacts=..., scan_limit=..., max_depth=...)` is the installation action and retains the discovery note only on that handle. `SkillBootstrap.install(...)` runs the same scan and does not expose a caller-id lookup. `discover_environment(...)` is the same read-only scan without retaining a note.

## What is detected

The scan is a bounded file-name inventory of a caller-supplied directory and/or an in-memory artifact map. Recognized names are exactly `MEMORY.md`, `memory.md`, `memories.json`, and `memory.json`. Other files are unknown. Missing roots, non-directories, and unreadable files are unreadable. File contents are not parsed into memories.

## Bounded scan

Default limit is 32 entries and depth 2. Paths are sorted. Extra entries set `inventory.truncated` and add a diagnostic. The scan does not follow symlinks as a separate store.

## Result envelope

A successful bootstrap returns:

- `ok: true`
- `op: bootstrap`
- `read_only: true`
- `imported: false`
- `explicit_import: not_invoked`
- `mechanism_memory_created: false`
- `caller_id`
- `sources`: path, kind, status, bytes, detail
- `inventory`: recognized, unknown, unreadable, scanned, truncated, scan_limit, max_depth
- `diagnostics`
- `supported_sources`

## Ownership

Caller memory files stay caller-owned. Discovery notes stay on the bootstrap seam and are bound to the `BootstrapSession` handle returned by `open`. They are not written to `MemoryService`, not restored by save/load, and not mechanism events.

Explicit import is not implemented. A later import would have to be a separate caller-invoked operation. Installation does not call it.

## Failure and partial discovery

A missing or unreadable source does not fail the whole bootstrap. It is recorded as unreadable and discovery continues within the bound. An empty environment returns an empty source list and a diagnostic. `caller_id` is required.

## Isolation

`session.last_inventory()` takes no caller id and returns only the note retained on that handle. `SkillBootstrap.last_inventory(caller_id)` is rejected. A second `open` call, including one that names another caller, cannot read the first handle's note.

## Non-claims

This stage does not claim production installers, authentication, concurrency, or compatibility with external memory products.
