# Agent Memory Skill

Framework-neutral in-process entrypoint. This is not an MCP server, HTTP service, or agent SDK.

## Startup sequence

1. Open a caller-bound bootstrap session with `SkillEntrypoint.open(caller_id)`.
2. Run bounded read-only discovery with `handle.start(root=..., artifacts=...)`.
3. Read the returned inventory and diagnostics. Unknown and unreadable sources do not abort startup.
4. Only after discovery, call `handle.enable_memory()` and then `handle.invoke(...)`.
5. Do not import, rewrite, or migrate existing caller memory. Installation does not ingest files into mechanism state.
6. Historical structuring is a separate call: `handle.import_selected(paths)` after discovery. It imports only selected recognized sources and does not rewrite caller files.
7. `read_graph` is a read-only projection of mechanism-owned objects. It does not create graph state.

The entrypoint uses `SkillBootstrap` and `SkillApi` only. It does not import `memory_infra.store`.

Discovery notes stay on the caller handle from `open`. A second open cannot read another handle's inventory.
